from django.urls import path
from . import views
from account.views import user_profile

app_name = 'companies'
urlpatterns = [
    # ... other url patterns ...
    path('create-company/', views.create_company, name='create_company'),
    path('edit-company/<int:pk>/', views.create_or_edit_company, name='edit_company'),
    path('company-dashboard/<int:pk>/', views.company_dashboard, name='company-dashboard'),
    path('add-inventory/', views.add_inventory, name='add_inventory'),
    path('inventory/<int:pk>/', views.company_inventory, name='company-inventory'),
   


    path('company/<int:pk>/product/<int:product_pk>/', views.store_product_detail, name='store_product_detail'),
    path('company/', views.company_edit, name='company_detail'),
    path('companies/<int:pk>/', views.company_profile_detail, name='company-public'),
    path('companies/', views.list_companies, name='list-companies'),
     

    path('api/inventory/<int:pk>/', views.company_inventory_api, name='company-inventory-api'),
    path('api/pos/<int:store_id>/', views.pos_api, name='pos-api'),
    path('api/submit-order/<int:store_id>/', views.order_summary, name='submit-order'),

    path('api/companies/<int:company_id>/customers/', views.list_customers_api, name='list_customers_api'),
    path('api/companies/<int:company_id>/customers/<int:customer_id>/', views.customer_detail_api, name='customer_detail_api'),
    path('api/<int:customerId>/orders', views.fetch_customer_orders, name='fetch_customer_orders'),
]
