from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

# this is used to create your own custom viewset
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.views import APIView

from .permissions import IsAdminOrReadOnly
from .models import Product, Collection, Review, Cart, CartItem, Customer, Order, ProductImage
from .serializers import CollectionSerializer, OrderSerializer, ProductSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer, ProductImageSerializer
from .filters import ProductFilter
from .pagination import DefaultPagination

# Create your views here.

# a view function is a function that takes a request and returns a response

# When you you this decorator, it converts the django request object to a rest framework request object.


class ProductView(ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    # if you don't have business logic to create queryset like depending on the use role, you can just use the field:
    #queryset = Product.objects.select_related('collection').all()
    #serializer_class = ProductSerializer

    # OrderingFilter allows me to SORT. I just need to specify the field name and the direction.
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # This allows you to search by field. BUt this only works with exact match. You need to create a custom filter.
    #filterset_fields = ['title']
    # YOU CAN ONLY IMPORT SEARCHFILTER which similar to ProductFilter
    filterset_class = ProductFilter
    # If you want pagination in ALL your views, you can remove this line and configure the pagination in the settings.py file.
    # IN the DefaultPagination is where you configure page size and the number of pages to be displayed.
    pagination_class = DefaultPagination
    ordering_fields = ['price', 'last_update']

    # override the get_queryset method to return a queryset of all products
    def get_queryset(self):
        return Product.objects.select_related('collection').all()

    # override the get_serializer_class method to return a serializer class
    # You use this method when you have business logic that needs to be executed before the serializer is created.
    # for example ,you return different serializers depending on the user role
    def get_serializer_class(self):
        return ProductSerializer

    # override the create method to return a response
    def get_serializer_context(self):
        return {'request': self.request}

# This way of creating a class inheriting APIView is way easier to understand than using generic views
# class ProductView(APIView):
 #   def get(self, request):
  #      qs = Product.objects.select_related('collection').all()
        # many=True tells the serializer that it needs to iterate over the queryset and serialize each item
   #     serializer = ProductSerializer(
    #        qs, many=True, context={'request': request})
     #   return Response(serializer.data)

    # def post(self, request):
     #   serializer = ProductSerializer(data=request.data)
      #  serializer.is_valid(raise_exception=True)
        # the reason you can save to the database using the serializer is because you are extending from ModelSerializer
        # There are other ways to save to the database
       # serializer.save()
        # return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # We don't need to override this method because we are using the default implementation
    """ def get(self, request, id):
        product = get_object_or_404(Product, id=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data) """

    # we don't need to override this method because we don't have any special business logic
    """ def put(self, request, id):
        product = get_object_or_404(Product, id=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data) """

    # we are overriding this method because we have custom validation logic product.orderitems.count() > 0
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        # notice how you don't need a repository class or even the objects interface to execute saves aor deletes. You can call them directly from the model object
        # Remember that you cannot delete an entry that has dependencies with other entities. You have delete those first
        # orderitems is the name specified in related_name in the OrderItem model. If you don't specifiy related_name, django will use orderitem_set
        if product.orderitems.count() > 0:
            return Response({'error': 'A product cannot be deleted because it is associated with an order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# This is a generic view that can be used to create a list of objects or retrieve a list of objects

# This is where you see the power of viewset. Do you see how you are repeating serializer, queryset and permissions in CollectionDetail


class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]


""" @api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        qs = Collection.objects.annotate(
            products_count=Count('products')).all()
        serializer = CollectionSerializer(qs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED) """


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if (collection.products.count() > 0):
            return Response({'error': 'A collection cannot be deleted because it is associated with a product'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


""" @api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection.objects.annotate(
        products_count=Count('products')), pk=pk)

    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if collection.products.count() > 0:
            return Response({'error': 'A collection cannot be deleted because it is associated with a product'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) """

# ModelViewSet is a generic view that can be used to create a list of objects or retrieve a list of objects
# it's an abstraction on top of ListCreateAPIView and RetrieveUpdateDestroyAPIView


class ReviewViewSet(viewsets.ModelViewSet):
    # Since we need access to the product id in the url, we need to override the get_queryset method
    #queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['pk'])


# we DO NOT inherit from ModelViewSet because that class provides list, retrieve, update, and destroy methods,
# and for Cart we don't have a list (GET request). We only support create, getting a cart, and deleting a cart
# BECAUSE I ADDED THE RETRIEVEMODELMIXIN I AM NOW ABLE TO FETCH CARTS BY ID!!!!
class CartViewSet(CreateModelMixin,  # just by adding this mixing, I can create a cart. LOTS OF DJANGO MAGIC
                  RetrieveModelMixin,  # just by adding this mixin, I can fetch by uuid
                  DestroyModelMixin,  # just by adding this mixin, now I can delete carts
                  viewsets.GenericViewSet):
    # prefetch_related is EXTREMELY IMPORTANT to avoid running multiple queries behind the scenes
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    # you can specify which http methods are allowed for this viewset
    # we are excluding PUT request because we only update one field (quantity), not the whole object
    # These methods here HAVE TO BE IN LOWERCASE. More django magic
    http_method_names = ['get', 'post', 'patch', 'delete']

    """
    I inhertit from ModelViewSet because I support all operations for cartItem (list, create, update, delete)
    """
    # we don't want to hardcode CartItemSerializer, we want to dynamically create depending on the request METHOD
    #serializer_class = CartItemSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            # WE DON'T ALLOW PUT REQUEST BECAUSE WE ONLY UPDATE A SINGLE PROPERTY (quantity)
            return UpdateCartItemSerializer
        return CartItemSerializer

    # we do this so that we can have access to the cart id in the serializer
    # we are reading cart_pk from the url
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        # the cart_pk name is specified in the urls.py lookup_field cart
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # select_related('product') IS IS EXTREMELY IMPORTANT TO AVOID RUNNING N+1 DATABASE QUERIES
        # without this what django does is one query to get the cartitems, and one query per cartitem to get the product which is TERRIBLE
        return CartItem.objects \
            .filter(cart_id=self.kwargs['cart_pk']) \
            .select_related('product')

# We DO NOT want to inherit from ModelViewSet because there are some operations we don't want to support, like deleting a customer
# so I need to create a custom viewset by adding different mixins
# Notice how GET reuest is NOT allowed (we don't want the client to get a list of clients). If we wanted to support the GET LIST
# we would have to inherit from ListModelMixin

# Because you are extending ModelViewSet, you can do all operations. However, we are going to restrict access based on user


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # What we are doing here is: Only admins can access this viewset. However, we override the me function to allow authenticated users (non-admins)
    permission_classes = [IsAdminUser]

    # If you want to specify permisions base on request method, you need to override get_permissions
    # Notice how in here we return actual objects, not classes
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    # This function creates an endpoint with the same name: /store/customers/me
    def me(self, request):
        # use get_or_create to handle the case where the customer doesn't exists
        # get_or_create returns a tuple with the customer object and a boolean indicating if the object was created
        # we are unpacking the tuple
        # Because we are using signals, we need to don't need to use get_or_create method anymore
        customer = Customer.objects.get(
            user_id=request.user.id)

        if request.method == 'GET':
            # We can access the user from the request because the authentication middleware found the JWT in the request, fetch the user from the db and attached it to the request
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    # if you want to specify which http methods are allowed for this viewset
    # Notice how for this particular method, you have to use lowercase
    http_method_names = ['post', 'get', 'patch', 'delete', 'head', 'options']

    # because we are using more than one serializer, we don't hardcode here. we instead override the get_serializer_class method
    #serializer_class = OrderSerializer
    # Because we have custom logic for authentication, we need to override the get_permissions method
    #permission_classes = [IsAuthenticated]

    # PUT http method should only be used when you are replacing all fields of an existing object
    # If you are only replacing some fields, you should use PATCH
    # In Motionpoint, we just send the whole object for simplicity and we use POST. Check to see how they do it at FORD
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    # we override the create method because we want to return a different serializer on creation. Otherwise, we could just use
    # the default implementation in ModelViewSet
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            # This way when we patch we only allow certain fields to be updated. In Motionpoint, we simply pass the whole object
            # and use a POST. Check how they use it at FORD
            return UpdateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        # so that we can use the user_id in the serializer
        return {'user_id': self.request.user.id}

    def get_queryset(self):
        # Remember that the authentication middleware adds the user to the request object. The user is obtained from the jwt token
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        # The get method expects one record in the database. If we get no record or multiple records, it will throw an exception
        # this is just like JPA's findOne()
        # So instead we are going to use get_or_create. This returns a tuple with the order object and a boolean indicating if the object was created
        # However, we are violating an important principle in programming: Command Query Separation.
        # this queryset should not be creating an order in the database. We will find a better way later on.

        # Because we are using signals now, we don't need to create a customer here
        # (customer_id, created) = Customer.objects.only(
         #   'id').get_or_create(user_id=user.id)

        customer_id = Customer.objects.only('id').get(user_id=user.id)

        return Order.objects.filter(customer_id=customer_id)


class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    # We only want to return the images for a particular product so we need to override the get_queryset method

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
        # In order to get the id from the url, we need to use the kwargs dictionary
        # by default django follows the following naming convention: /products/1/images/1 will become
        # /products/1(product_pk)/images/1(pk)
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
