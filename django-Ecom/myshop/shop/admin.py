from django.contrib import admin

from .models import Profile,CATEGORY,Item,OrderItem,Order,BillingAddress,Payment
# Register your models here.
class ItemAdmin(admin.ModelAdmin):
    fields = ['title', 'slug','category','description','image','price','Weight','Availabil',]
    prepopulated_fields = {'slug':['title']}
    

class PaymentAdmin(admin.ModelAdmin):
    fields = ['strip_charge_id', 'user','amout','timestap']
    readonly_fields = ['strip_charge_id', 'user','amout','timestap']



admin.site.register(Item,ItemAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CATEGORY)
admin.site.register(Profile)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(BillingAddress)
