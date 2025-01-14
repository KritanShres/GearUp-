from django.contrib import admin
from .models import * 

admin.site.register(Category) 
admin.site.register(Brand)
admin.site.register(Laptop) 
admin.site.register(Customer) 
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress) 