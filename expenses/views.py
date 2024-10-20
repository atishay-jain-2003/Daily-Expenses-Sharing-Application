from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Import this
from .models import User, Expense, ExpenseSplit
import json,csv
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
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
            return redirect('/api/')  # Redirect to the API or another valid page
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'login.html')


@csrf_exempt  # Disable CSRF for this view

@api_view(['POST'])
def add_expense(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Get the total amount and split method
        total_amount = data.get('total_amount')
        split_method = data.get('split_method')
        user_data = data.get('users', [])

        # Validate the split method
        if split_method not in ['equal', 'exact', 'percentage']:
            return JsonResponse({"error": "Invalid split method"}, status=400)

        # Initialize variables
        valid_users = []
        total_split_amount = 0
        total_percentage = 0

        # Validate each user by email instead of id
        for user_entry in user_data:
            try:
                user = User.objects.get(name=user_entry['name'])  # Fetch by email
                valid_users.append(user)
            except ObjectDoesNotExist:
                return JsonResponse({"error": f"User with name {user_entry['name']} does not exist"}, status=400)

            # Validate based on the split method
            if split_method == 'exact':
                amount_owed = user_entry.get('amount_owed')
                if amount_owed is None:
                    return JsonResponse({"error": f"Missing amount_owed for user {user.name}"}, status=400)
                total_split_amount += amount_owed

            elif split_method == 'percentage':
                percentage = user_entry.get('percentage')
                if percentage is None:
                    return JsonResponse({"error": f"Missing percentage for user {user.name}"}, status=400)
                total_percentage += percentage

        # Equal Split Validation
        if split_method == 'equal':
            if any('amount_owed' in user_entry for user_entry in user_data):
                return JsonResponse({"error": "Amount should not be provided for 'equal' split method"}, status=400)
            split_amount = total_amount / len(valid_users)

        # Exact Split Validation
        elif split_method == 'exact':
            if total_split_amount != total_amount:
                return JsonResponse({"error": "Total amount does not match the sum of individual exact amounts"}, status=400)

        # Percentage Split Validation
        elif split_method == 'percentage':
            if total_percentage != 100:
                return JsonResponse({"error": "Total percentage does not equal 100"}, status=400)

        # Create the Expense
        expense = Expense.objects.create(
            description=data.get('description'),
            total_amount=total_amount,
            split_method=split_method
        )

        # Create ExpenseSplit entries for each user
        for user_entry in user_data:
            user = User.objects.get(name=user_entry['name'])  # Fetch by email

            if split_method == 'equal':
                amount_owed = split_amount
            elif split_method == 'exact':
                amount_owed = user_entry.get('amount_owed')
            elif split_method == 'percentage':
                percentage = user_entry.get('percentage')
                amount_owed = (percentage / 100) * total_amount

            ExpenseSplit.objects.create(
                expense=expense,
                user=user,
                amount_owed=amount_owed
            )

        return JsonResponse({'message': 'Expense added successfully'})


# User Registration
@csrf_exempt
@api_view(['POST'])
def register_user(request):
    data = request.data
    try:
        # Check if the email already exists
        if User.objects.filter(email=data['name']).exists():
            return Response({'error': 'Name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create(
            name=data['name'],
            email=data['email'],
            password=data['password'] 
        )

        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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