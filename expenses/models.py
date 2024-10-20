from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Expense(models.Model):
    description = models.CharField(max_length=255)
    total_amount = models.FloatField()
    split_method = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    users = models.ManyToManyField(User, through='ExpenseSplit')

    def __str__(self):
        return self.description


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_owed = models.FloatField()
