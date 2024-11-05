from django.shortcuts import render,redirect
from django.http import HttpResponse
from common.models import Category
from store.models import Product
from django.utils.text import slugify
from django.shortcuts import get_object_or_404, redirect
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from account.views import is_seller
from account.models import DeliveryBoy
from django.urls import reverse
from django.contrib.auth.models import User

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.models import User

from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash


def home(request):
    category=Category.objects.all()
    products = Product.objects.filter(is_avilable=True)
    product_count=products.count()
    context = {'product':products,'product-count':product_count} 
    return render(request,'home.html',context)


def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        cat_image = request.FILES.get('cat_image')

        if not slug:
            slug = slugify(category_name)

        category = Category(
            category_name=category_name,
            slug=slug,
            description=description,
            cat_image=cat_image
        )
        category.save()
    return render(request, 'seller/seller_add_category.html')


def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        price = request.POST.get('price')
        images = request.FILES.get('images')
        stock = request.POST.get('stock')
        is_avilable = request.POST.get('is_avilable') == 'on'
        category_id = request.POST.get('category')
        sku = request.POST.get('sku')
        priority = request.POST.get('priority')
        category = Category.objects.get(id=category_id)
        if not slug:
            slug = slugify(product_name)

        product = Product(
            product_name=product_name,
            slug=slug,
            description=description,
            price=price,
            images=images,
            stock=stock,
            is_avilable=is_avilable,
            category=category,
            sku=sku,
            priority=priority
        )
        product.save()
    categories = Category.objects.all()
    return render(request, 'seller/seller_add_product.html', {'categories': categories})


def all_products(request):
    products = Product.objects.all()
    return render(request, 'seller/view_product.html', {'products': products})


def all_categories(request):
    categories = Category.objects.all()
    return render(request, 'seller/view_category.html', {'categories': categories})



def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('all_categories')


def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        cat_image = request.FILES.get('cat_image')
        category.category_name = category_name
        category.slug = slug
        category.description = description
        if cat_image:
            if category.cat_image:
                default_storage.delete(category.cat_image.name)
            category.cat_image = cat_image
        category.save()
        return redirect('all_categories')

    return render(request, 'seller/edit_category.html', {'category': category})


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()  

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.slug = request.POST.get('slug')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.is_avilable = request.POST.get('is_avilable') == 'on'
        product.category_id = request.POST.get('category')
        product.sku = request.POST.get('sku')
        product.priority = request.POST.get('priority')
        cat_image = request.FILES.get('images')

        if cat_image:
            if product.images:
                default_storage.delete(product.images.name)
            product.images = cat_image

        product.save()
        return redirect('all_products')
    return render(request, 'seller/edit_product.html', {'product': product, 'categories': categories})


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        if product.images:
            default_storage.delete(product.images.name)
        product.delete()
        return redirect('all_products')
    return render(request, 'confirm_delete_product.html', {'product': product})


def seller_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_staff and is_seller(u))(view_func))
    return decorated_view_func


@login_required(login_url='seller_login_view')
@seller_required
def seller_approve_delivery_view(request):
    delivery=DeliveryBoy.objects.all().filter(status=False)
    return render(request,'seller/seller_approved.html',{'delivery':delivery})


@login_required(login_url='seller_login_view')
@seller_required
def approve_delivery_view(request,pk):
    delivery=DeliveryBoy.objects.get(id=pk)
    delivery.status=True
    delivery.save()
    return redirect(reverse('seller_approve_delivery_view'))



@login_required(login_url='seller_login_view')
@seller_required
def reject_seller_view(request,pk):
    delivery=DeliveryBoy.objects.get(id=pk)
    user=User.objects.get(id=delivery.user_id)
    user.delete()
    delivery.delete()
    return redirect('seller_approve_delivery_view')



def seller_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_user_model().objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = request.build_absolute_uri(
                reverse('seller_reset_password', kwargs={'uidb64': uid, 'token': token})
            )

            subject = 'Password Reset Request'
            message = render_to_string('seller/seller_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })

            try:
                send_mail(subject, message, 'snehasatheesh176@gmail.com', [user.email])
                messages.success(request, 'Password reset link has been sent to your email.')
            except Exception as e:
                messages.error(request, f'Error sending email: {e}')
            return redirect('seller_forgot_password')
        else:
            messages.error(request, 'No account found with that email.')
    
    return render(request, 'seller/seller_forgot_password.html')



# Reset password
def seller_reset_password(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST['password']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password has been reset successfully. You can now log in with your new password.')
            return redirect('seller_login_view')  
        return render(request, 'seller/seller_reset_password.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'The link is invalid or has expired.')
        return redirect('seller_forgot_password')


@login_required
def seller_change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        user = request.user

        if not check_password(old_password, user.password):
            messages.error(request, 'Old password is incorrect.')
        elif new_password1 != new_password2:
            messages.error(request, 'The new passwords do not match.')
        elif not new_password1:
            messages.error(request, 'The new password cannot be empty.')
        else:
            user.set_password(new_password1)
            user.save()

            update_session_auth_hash(request, user)

            messages.success(request, 'Your password was successfully updated!')
            return redirect('seller_password_change_done')

    return render(request, 'seller/seller_password_change.html')


def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')