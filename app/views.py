from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.urls import reverse


def ProductView(request):
        totalitem = 0
        topwears = Product.objects.filter(category='Top Wear')
        bottomwears = Product.objects.filter(category='Bottom Wear')
        mobile = Product.objects.filter(category='Mobile')
        laptop = Product.objects.filter(category='Laptop')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html',
        {'topwears': topwears, 'bottomwears': bottomwears, 'mobile': mobile, 'laptop': laptop, 'totalitem':totalitem})

class ProductDetailView(View):
    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html', {'product': product,'item_already_in_cart': item_already_in_cart, 'totalitem':totalitem})

@login_required
def buy_now(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
      totalitem = len(Cart.objects.filter(user=request.user))
      user = request.user
      cart = Cart.objects.filter(user=user)
      print(cart)
      amount = 0.0
      shipping_amount = 70.0
      total_amount = 0.0
      cart_product = [p for p in Cart.objects.all() if p.user == user]
      if cart_product:

          for p in cart_product:
              tempamount = (p.quantity * p.product.discounted_price)
              amount += tempamount
              totalamount = amount + shipping_amount
          return render(request, 'app/addtocart.html', {'carts':cart, 'totalamount':totalamount, 'amount':amount})
      else:
         return render(request, 'app/emptycart.html')

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
           tempamount = (p.quantity * p.product.discounted_price)
           amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
         }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
           tempamount = (p.quantity * p.product.discounted_price)
           amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
         }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
           tempamount = (p.quantity * p.product.discounted_price)
           amount += tempamount

        data = {
            'amount':amount,
            'totalamount':amount + shipping_amount
         }
        return JsonResponse(data)



@method_decorator(login_required, name='dispatch')
class ProfileView(View):
   def get(self, request):
    form = CustomerProfileForm()
    return render(request, 'app/profile.html',{'form':form,
     'active':'btn-primary'})

   def post(self,request):
    form = CustomerProfileForm(request.POST)
    if form.is_valid():
        user = request.user
        name = form.cleaned_data['name']
        locality = form.cleaned_data['locality']
        city = form.cleaned_data['city']
        state = form.cleaned_data['state']
        zipcode = form.cleaned_data['zipcode']
        reg = Customer(user=user, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
        reg.save()
        messages.success(request, 'Profile Update Successfully...')
    return render(request, 'app/profile.html', {'form':form,'active':'btn_primary'})


@login_required
def address(request):
    totalitem = 0
    add = Customer.objects.filter(user=request.user)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/address.html', {'add':add,
    'active':'btn-primary', 'totalitem':totalitem})

def search(request):
    data = request.GET.get('search')
    if data:
        get_product = Product.objects.filter(Q(category__contains=data) | Q(title__contains=data) | Q(description__contains=data) |
                                             Q(brand__contains=data))
        return render(request, 'app/search.html',{'data': get_product})
    else:
        return redirect(reverse('home'))

@login_required
def orders(request):
    totalitem = 0
    op = OrderPlaced.objects.filter(user=request.user)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/orders.html', {'order_placed':op, 'totalitem':totalitem})

def mobile(request,data=None):

    if data == None:
        mobiles = Product.objects.filter(category='Mobile')
        return render(request,'app/mobile.html',{'mobiles':mobiles})
    elif data == 'Apple' or data == 'Samsung' or data == 'Oneplus':
        mobiles = Product.objects.filter(category='Mobile').filter(brand=data)
        return render(request, 'app/mobile.html', {'mobiles': mobiles})
    elif data == 'below':
        mobiles = Product.objects.filter(category='Mobile').filter(discounted_price__lt=20000)
        return render(request, 'app/mobile.html', {'mobiles': mobiles})
    elif data == 'above':
        mobiles = Product.objects.filter(category='Mobile').filter(discounted_price__gt=20000)
        return render(request, 'app/mobile.html',{'mobiles':mobiles})


def laptop(request,data=None):

    if data == None:
        laptops = Product.objects.filter(category='Laptop')
        return render(request,'app/laptop.html',{'laptops':laptops})
    elif data == 'Apple' or data == 'Asus' or data == 'Dell':
        laptops = Product.objects.filter(category='Laptop').filter(brand=data)
        return render(request, 'app/laptop.html', {'laptops': laptops})
    elif data == 'below':
        laptops = Product.objects.filter(category='Laptop').filter(discounted_price__lt=50000)
        return render(request, 'app/laptop.html', {'laptops': laptops})
    elif data == 'above':
        laptops = Product.objects.filter(category='Laptop').filter(discounted_price__gt=50000)
        return render(request, 'app/laptop.html',{'laptops':laptops})

def topwear(request,data=None):

    if data == None:
        topwears = Product.objects.filter(category='Top Wear')
        return render(request,'app/topwear.html',{'topwears':topwears})
    elif data == 'Adidas' or data == 'levis' or data == 'zara':
        topwears = Product.objects.filter(category='Top Wear').filter(brand=data)
        return render(request, 'app/topwear.html', {'topwears': topwears})
    elif data == 'below':
        topwears = Product.objects.filter(category='Top Wear').filter(discounted_price__lt=399)
        return render(request, 'app/topwear.html', {'topwears': topwears})
    elif data == 'above':
        topwears = Product.objects.filter(category='Top Wear').filter(discounted_price__gt=399)
        return render(request, 'app/topwear.html',{'topwears':topwears})

def bottomwear(request,data=None):

    if data == None:
        bottomwears = Product.objects.filter(category='Bottom Wear')
        return render(request,'app/bottomwear.html',{'bottomwears':bottomwears})
    elif data == 'puma' or data == 'levis' or data == 'zara':
        bottomwears = Product.objects.filter(category='Bottom Wear').filter(brand=data)
        return render(request, 'app/bottomwear.html', {'bottomwears': bottomwears})
    elif data == 'below':
        bottomwears = Product.objects.filter(category='Bottom Wear').filter(discounted_price__lt=399)
        return render(request, 'app/bottomwear.html', {'bottomwears': bottomwears})
    elif data == 'above':
        bottomwears = Product.objects.filter(category='Bottom Wear').filter(discounted_price__gt=399)
        return render(request, 'app/bottomwear.html',{'bottomwears':bottomwears})


class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',{'form':form})
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Registration successfully!!')
            form.save()
        return render(request, 'app/customerregistration.html',{'form':form})

@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0
    shipping_amount = 70
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    print(cart_product)
    totalamount = 0
    # print(cart_product,"")
    # if cart_product:
    for p in cart_product:
        tempamount = (p.quantity * p.product.discounted_price)
        amount += tempamount
    totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'add':add, 'cart_items':cart_items,'totalamount':totalamount, 'cart_value':totalamount-70})

@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer,product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")