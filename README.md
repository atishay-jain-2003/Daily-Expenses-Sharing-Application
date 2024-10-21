# Expense Share Application

## Overview

The Expense Share Application is a web-based platform designed to help users manage and share daily expenses. Users can register, log in, add expenses, and download balance sheets in CSV or PDF formats. The application is built using Django and utilizes session management for user authentication.

## Features

- User registration and authentication
- Add and manage expenses
- Download balance sheets in CSV and PDF formats

## Technologies Used

- Django: The web framework used for building the application
- Python: The programming language used for backend development
- HTML/CSS: For the frontend design
- SQLite: The database for storing user and expense data
- ReportLab: For generating PDF reports

## Setup Instructions

Follow the steps below to set up and run the project locally:

### Prerequisites

- Python 3.x installed on your machine
- Pip (Python package installer) installed

### Installation Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/atishay-jain-2003/Daily-Expenses-Sharing-Application.git
   cd Daily-Expenses-Sharing-Application

2. **Install Required Packages**
   
   ```bash
   pip install -r requirements.txt

3. **Set Up the Database**

   Run the following command to create the database and apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate

4. **Run the Development Server**
   
   Start the Django development server:
   ```bash
   python manage.py runserver

### Usage
1. **Registration**

   Go to /register/ to create a new user account.

3. **Login**

   Navigate to /login/form/ to log in using your registered username and password.

4. **Add Expenses**

   Once logged in, use /expenses/add/ to add new expenses.
5. **Download Balance Sheets**

   You can download your balance sheet in CSV format at /expenses/download/csv/ or in PDF format at /expenses/download/pdf/.
6. **Logout**
   
   Use the /logout/ route to log out of your account.

### Contributing
Contributions are welcome! Please fork the repository and create a pull request for any enhancements or bug fixes.

### Contact
For any questions or feedback, feel free to reach out:

Email: atishayjainaj671@gmail.com

GitHub Profile: https://github.com/atishay-jain-2003

