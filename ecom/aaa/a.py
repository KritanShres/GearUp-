from django.db import models
from django.contrib.auth.models import User

#Product models 
class Category(models.Model):
    name = models.CharField(max_length=255)
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE, null= True, blank= True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank = True, null =True )
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True) 
    processor = models.CharField(null= True, blank = True, max_length=50) 
    display_type = models.CharField(null= True, blank = True, max_length=10) 
    ram = models.IntegerField(null= True, blank = True) 
    ssd = models.IntegerField(null = True, blank = True) 
    gpu = models.CharField(null= True, blank = True, max_length=50) 
    os = models.CharField(null=True, blank = True, max_length=50)
    def __str__(self):
        return self.name
    
    @property 
    def imageURL(self): 
        try: 
            url = self.image.url
        except:
            url = ''
        return url
    
class ProductItem(models.Model): 
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null= True, blank = True)
    product_quantity = models.IntegerField()


#Customer models
class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_record = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.transaction_id
    
    @property 
    def get_cart_total(self): 
        orderitems = self.orderitem_set.all()
        total = sum ([item.get_total for item in orderitems])
        return total 
    
    @property
    def get_cart_items(self): 
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total 

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return self.order

    @property
    def get_total(self): 
        total = self.product.price * self.quantity
        return total
    
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address



def store(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}
		cartItems = order['get_cart_items']

	products = Product.objects.all()
	categories = Category.objects.all() 
	context = {'products':products, 'cartItems':cartItems, 'categories':categories}
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
	product = Product.objects.get(id=productId)
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

#Authentication Views
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
	categories = Category.objects.all() 
	items = Product.objects.all()
	

	if category_id: 
		items = items.filter(category_id=category_id) 

	if query: 
		items = items.filter(Q(name__icontains=query)|Q(description__icontains = query))

	return render(request, 'store/items.html', {
		'items': items, 
		'query': query,
		'categories': categories,
		'category_id':int(category_id)
	})

#test views
def test(request): 
	products = Product.objects.all()
	categories = Category.objects.all()
	return render(request, 'store/test.html',{'products':products,'categories':categories})