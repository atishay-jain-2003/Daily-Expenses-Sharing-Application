from django.urls import path
from .views import (
    add_expense,
    register_user,
    user_login,
    download_balance_sheet_csv,
    download_balance_sheet_pdf,
    user_logout,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Expense management
    path('expenses/add/', add_expense, name='add_expense'),
    
    # User registration and authentication
    path('register/', register_user, name='register'),
    path('login/form/', user_login, name='login_form'),  # Web login form

    # Download balance sheets
    path('expenses/download/csv/', download_balance_sheet_csv, name='download_csv'),
    path('expenses/download/pdf/', download_balance_sheet_pdf, name='download_pdf'),

    # Logout
    path('logout/', user_logout, name='logout'),
]
