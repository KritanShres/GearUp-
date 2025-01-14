from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

urlpatterns = [
    #store
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('login-register/', views.signup_login_view, name='login-signup'),
    path('register/', views.signup, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('update_item/',views.updateItem,name='update_item'),
    #category


    #for filter
    path('items/',views.items, name='items'),

    #for tests
    path('tests/',views.test, name='tests'),
    
    #for detail page 
    path('detail/<int:pk>', views.detail, name='detail'),
]