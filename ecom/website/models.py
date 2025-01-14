from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Laptop(models.Model):
    category = models.ForeignKey(Category, related_name='laptops', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='laptops', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='laptop_images/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    # Specifications
    processor = models.CharField(max_length=100)
    ram = models.PositiveIntegerField(help_text="RAM in GB")
    storage = models.CharField(max_length=100, help_text="Storage type and size (e.g., 512GB SSD)")
    gpu = models.CharField(max_length=100, blank=True, null=True, help_text="Graphics card (if any)")
    display_size = models.FloatField(help_text="Display size in inches")
    os = models.CharField(max_length=50, help_text="Operating System")
    battery = models.CharField(max_length=100, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kg")

    def __str__(self):
        return f"{self.brand.name} {self.name}"


#Customer Database Model
class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_record = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.transaction_id
    
    @property 
    def get_cart_total(self): 
        orderitems = self.orderitem_set.all()
        total = sum ([item.get_total for item in orderitems])
        return total 
    
    @property
    def get_cart_items(self): 
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total 

class OrderItem(models.Model):
    product = models.ForeignKey(Laptop, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return self.order

    @property
    def get_total(self): 
        total = self.product.price * self.quantity
        return total
    
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
