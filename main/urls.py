from django.urls import path
from . import views
from .payment_views import initiate_payment, payment_callback

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('intermediate-dashboard/', views.intermediate_dashboard, name='intermediate_dashboard'),
    path('pro-dashboard/', views.pro_dashboard, name='pro_dashboard'),
    path('subscription/', views.subscription_view, name='subscription'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('payment/', initiate_payment, name='initiate_payment'),
    path('payment/callback/', payment_callback, name='payment_callback'),
] 