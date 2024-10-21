from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Import this
from .models import User, Expense, ExpenseSplit
import csv
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect
from django.contrib import messages

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = User.objects.get(name = username)
        
        if user is not None:
            if user.password != password:
                messages.error(request, "Invalid username or password")
                return render(request, 'login.html')
            #login(request, user)
            request.session['username'] = username  
            return redirect('add_expense')  # Redirect to the API or another valid page
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'login.html')

@csrf_exempt
def add_expense(request):
    if not is_logged_in(request):
        messages.error(request, "User not logged in!!")
        return redirect('login_form')
        
    if request.method == 'POST':
        description = request.POST.get('description')
        total_amount = float(request.POST.get('total_amount'))
        split_method = request.POST.get('split_method')

        # Handle "equal" split method
        if split_method == 'equal':
            user_names = request.POST.get('users_equal').split(',')
            valid_users = []
            for name in user_names:
                try:
                    user = User.objects.get(name=name.strip())  # Strip whitespace
                    valid_users.append(user)
                except ObjectDoesNotExist:
                    messages.error(request, f"User with name {name} does not exist.")
                    return redirect('add_expense')  # Redirect back to add expense page
            
            split_amount = total_amount / len(valid_users)

            # Create the Expense
            expense = Expense.objects.create(
                description=description,
                total_amount=total_amount,
                split_method=split_method
            )

            # Create ExpenseSplit entries for each user
            for user in valid_users:
                ExpenseSplit.objects.create(
                    expense=expense,
                    user=user,
                    amount_owed=split_amount
                )

        # Handle "exact" split method
        elif split_method == 'exact':
            user_entries = request.POST.get('exact_users').split(',')
            total_split_amount = 0
            valid_users = []

            for entry in user_entries:
                name, amount_owed = entry.split(':')
                try:
                    user = User.objects.get(name=name.strip())
                    valid_users.append((user, float(amount_owed.strip())))
                    total_split_amount += float(amount_owed.strip())
                except ObjectDoesNotExist:
                    messages.error(request, f"User with name {name} does not exist.")
                    return redirect('add_expense')  # Redirect back to add expense page

            if total_split_amount != total_amount:
                messages.error(request, "Total amount does not match the sum of individual exact amounts.")
                return redirect('add_expense')  # Redirect back to add expense page

            # Create the Expense
            expense = Expense.objects.create(
                description=description,
                total_amount=total_amount,
                split_method=split_method
            )

            # Create ExpenseSplit entries for each user
            for user, amount_owed in valid_users:
                ExpenseSplit.objects.create(
                    expense=expense,
                    user=user,
                    amount_owed=amount_owed
                )

        # Handle "percentage" split method
        elif split_method == 'percentage':
            user_entries = request.POST.get('percentage_users').split(',')
            total_percentage = 0
            valid_users = []

            for entry in user_entries:
                name, percentage = entry.split(':')
                try:
                    user = User.objects.get(name=name.strip())
                    valid_users.append((user, float(percentage.strip())))
                    total_percentage += float(percentage.strip())
                except ObjectDoesNotExist:
                    messages.error(request, f"User with name {name} does not exist.")
                    return redirect('add_expense')  # Redirect back to add expense page

            if total_percentage != 100:
                messages.error(request, "Total percentage does not equal 100.")
                return redirect('add_expense')  # Redirect back to add expense page

            # Create the Expense
            expense = Expense.objects.create(
                description=description,
                total_amount=total_amount,
                split_method=split_method
            )

            # Create ExpenseSplit entries for each user
            for user, percentage in valid_users:
                amount_owed = (percentage / 100) * total_amount
                ExpenseSplit.objects.create(
                    expense=expense,
                    user=user,
                    amount_owed=amount_owed
                )

        # Success message after successfully adding the expense
        messages.success(request, 'Expense added successfully!')
        return redirect('add_expense')  # Redirect back to add expense page for another entry

    return render(request, 'add_expense.html')
        

@csrf_exempt  # Disable CSRF for this view (optional, recommended to keep CSRF enabled)
def register_user(request):
    if request.method == 'POST':
        # Handle form data submission (POST request)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validate input data
        if not username or not password or not email:
            messages.error(request, 'All fields are required.')
            return redirect('register')  # Redirect back to registration page

        # Create and save the new user
        try:
            if User.objects.filter(name=username).exists():  # Use filter() instead of get() for existence check
                messages.error(request, 'Name already exists.')
                return redirect('register')  # Redirect back to registration page

            user = User.objects.create(
                name=username,
                email=email,
                password=password  # Hash the password before saving
            )
            
            messages.success(request, 'User registered successfully!')  # Success message
            return redirect('login_form')  # Redirect to the login page after successful registration
        except Exception as e:
            messages.error(request, str(e))  # Error message
            return redirect('register')  # Redirect back to registration page
    
    # Render the registration form (GET request)
    return render(request, 'register.html')


def is_logged_in(request):
    return 'username' in request.session


def download_balance_sheet_csv(request):

    if not is_logged_in(request):
        return redirect('login_form')  # Redirect to login if not logged in
    
    username = request.session['username']
    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="balance_sheet.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    writer.writerow(['User', 'Expense Description', 'Amount Owed'])

    # Fetch the expense splits for the authenticated user
    splits = ExpenseSplit.objects.all()  # No filtering by user if not logged in

    for split in splits:
        if split.user.name == username :
            writer.writerow([split.user.name, split.expense.description, split.amount_owed])

    return response



# Function to download the balance sheet in PDF format
def download_balance_sheet_pdf(request):
    if not is_logged_in(request):
        return redirect("login_form")  # Redirect to login if not logged in
    username = request.session['username']

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="balance_sheet.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Balance Sheet")

    p.setFont("Helvetica", 12)
    
    # Filter by the logged-in user
    splits = ExpenseSplit.objects.all()

    y_position = 750
    line_height = 20

    for split in splits:
        if split.user.name == username:
            print(split.user.__str__())
            p.drawString(100, y_position, f"User: {split.user.name}")
            p.drawString(300, y_position, f"Expense: {split.expense.description}")
            p.drawString(500, y_position, f"Owed: {split.amount_owed}")
            y_position -= line_height

            if y_position <= 50:
                p.showPage()
                y_position = 800

    p.showPage()
    p.save()

    return response


def user_logout(request):
    if 'username' in request.session:
        del request.session['username']  # Remove the username from the session
    return redirect('login_form')  