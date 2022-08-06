from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection
from django.db.models import Q, F
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, OrderItem, Order, Customer, Collection
from tags.models import TaggedItem
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
import requests
import logging

# this converts to playground.views. This is better than hardcoding the name because if we ever change the name of the file, this will break
logger = logging.getLogger(__name__)


# Create your views here.


class HelloView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            logger.info('calling httpbin')
            response = requests.get('https://httpbin.org/delay/2')
            logger.info('received the response')
            data = response.json()

        except requests.ConnectionError:
            logger.critical('httpbin is offline')

        return render(request, 'hello.html', {'name': 'Mosh'})


def say_hello2(request):
    requests.get('https://httpbin.org/delay/2')

    return render(request, 'hello.html', {'name': 'Mosh'})


def say_hello(request):
    # Every model in django has an attribute called objects and it returns a manager object.
    # A manager is an interface to the database

    # a query_set object encapsulates a query
    # This doesn't actually makes a call to the database just yet. We can add filters and order by and we evaluate LATER.
    query_set = Product.objects.all().order_by('title')

    # When you INTERACT with the query_set object, that is when django executes(evaluates) the query. This is why query_set is LAZY.
    # for product in query_set:
    # print(product.title)

    try:
        # objects.get returns an actual object, not a queryset because you are not doing extra processing after getting just one item. (pk=1) means primary key = 1
        # There are other ways for you to get an object. objects.filter(pk=1).first() <-- this does not throw an exception for example.
        product = Product.objects.get(pk=1)
    except ObjectDoesNotExist:
        pass
        # return HttpResponse('Product does not exist')

    # keyword value __ greater than. You can find all possible values in https://docs.djangoproject.com/en/4.0/ref/models/querysets/
    querySet = Product.objects.filter(price__gt=20).order_by(
        '-title')  # the minus is in descending order

    # the "i" stands for insensitive, otherwise the contains is case sensitive. The double underscore is what allows to use query set api get, contains, startswith, etc.
    #querySet = Product.objects.filter(title__icontains='coffee')

    # Gets all the products with description null
    #querySet = Product.objects.filter(description__isnull=True)

    # Customers with .com accounts
    #querySet = Customer.objects.filter(email__icontains='.com')

    # Collections that don't have a featured product
    #querySet = Collection.objects.filter(featured_product__isnull=True)

    # Products with low inventory
    #querySet = Product.objects.filter(inventory__lt=10)

    # Orders placed by customer with id = 1
    #querySet = Orders.objects.filter(customer__id=1)

    # Order items for products in collection 3. PERFECT EXAMPLE OF JOINS. This is the equivalent of doing 2 joins
    #querySet = OrderItem.objects.filter(product__collection__id=3)

    # MORE COMPLEX QUERIES. THE comma gets converted to AND
    #qs = Product.objects.filter(inventory__lt=10, price__lt=20)

    # OR YOU CAN WRITE IT LIKE THIS. THIS gets converted to AND
    #qs = Product.objects.filter(inventory__lt=10).filter(price__lt=20)

    # IF YOU WANT TO USE OR OPERATOR, YOU CAN USE Q OBJECT. the curly line converts to NOT in sql
    #qs = Product.objects.filter(Q(inventory__lt=10) | ~Q(price__lt=20))

    # You can also use F objects to reference fields

    # If you just want to get certain columns, you can use the values method.
    # Product.objects.values('id', 'title', 'collection__title')

    qs = Product.objects.filter(
        id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

    # DO NOT USE THE "ONLY" METHOD. JUST USE THE VALUES METHOD. THE "ONLY" METHOD WILL MAKE EXTRA DATABASE CALLS FOR LOOP ITERATION.

    # result is a dictionary 'count': 1000
    result = Product.objects.aggregate(count=Count('id'))

    # print(Order.objects.aggregate(Count('id')))

    # print(OrderItem.objects.filter(product__id=1).aggregate(
    #   sold=Sum('quantity')))

    print(Product.objects.filter(collection_id=3).aggregate(
        min=Min('price'), max=Max('price'), avg=Avg('price')))

    print(Customer.objects.annotate(last_order_id=Max('orders__id')))

    print(Collection.objects.annotate(products_count=Count('product')))

    print(Customer.objects.annotate(
        orders_count=Count('order')).filter(orders_count__gt=5))

    print(Customer.objects.annotate(total_ammount_spent=Sum(
        F('order__orderitem__unit_price') * F('order__orderitem__quantity'))))

    # GOOD EXAMPLE: Top 5 best-selling products and theit total sales
    print(Product.objects.annotate(total_sales=Sum(
        F('orderitem__unit_price') * F('orderitem__quantity')
    )).order_by('-total_sales')[:5])

    # REMEMBER that the objects object returns a DEFAULT manager that is an interface to the database. You can create CUSTOM MANAGERS.

    content_type = ContentType.objects.get_for_model(Product)

    # IMPORTANT: select_related allows to PRELOAD a related object(via foreign key) to avoid doing a lot of queries inside a loop
    # You can use \ to format your query to make it easier to read
    TaggedItem.objects \
        .select_related('tag') \
        .filter(
            content_type=content_type,
            object_id=1
        )

    # HOW TO CREATE AN OBJECT
    # Django ORM is different than Hibernate. You have to fetch the object from the db to update values without reset other fields
    collection = Collection.objects.get(pk=11)
    # collection = Collection()  # there is no new keyword
    collection.title = 'New Collection'
    # this product has to exists BEFORE you save the collection. Just like in Java
    # to set it to null, we use
    collection.featured_product = Product(pk=1)

    # Because there is no id provided, django will treat this as an insert instead of update. Just like in Java
    collection.save()

    # to delete a single object. You first fetch it from the db and then you call delete()
    # collection.delete()

    # to delete a group of objects
    # Collection.objects.filter(id__gt=5).delete()

    # HOW TO CREATE A TRANSACTION
    with transaction.atomic():
        order = Order()
        order.customer = Customer.objects.get(pk=1)
        order.save()

        item = OrderItem()
        item.order = order
        item.product = Product.objects.get(pk=1)

    # HOW TO WRITE RAW SQL WHEN YOU HAVE COMPLEX QUERIES
    queryset = Product.objects.raw('SELECT id, title from store.product')

    # BUT IF YOU WANT TO RETURN A MODEL THAT DOESN'T EXIST IN THE DATABASE, JUST LIKE WHAT YOU DID IN TMV2
    with connection.cursor() as cursor:
        cursor.execute('SELECT id, title from store.product')
        row = cursor.fetchone()
        product = Product(id=row[0], title=row[1])
        return product

    return render(request, 'hello.html', {'name': 'Enrique', 'products': list(querySet)})
    # return HttpResponse("Hello World!")
