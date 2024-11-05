from django.shortcuts import render
from django.urls import path
from common import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_category', views.add_category, name='add_category'),
    path('add-product/', views.add_product, name='add_product'),
    path('all_products/', views.all_products, name='all_products'),
    path('all_categories/', views.all_categories, name='all_categories'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    
    
    path('seller_approve_delivery_view', views.seller_approve_delivery_view,name='seller_approve_delivery_view'),
    path('approve_delivery_view/<int:pk>', views.approve_delivery_view,name='approve_delivery_view'),
    path('reject_seller_view/<int:pk>', views.reject_seller_view,name='reject_seller_view'),
    
    
    path('seller_forgot_password', views.seller_forgot_password, name='seller_forgot_password'),
    path('seller_reset_password/<uidb64>/<token>/', views.seller_reset_password, name='seller_reset_password'),
    
    path('seller_password-change-done/', lambda request: render(request, 'seller/seller_password_change_done.html'), name='seller_password_change_done'),
    path('seller_change-password/', views.seller_change_password, name='seller_change_password'),
    path('contact',views.contact,name='contact'),
    path('about',views.about,name='about'),

    
]

