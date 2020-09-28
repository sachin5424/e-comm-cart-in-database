from django import forms
from django_countries.fields import CountryField



class checkoutForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    countries = CountryField(blank_label='select Country').formfield(attrs={'class':' checkout__input w-full h-auto'})
    zip = forms.CharField(max_length=20)
    street_address = forms.CharField(max_length=100)
    apartment_address = forms.CharField(required=False,max_length=100)
    phone_number = forms.CharField()
    email = forms.EmailField()

    
    
