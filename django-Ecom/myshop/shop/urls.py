from django.urls import path
from shop import views
from django.views.generic import RedirectView
app_name='shop'
urlpatterns = [
    path('', RedirectView.as_view(url="home/")),
    path('home/',views.index,name='Home'),
    path('shop_List/',views.shop_List.as_view(),name='shop_List'),
    path('home/<str:slug>/', views.Home_Detail,name='Home_Detail'),
    path('add_to_cart/<str:slug>/',views.add_to_cart,name='add_to_cart'),
    path('remove_to_cart/<str:slug>/',views.remove_to_cart,name='remove_to_cart'),
    # path('shopping_cart_add_to_cart/<str:slug>',views.shopping_cart_add_to_cart,name='shopping_cart_add_to_cart'),
    path('OrderSummaryView/',views.OrderSummaryView.as_view(),name='OrderSummaryView'),
    path('single_item_remove_to_cart/<str:slug>/', views.single_item_remove_to_cart, name='single_item_remove_to_cart'),
    # path('Order_Summary_item_remove/',views.Order_Summary_item_remove,name='Order_Summary_item_remove'),
    path('New_Account/',views.New_Account,name='New_Account'), 
    path('Profile_Edit/<int:pk>/',views.Profile_Edit.as_view(),name='Profile_Edit'),
    path('checkout/',views.checkout.as_view(),name='checkout'),
    path('Paymet/',views.Paymet.as_view(),name='Paymet'),
    
]
