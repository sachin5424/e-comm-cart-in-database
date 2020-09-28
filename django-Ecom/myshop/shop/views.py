from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.checks import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
from .models import Profile,CATEGORY,Item,OrderItem,Order,BillingAddress,Payment
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import Profile
from django.views.generic.edit import UpdateView, ModelFormMixin
from django.views.generic.list import ListView
from django.views.generic import View
from .forms import checkoutForm
from django.conf import settings
import stripe
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token


def index(request):
    item = Item.objects.all()
    return render(request, 'shop/index.html',{'items':item})


class checkout(View):
    def get(self,*args,**kwargs):
        form=checkoutForm()
        context ={
            'form':form
        }
        return render(self.request,'shop/checkout.html',context)

    def post(self,*args, **kwargs):
        form=checkoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
               first_name = form.cleaned_data.get('first_name')
               last_name =  form.cleaned_data.get('last_name')
               countries =  form.cleaned_data.get('countries')
               zip =  form.cleaned_data.get('zip')
               street_address = form.cleaned_data.get('street_address')
               apartment_address =  form.cleaned_data.get('apartment_address')
               phone_number =  form.cleaned_data.get('phone_number')
               email =  form.cleaned_data.get('email')
               billing_address = BillingAddress( user=self.request.user,first_name=first_name,last_name=last_name,countries=countries,zip=zip,street_address=street_address,apartment_address=apartment_address,phone_number=phone_number,email=email)
               billing_address.save()
               order.billing_address=billing_address
               order.save()
            return redirect('shop:Paymet')
        except ObjectDoesNotExist:
            return redirect('shop:OrderSummaryView')
class Paymet(View):
    def get(self,*args, **kwargs):
        return render(self.request,'shop/payment.html')

    def post(self,*args, **kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False)
        token = self.request.POST.get('stripeToken')
        amount= int(order.get_total()*100),
        try:
            # Use Stripe's library to make requests...
            charge=stripe.Charge.create(
            amount=int(order.get_total()*100),

            currency="usd",
            source=token,
            
            )
            payment=Payment()
            payment.user=self.request.user
            payment.strip_charge_id=charge['id']
            payment.amout=order.get_total()
            payment.save()
            # order
            order.ordered=True
            order.payment=payment
            order.save()
            messages.success(self.request,'your order successfull')
            return redirect('/')
            
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body =e.json_body
            err = body.get('error',{})
            messages.error(self.request, f"{err.get('message')}")
        
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, 'requests made to the API ')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request,'Invalid parameters')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request,'Authentication')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, 'Network')
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request,'generic error')
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request,'generic error')
        return redirect('/')
 
        

class shop_List(ListView):
    paginate_by = 10
    model = Item
    template_name = 'shop/shop-grid.html'

    # return render(request,'shop/shop-grid.html',{'ok':ok})


def Home_Detail(request,slug):
    pks = get_object_or_404(Item,slug=slug)
    parm ={
      'object':pks
    }
    return render(request,'shop/shop-details.html',parm)

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.add_message(request, messages.INFO, '"This item quantity was updated."')
            return redirect("shop:Home_Detail",slug=slug)
        else:
            order.items.add(order_item)
            messages.add_message(request,messages.INFO,"This item was added to your cart.")
            return redirect("shop:Home_Detail",slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
        user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.add_message(request,messages.INFO, "This item was added to your cart.")
        return redirect("shop:Home_Detail" ,slug=slug)



@login_required
def remove_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item =OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]
            order.items.remove(order_item)
            messages.add_message(request, messages.INFO, "This item was remove to your cart.")
        else:

            return redirect('shop:Home_Detail', slug=slug)

    else:
        return redirect('shop:Home_Detail',slug=slug)

    return redirect('shop:Home_Detail',slug=slug)

@login_required
def single_item_remove_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item =OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
        else:
            return redirect('shop:OrderSummaryView')
    else:
        return redirect('shop:OrderSummaryView')

    return redirect('shop:OrderSummaryView')


def New_Account(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        username = request.POST.get('Username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user = User.objects.create_user(username, email, password1)
        user.first_name = fname
        user.last_name = lname
        user.save()
        return redirect('shop:Home')
    else:
        return render(request, 'registration/registration_form.html')


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            parm = {
                'object': order
            }
            return render(self.request, 'shop/shoping-cart.html', parm)
        except ObjectDoesNotExist:
            return redirect('/')

@method_decorator(login_required, name="dispatch")
class Profile_Edit(UpdateView):
    model = Profile
    fields = ["image", "address", "phone_no"]
    def get(self, request, *args, **kwargs):
        return Profile.user.id
    template_name = 'registration/profile.html'
