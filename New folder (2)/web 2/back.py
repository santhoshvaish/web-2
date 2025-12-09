
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(_file_)))
SECRET_KEY = 'replace-this-with-a-secure-key'
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'thanam_site.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'store', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]},
    },
]
WSGI_APPLICATION = 'thanam_site.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'store', 'static')]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]

import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thanam_site.settings')
application = get_wsgi_application()

from django.apps import AppConfig
class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

from django.contrib import admin
from .models import Category, Product
admin.site.register(Category)
admin.site.register(Product)

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    def _str_(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.CharField(max_length=300, blank=True)  # URL or static path
    is_offer = models.BooleanField(default=False)

    def _str_(self):
        return self.name

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]

from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product
from django.db.models import Q

def home(request):
    categories = Category.objects.all()
    offers = Product.objects.filter(is_offer=True)[:6]
    return render(request, 'store/home.html', {'categories': categories, 'offers': offers})

def products(request):
    q = request.GET.get('q','').strip()
    cat = request.GET.get('category','')
    products = Product.objects.all()
    if cat:
        products = products.filter(category__slug=cat)
    if q:
        products = products.filter(Q(name_icontains=q)|Q(description_icontains=q))
    categories = Category.objects.all()
    return render(request, 'store/products.html',{'products': products, 'categories': categories, 'q': q, 'selected_cat': cat})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})
    item = cart.get(str(pk), {'quantity': 0, 'name': product.name, 'price': str(product.price)})
    item['quantity'] = item.get('quantity', 0) + 1
    cart[str(pk)] = item
    request.session['cart'] = cart
    return redirect('cart')

def cart_view(request):
    cart = request.session.get('cart', {})
    total = sum(float(item['price'])*item['quantity'] for item in cart.values())
    return render(request, 'store/cart.html', {'cart': cart, 'total': total})

def about(request):
    return render(request, 'store/about.html')

def contact(request):
    return render(request, 'store/contact.html') 