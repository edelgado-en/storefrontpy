from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .signals import order_created
from .models import Product, Collection, ProductImage, Review, Cart, CartItem, Customer, Order, OrderItem, ProductImage


# This is where you define how you product resource will look like, because just like in Java, the resource
# does not look exactly like the model. So the serializers folder is the equivalent to the resources folder in Java.

# You can go to django-rest-framework.org/api-guide to see all the options


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'price',
                  'price_with_tax', 'collection']

    #id = serializers.IntegerField(read_only=True)
    # The reason you are specifying the max_length here again is because
    # we are going to use this serializer when creating new products and we want to validate the input. Just like lombok annotation with @Valid in Java
    # You use the source paremeter when the name of the field is different from the name of the model field.
    #new_title = serializers.CharField(max_length=255, source='title')
    #price = serializers.DecimalField(max_digits=6, decimal_places=2)

    # we can add new fields that don't exist in the model just like I always do in Java
    price_with_tax = serializers.SerializerMethodField(
        method_name='get_price_with_tax')

    # You can serialize mode relationships also. This uses the string representation of the colleciton object. YOu can override it with __str__
    # To avoid getting n+1 queries in the loop. YOu need to prefect the collections when fetching the products in views.py. Like this:
    # qs = Product.objects.select_related('collection').all(). There are different ways to serialized but, you are gonna use CollectionSerializer
    #collection = serializers.StringRelatedField()

    def get_price_with_tax(self, product: Product):
        return product.price * Decimal(1.1)

    # we are overring the validate method to create a custom validation. The default validaiton uses the model validation
    # This method is called when you use serializer.is_valid(raise_exception=True)
    def validate(self, data):
        if data['price'] < 0:
            raise serializers.ValidationError('Price must be positive')
        return data

    # You can also overrride the create method to create a new product when you need to associate other entities
    # This method is called when the serializer calls save()
    # def create(self, validated_data):
        # the ** UNPACKS the values from provided dictionary. Is kinda like the spread operator.
     #   product = Product(**validated_data)
      #  product.other = 1
       # product.save()
        # return product


"""     def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance """


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    # By adding read_only=True, you are telling the serializer to not allow the client to update/create the products_count field.
    products_count = serializers.IntegerField(read_only=True)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description', 'product']


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']

# We define the CartItemSerializer first because we are going to use it in the CartSerializer


class CartItemSerializer(serializers.ModelSerializer):
    # Because we don't want to simply show the product id, we need to tell django what we want to show
    # instead of using ProductSerializer, we create a different one because we only want to show certain values in the CartItem
    #product = ProductSerializer()
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    # is import to use the naming convention expected by django: get_<field_name> so that the serializerMethodField can use it
    # also cart_item can have any name you want. it refers to the instance model of the current serializer. We annotate with :CartItem to have intellisense
    def get_total_price(self, cart_item: CartItem):
        return cart_item.product.price * cart_item.quantity

    class Meta:
        model = CartItem
        # total_price is a calculated field. It is not a field in the model.
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    # This will prevent from the id field showing when trying to create a new cart. We want to create a cart as an empty object
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])

    class Meta:
        model = Cart
        # we dont' return created_at because it has no use for the user. We only have the value for internal purposes.
        # remember that django adds the items field to the Cart model because I specified related_name='items' in the CartItem model
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    # To VALIDATE DATA pass by the client we can do it at the field level or at the object level
    # Naming convention here is very important: validate_<field_name>
    # You either raise a validation error or return the validated value
    def validate_product_id(self, value):
        try:
            Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Product does not exist')

        return value

    # because we have some custom business logic to save the the cart item (cannot have duplicates products)
    # we cannot rely on the default implementation of the save method in ModelSerializer. We need to override it

    def save(self, **kwargs):
        cart_id = self.context['cart_id']  # this is set in the view
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        # in the serializer we don't have access to url paramters, we need to use a context object in the view and pass it to the serializer
        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            # update existing cart item
            cart_item.quantity += quantity
            self.instance = cart_item.save()

        except CartItem.DoesNotExist:
            # create new cart item
            # ** unpacks the kwargs dictionary into the keyword arguments. SHORTCUT to avoid doing product_id=product_id, quantity=quantity
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    # Because user_id is created dynamically, we still need to specify it in here
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    # Because when we are creating an order we only pass the id, we need a different serializer

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at',
                  'payment_status', 'items']


# Because when we update an order, we only want to update certain fields, we create a new serializer and using it for PATCH requests
# Another solution will be to make the fields read only in the OrderSerializer, but this will make the serializer more complicated
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    # we are not extending ModelSerializer because cart_id doesn't exist in the Order model, so we don't have to use class Meta either
    cart_id = serializers.UUIDField()

    # Remember that to validate a specific field we need to use the validate_<field_name> method
    # We do this because we don't want to create orders if the cart doesn't exist
    def validate_cart_id(self, value):
        try:
            Cart.objects.get(pk=value)
        except Cart.DoesNotExist:
            raise serializers.ValidationError('Cart does not exist')

        if CartItem.objects.filter(cart_id=value).count() == 0:
            raise serializers.ValidationError('Cart is empty')

        return value

    # because our logic to save an order is different than the default one, we need to override the save method
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            print(cart_id)
            # we don't have access to the user because we are in a serializer, we need to set a context object in the view to pass the user id here
            print(self.context['user_id'])

            # remember that get_or_create returns a tuple with the object and a boolean. The boolean is True if the object was created
            # BECAUSE we are using signals now, we don't need to create the customer here
            customer = Customer.objects.get(
                user_id=self.context['user_id'])
            # we only need to pass the customer because the other values are auto-generated or have a default value
            order = Order.objects.create(customer=customer)

            # VERY IMPORTANT that we use select_related('product') to eager load the product field, otherwise django will make a db call per cart item iteration
            cart_items = CartItem.objects.select_related(
                'product').filter(cart_id=cart_id)

            # we use a list comprehension to create a list of OrderItem objects
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.price,
                    quantity=item.quantity
                )
                for item in cart_items
            ]

            # we use bulk_create to create the order items in one query
            OrderItem.objects.bulk_create(order_items)

            # now we need to delete the cart
            Cart.objects.filter(pk=cart_id).delete()

            # we are returning the order object so that we can use it in the view override method create, in order to return to the client
            return order


class ProductImageSerializer(serializers.ModelSerializer):

    # We are overriding the default implementation of the save method because the client is only passing
    # the image file in the request body. We need to get the product id from the url params in order to save it in the database
    def create(self, validated_data):
        product_id = self.context['product_id']
        # IMPORTANT:
        # **validated_data means pass all the fields in the request body to the method
        # Django will append some characters to the file name like dog_tygh6qc.jpg
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        mode = ProductImage
        # We are not including the product here because it is already part of the url: /product/1/images/1
        fields = ['id', 'image']
