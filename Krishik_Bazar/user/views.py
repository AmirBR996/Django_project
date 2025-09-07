from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from .models import User  # Assuming User is a custom model with a password field
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from products.models import Product
# Registration with hashed password
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        role = request.POST.get('role')
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        password = request.POST.get('password').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered")
            return redirect('register')

        # Use the User manager's create_user method to handle hashing
        User.objects.create_user(
            username=username,
            email=email,
            password=password, # password is now automatically hashed
            role=role,
            phone=phone,
            address=address,
        )
        
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'register.html')

# Login with hashed password check
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()

        try:
            user = User.objects.get(email=email)
            # Use Django's authenticate to check the hashed password
            user_auth = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect('login')

        if user_auth is not None:
            # Login the user
            login(request, user_auth)
            # Store the role in the session
            request.session['user_role'] = user_auth.role
            messages.success(request, "Logged in successfully!")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('login')

    return render(request, 'login.html')

# Home view
def home(request):
    products = Product.objects.all()  # fetch all products
    return render(request, 'home.html', {"products": products})
# Logout view
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# Profile view
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def profile_update(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        role = request.POST.get('role')
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm-password', '').strip()

        # Check for unique username and email, excluding the current user
        if User.objects.exclude(pk=user.pk).filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('profile')
        if User.objects.exclude(pk=user.pk).filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect('profile')
            
        # Update user fields
        user.username = username
        user.email = email
        user.role = role
        user.phone = phone
        user.address = address

        # Handle password change
        if password:
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect('profile')
            user.set_password(password)
            messages.success(request, "Password updated successfully.")
            # Important: Update the user's session to prevent them from being logged out
            update_session_auth_hash(request, user)

        user.save()
        messages.success(request, "Profile updated successfully.")
        
    return redirect('profile')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products.html', {"products": [product]})