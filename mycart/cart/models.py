import uuid
from django.db import models
from store.models import Product
from django.contrib.auth.models import User


# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True, null=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.cart_id:
            self.cart_id = str(uuid.uuid4())  # Generate a unique cart_id using UUID
        super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return self.cart_id
    

class Cart_item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField(default=1)  # Ensure default value
    is_active=models.BooleanField(default=True)
    
    def sub_total(self):
       return self.product.price*self.quantity
    
    def __str__(self):
        return self.product.product_name
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.order_items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_cost(self):
        return self.price * self.quantity
