from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Product
from functools import wraps
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
def farmer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('login')
        if request.user.role != 'farmer':
            messages.error(request, "Only farmers can access this page.")
            return redirect('home')  # Redirect to home instead of forbidden to avoid loops
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@farmer_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price_str = request.POST.get('price')
        stock_str = request.POST.get('stock')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        # Basic validation
        if not all([name, description, price_str, stock_str, category]):
            messages.error(request, "All fields are required.")
            return render(request, 'add_product.html', {'user': request.user, 'farmer_products': Product.objects.filter(user=request.user).order_by('-created_at')})

        try:
            price = float(price_str)
            stock = int(stock_str)
        except (ValueError, TypeError):
            messages.error(request, "Price and stock must be valid numbers.")
            return render(request, 'add_product.html', {'user': request.user, 'farmer_products': Product.objects.filter(user=request.user).order_by('-created_at')})

        # Create and save the new product
        new_product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image=image,
            user=request.user
        )

        messages.success(request, f"Product '{new_product.name}' added successfully!")
        return redirect('add_product')
    
    # Retrieve and display products for the current farmer
    farmer_products = Product.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'user': request.user,
        'farmer_products': farmer_products,
    }
    return render(request, 'add_product.html', context)

@farmer_required
def edit_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            product = Product.objects.get(id=product_id, user=request.user)
        except Product.DoesNotExist:
            messages.error(request, "Product not found or you do not have permission to edit it.")
            return redirect('add_product')

        name = request.POST.get('name')
        description = request.POST.get('description')
        price_str = request.POST.get('price')
        stock_str = request.POST.get('stock')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        # Validation
        if not all([name, description, price_str, stock_str, category]):
            messages.error(request, "All fields are required.")
            return redirect('add_product')

        try:
            price = float(price_str)
            stock = int(stock_str)
        except (ValueError, TypeError):
            messages.error(request, "Price and stock must be valid numbers.")
            return redirect('add_product')

        # Update product
        product.name = name
        product.description = description
        product.price = price
        product.stock = stock
        product.category = category
        if image:
            product.image = image
        product.save()

        messages.success(request, f"Product '{product.name}' updated successfully!")
        return redirect('add_product')

    return redirect('add_product')

@farmer_required
def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id, user=request.user)
            product_name = product.name
            product.delete()
            messages.success(request, f"Product '{product_name}' deleted successfully!")
        except Product.DoesNotExist:
            messages.error(request, "Product not found or you do not have permission to delete it.")
        return redirect('add_product')
    
    return redirect('add_product')

def view_products(request):
    # Start with all products
    products = Product.objects.all()
    
    # 1. Handle Filtering and Searching
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category=category_filter)
        
    # 2. Handle Sorting
    sort_by = request.GET.get('sort', 'date_desc') # Default to newest first
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'date_asc':
        products = products.order_by('created_at')
    else: # 'date_desc'
        products = products.order_by('-created_at')

    # 3. Handle Pagination
    paginator = Paginator(products, 12) # Show 12 products per page
    page_number = request.GET.get('page', 1)
    
    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    context = {
        'products': paginated_products, # Pass the paginated list to the template
        'search_query': search_query,
        'category_filter': category_filter,
        'sort_by': sort_by,
    }

    return render(request, 'products.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
    }
    # Render the same template with a single product
    return render(request, 'products.html', context)
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # This is placeholder logic. You will need to implement your
    # actual cart management here.
    # Example:
    # cart = request.session.get('cart', {})
    # cart[product.id] = cart.get(product.id, 0) + 1
    # request.session['cart'] = cart
    
    messages.success(request, f"{product.name} has been added to your cart!")
    
    return redirect('product_detail', product_id=product_id)