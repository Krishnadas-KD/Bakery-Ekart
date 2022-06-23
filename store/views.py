from django.shortcuts import redirect, render
from django.http import JsonResponse
import json
import datetime
from .models import *
from math import ceil

from . utils import cookieCart, cartData, guestOrder

from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def store(request):

  data = cartData(request)
  cartItems = data['cartItems']
  order = data['order']
  items = data['items']

  allProds = []
  catprods = Product.objects.values('category', 'id')
  cats = {item['category'] for item in catprods}
  for cat in cats:
    prod = Product.objects.filter(category=cat)
    n = len(prod)
    nSlides = n // 6 + ceil((n / 6) - (n // 6))
    allProds.append([prod, range(1, nSlides), nSlides])

  context = {'allProds': allProds, 'cartItems': cartItems}
  return render(request, 'store/store.html', context)


def cart(request):

  data = cartData(request)
  cartItems = data['cartItems']
  order = data['order']
  items = data['items']

  context = {'items': items, 'order': order, 'cartItems': cartItems}
  return render(request, 'store/cart.html', context)


def checkout(request):

  data = cartData(request)
  cartItems = data['cartItems']
  order = data['order']
  items = data['items']

  context = {'items': items, 'order': order, 'cartItems': cartItems}
  return render(request, 'store/checkout.html', context)



#ad login
def loginp(request):
  print('login')
  return render(request, 'adminp/Login.html')

def locheck(request):
  if 'email' in request.session:
    product=Product.objects.all()
    ship=ShippingAddress.objects.all()
    order=Order.objects.all()
    orderitem=OrderItem.objects.all()


    return render(request, 'adminp/index.html',{'product':product,'sales':ship,'order':order,'orderitem':orderitem})
  if request.POST:
    username = request.POST.get('username')
    password = request.POST.get('password')
    if adlog.objects.get(username=username).password == password:
      request.session['email'] = username
      product=Product.objects.all()
      sales=ShippingAddress.objects.all()
      order=Order.objects.all()
      orderitem=OrderItem.objects.all()
    
      print(sales)
      return render(request, 'adminp/index.html')
    else:
      msg='Invalid username or password'
      return render(request, 'adminp/login.html',msg=msg)

#add product
def add_productP(request):
  return render(request, 'adminp/addproducts.html')

def add_product(request):
  if request.method == 'POST':
    name=request.POST.get('name')
    category=request.POST.get('category')
    subcategory=request.POST.get('subcategory')
    price=request.POST.get('price')
    description=request.POST.get('description')
    image=request.FILES.get('image')
    form = Product(product_name=name,category=category,subcategory=subcategory,price=price,desc=description,image=image, pub_date=datetime.datetime.now())
    form.save()
    return redirect('/adlocheck/')


def logout(request):
  request.session.flush()
  return redirect('/')

def updateItem(request):
  data = json.loads(request.body)
  productId = data['productId']
  action = data['action']
  print('Action:', action)
  print('Product:', productId)

  customer = request.user.customer
  product = Product.objects.get(id=productId)
  order, created = Order.objects.get_or_create(
      customer=customer, complete=False)

  orderItem, created = OrderItem.objects.get_or_create(
      order=order, product=product)

  if action == 'add':
    orderItem.quantity = (orderItem.quantity + 1)
  elif action == 'remove':
    orderItem.quantity = (orderItem.quantity - 1)

  orderItem.save()

  if orderItem.quantity <= 0:
    orderItem.delete()

  return JsonResponse("Item was added", safe=False)


@csrf_exempt
def processOrder(request):
  transaction_id = datetime.datetime.now().timestamp()
  data = json.loads(request.body)

  if request.user.is_authenticated:
    customer = request.user.customer
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
  else:
    customer, order = guestOrder(request, data)

  total = float(data['form']['total'])
  order.transaction_id = transaction_id

  if total == order.get_cart_total:
    order.complete = True
  order.save()

  ShippingAddress.objects.create(
      customer=customer,
      order=order,
      address=data['shipping']['address'],
      city=data['shipping']['city'],
      state=data['shipping']['state'],
      zipcode=data['shipping']['zipcode']
  )

  return JsonResponse('Payment submitted..', safe=False)
