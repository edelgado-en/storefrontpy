from django.contrib import admin
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
# This is to generate a alphanumeric string to avoid using 1,2,3,4. We are using this for the id of the cart since we are putting the id in the url.
from uuid import uuid4

from .validators import validate_file_size

# Create your models here.

# This means the product class is inheriting from Model class

# We dont have to create an id as primary key
# because Django creates it automatically unless that you create your own primary key that is different than id

# Many to many relationship with Product. Many products can have many promotions.


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    # related_name='+' tells Django not to create a reverse relationship. There is a name clash with collection in Product class
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']

# in Python by default the fiels are NOT NULL unless you say (null=True)!!! in Java is the opposite


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(default='-')
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    last_udpate = models.DateTimeField(auto_now=True)
    # one to many. A collection can have many products
    # what related_name MEANS IS: every entry in the Collection ENTITY (not table) has a field called products
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='products')
    # Django will automatically create the reverse connection in the Promotion class. I could have add products in Promotion,but I add it here because it makes more sense
    # products_set will be created in Promotion automatically
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images')
    # With this implementation, we are saving images in the file system, and their path in the database. This way our queries will be faster.
    # This path is relative to the media folder. So it will look like media/store/images/
    # In order to use ImageField you have to install Pillow: pipenv install pillow
    # ImageField already checks for file extension under the hood, but if you use FileField, you have add another validator
    # FileExtensionValidator(allowed_extensions=['pdf'])
    image = models.ImageField(upload_to='store/images',
                              validators=[validate_file_size])


class Review(models.Model):
    # IMPORTANT TO UNDERSTAND: related_name will create a field called reviews in the Product class so that you can easily access liek this: product.reviews
    # if you don't specify the related_name, Django will create a field called reviews_set
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    # A text field has no limitations on the length of the text.
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    # we add this decorator to make this column sortable in the admin view
    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    def get_orders(self):
        return self.orders.count()

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    # You can add a class Meta to change the default behavior of the model. You can create indexes, change table names, etc
    # class Meta:
    # Changing the name is not recommended. It is better to use the conventions used by Django
    #db_table = 'store_customers'
    #   indexes = [
    #      models.Index(fields=['first_name', 'last_name'])
    # ]


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]
    # auto_noew_add means that Djando will automatically add the current time and date when the order is created
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_CHOICES, default=PAYMENT_STATUS_PENDING)
    # PROTECT because if we delete a customer, we don't want to delete orders associated with that customer
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='orders')

    # This is creating a CUSTOMER permission entry in the auth_permission table with a name of "can cancel order". cancel_order is a unique identifier
    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel an order'),
        ]


class OrderItem(models.Model):
    # One to many relationship. An order can have many order items. PROTECT because if we delete an order, we don't want to delete order items associated with that order
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    # because we want to store the price of the product when it was ordered. Products can change overtime.
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    # one to many relationship. A customer can have many addresses
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    # Notice how we are NOT calling uuid4(), we just are just refering the function. If you call the function, when you run makemigrations, it will generate a uuid
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    # one to many relationship. A cart can have many cart items
    # related_name='cartitems' means the Cart model will have a field called items, othwerise django use the default: cartitem_set
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    # To create a unique constraint, use the Meta class
    class Meta:
        # we can you can have many constraints, you use a list of list. In this case we just want a unique constraint for cart and product together
        unique_together = [('cart', 'product')]
