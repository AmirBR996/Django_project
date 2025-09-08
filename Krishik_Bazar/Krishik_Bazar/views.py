from django.shortcuts import render
def register(request):
    return render(request, 'register.html')
def login(request):
    return render(request, 'login.html')
def home(request):
    return render(request, 'home.html',{})
def logout_view(request):
    return render(request, 'home.html')
def profile(request):
    return render(request, 'profile.html')
def product(request):
    return render(request, 'product.html')
def add_product(request):
    return render(request, 'add_product.html')
def cart(request):
    return render(request, 'cart.html')
def checkout(request):
    return render(request, 'checkout.html')