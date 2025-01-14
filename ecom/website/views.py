from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

from .models import * 
from .forms import CreateUserForm, CustomAuthenticationForm, SignupForm, LoginForm

# Create your views here.

#database views
def store(request):
	if request.user.is_authenticated:
		if not hasattr(request.user, 'customer'):
			customer = Customer.objects.create(user=request.user)
		else:
			customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total': 0, 'get_cart_items': 0}
		cartItems = order['get_cart_items']

	products = Laptop.objects.all()
	categories = Category.objects.all()
	brands = Brand.objects.all()
	context = {'products': products, 'cartItems': cartItems, 'categories': categories, 'brands': brands}
	
	return render(request, 'store/store.html', context)

def cart(request):
    if request.user.is_authenticated: 
        customer = request.user.customer 
        order, created = Order.objects.get_or_create(customer = customer, complete= False) 
        items = order.orderitem_set.all()
    else: 
        items = [] 
        order = {'get_cart_total' : 0, 'get_cart_items': 0}
    context= {'items' : items, 'order' : order} 
    return render(request, 'store/cart.html', context)

def checkout(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
		cartItems = order['get_cart_items']
	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Laptop.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if not request.user.is_authenticated and action == "add": 
		print('redirecting')
		return redirect('login-signup')

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False) 

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		total = float(data['form']['total'])
		order.transaction_id = transaction_id

		if total == order.get_cart_total:
			order.complete = True
		order.save()

		if order.shipping == True:
			ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
			)
	else:
		print('User is not logged in')

	return JsonResponse('Payment submitted..', safe=False)

#Authentication Views
def signup_login_view(request):
    if request.method == "POST":
        signup_form = CreateUserForm()
        login_form = CustomAuthenticationForm()

        if "signup" in request.POST:
            signup_form = CreateUserForm(request.POST) 
            if signup_form.is_valid():
                signup_form.save()
                messages.success(request, "Account was created successfully.")
                return redirect('store')  

        elif "login" in request.POST:
            login_form = CustomAuthenticationForm(data=request.POST)
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password) 

            if user is not None:
                login(request, user) 
                return redirect('store') 
            else:
                messages.error(request, "Invalid username or password.")

    else:
        signup_form = CreateUserForm() 
        login_form = CustomAuthenticationForm()

    return render(request, 'store/login-register.html', {
        'signup_form': signup_form,
        'login_form': login_form,
    })

def signup(request): 
	if request.method== 'POST': 
		form = UserCreationForm(request.POST)
		if form.is_valid(): 
			form.save() 
			return redirect('store')
	else: 
		form =UserCreationForm
	context = {'form':form}
	return render(request, 'store/register.html', context)

def logout_page(request):
    logout(request)
    return redirect('store')

#category_views
def items(request): 
	query = request.GET.get('query','')
	category_id = request.GET.get('category',0)
	brand_id = request.GET.get('brand', 0)
	categories = Category.objects.all() 
	items = Laptop.objects.all()
	brands = Brand.objects.all()

	if category_id: 
		items = items.filter(category_id=category_id) 
	if brand_id: 
		items = items.filter(brand_id = brand_id)
	if query: 
		items = items.filter(Q(name__icontains=query)|Q(description__icontains = query))
		brands = brands.filter(Q(name__icontains = query)|Q(description__icontains = query))

	return render(request, 'store/items.html', {'items': items, 'query': query, 'categories': categories,'category_id':int(category_id),'brands': brands,})

def detail(request,pk): 
	detail = Laptop.objects.get(pk=pk)
	related_item = Laptop.objects.filter(category = detail.category).exclude(pk=pk)[0:3]
	context ={'detail':detail, 'related_items': related_item} 
	return render(request, 'store/detail.html', context)



#test views
def test(request): 
	products = Laptop.objects.all()
	categories = Category.objects.all()
	return render(request, 'store/test.html',{'products':products,'categories':categories})	