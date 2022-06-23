from django.urls import path

from . import views

urlpatterns = [
    # Leave as empty string for base url
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('alogin/', views.loginp, name="alogin"),
    path('adlocheck/', views.locheck, name="locheck"),
    path('add_product/', views.add_product, name="add_product"),
    path('add_productP/', views.add_productP, name="add_productP"),
    path('logout/', views.logout, name="logout"),
]
