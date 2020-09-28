from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django_countries.fields import CountryField
# Create your models here.

class CATEGORY(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name


class Item(models.Model):
    title = models.CharField(max_length=70)
    slug = models.SlugField(max_length=70)
    category = models.ForeignKey(CATEGORY,on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField()
    price = models.FloatField()
    Weight = models.FloatField()
    Availabil = models.BooleanField(default=False)
    def __str__(self):
        return '%s(%s)'%(self.title ,self.category.name)

    def get_absolute_url(self):
        return reverse('shop:Home_Detail', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('shop:add_to_cart', kwargs={'slug': self.slug})

    def get_remove_to_cart(self):
        return reverse('shop:remove_to_cart', kwargs={'slug': self.slug})




class OrderItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return '%s(%s)'%(self.user.username ,self.quantity)

    def get_total_price(self):
        return self.quantity * self.item.price
    def get_f_price(self):
        return self.get_total_price()

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress',on_delete=models.SET_NULL,blank=True,null=True)
    payment = models.ForeignKey('Payment',on_delete=models.SET_NULL,blank=True,null=True)
    def __str__(self):
        return '%s(%s)'%(self.user.username ,self.ordered_date)


    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_f_price()
        return total


# profile

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/profile/')
    address = models.CharField(max_length=200)
    phone_no = models.CharField(validators=[RegexValidator("^0?[5-9]{1}\d{9}$")], max_length=15, null=True, blank=True)
    def __str__(self):
        return self.user.username





@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Billing
class BillingAddress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    countries = CountryField(multiple=False)
    zip = models.CharField(max_length=20)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    strip_charge_id  = models.CharField(max_length=50)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amout = models.FloatField()
    timestap = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username
     