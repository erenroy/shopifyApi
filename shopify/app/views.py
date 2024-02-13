from django.shortcuts import render , redirect , get_object_or_404
from django.views import View
from .models import Customer , Product , Cart , OrderPlaced
from .forms import CustomerRegistrationForm , CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Post
from .models import Contact
from django.contrib.auth.decorators import login_required

from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class ProductListAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProductView(View):
    def get(self,request):
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        return render(request, 'app/home.html' , {'topwears':topwears , 'bottomwears':bottomwears , 'mobiles':mobiles , 'laptops':laptops })

class ProductDetailView(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request, 'app/productdetail.html', {'product':product})

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user ,product=product).save()
    return redirect('/cart')
@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount =  amount + shipping_amount
            return render(request, 'app/addtocart.html',{'carts':cart , 'totalamount':totalamount , 'amount':amount})
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
            'quantity':c.quantity,
            'amount': amount,
            'totalamount': amount  + shipping_amount
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
            'quantity':c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        data = {
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)

@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')

@login_required
def address(request):
    add =  Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',{'add':add, 'active':'btn-primary'})
@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',{'order_placed':op})
@login_required
def mobile(request , data=None):
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Redmi' or data == 'Samsung':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)
    return render(request, 'app/mobile.html', {'mobiles':mobiles})

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',{'form':form})
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulations !! Registered successfuly')
            form.save()
        return render(request, 'app/customerregistration.html',{'form':form})

def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        totalamount = amount + shipping_amount

    return render(request, 'app/checkout.html', {'add':add , 'totalamount':totalamount, 'cart_items':cart_items})

class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request , 'app/profile.html',{'form':form,'active':'btn-primary'})
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcod = form.cleaned_data['zipcod']
            reg = Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcod=zipcod)
            reg.save()
            messages.success(request, 'congratulation  !! profile updated successfully ')
        return render(request, 'app/profile.html',{'form':form,'active':'btn-primary'})
@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    return redirect("orders")

def searchpage(request,q=None):
    query = request.GET.get('q','')
    if query == 'mobile':
        searchresult = Product.objects.filter(category='M')
    elif query == 'laptop':
        searchresult = Product.objects.filter(category='L')
    elif query == 'shirts':
        searchresult = Product.objects.filter(category='TW')
    elif query == 'pants':
        searchresult = Product.objects.filter(category='BW')
    elif query == query:
        searchresult = Product.objects.filter(brand__istartswith=query)
        if not searchresult:
            searchresult = Product.objects.filter(title__istartswith=query)
        

    return render(request, 'app/searchpage.html',{'query':query , 'searchresult':searchresult})

def laptop(request , data=None):
    if data == None:
        laptops = Product.objects.filter(category='L')
    elif data == 'Asus' or data == 'Apple':
        laptops  = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'below':
        laptops  = Product.objects.filter(category='L').filter(discounted_price__lt=10000)
    elif data == 'above':
        laptops = Product.objects.filter(category='L').filter(discounted_price__gt=10000)
    return render(request, 'app/laptop.html', {'laptops':laptops })

def Pricebarg(request , prod):
    a = 14
    product = Product.objects.get(pk=prod)
    products = product.discounted_price
    print(products)
    return render(request, 'app/pricebarg.html',{'product':product,'a':a} )
    
@login_required
def blog(request):
    allPosts = Post.objects.all()
    context = {'allPosts': allPosts}
    return render(request, 'app/blog.html',context )

def blogdetails(request,post_slug):
    post = get_object_or_404(Post , slug=post_slug)
    context = {'post': post}
    return render(request, 'app/blogdetails.html',context)

def subscription(request):
    return render(request, 'app/subscription.html')

def contact(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        username = request.POST['username']
        email = request.POST['email']
        address = request.POST['address']
        address_additional = request.POST['address_additional']
        phone = request.POST['phone']
        if len(fname)<2 or len(email)<3 or len(phone)<10 :
            pass
        else:
            contact = Contact(fname =fname ,lname=lname, username=username,address=address,email=email , phone=phone ,address_additional=address_additional)
            contact.save()

    return render(request, 'app/contact.html')



