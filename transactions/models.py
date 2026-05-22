from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Alış'),
        ('sale', 'Satış'),
    ]
    SALE_PRODUCTS = [
        ('cilek', 'Çilek'),
        ('elma', 'Elma'),
        ('kiraz', 'Kiraz'),
        ('seftali', 'Şeftali'),
    ]
    PURCHASE_PRODUCTS = [
        ('gubre', 'Gübre'),
        ('fide', 'Fide'),
        ('boru', 'Boru'),
    ]
    UNIT_CHOICES = [
        ('adet', 'Adet'),
        ('kg', 'Kg'),
        ('lt', 'Lt'),
        ('m', 'Metre'),
        ('paket', 'Paket'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    product = models.CharField(max_length=20, choices=SALE_PRODUCTS + PURCHASE_PRODUCTS)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='adet')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.customer.name} - {self.type} - {self.quantity} {self.unit} - {self.amount}"

    def save(self, *args, **kwargs):
        # Calculate amount from quantity and unit_price
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update customer balance
        if self.type == 'sale':
            self.customer.balance += self.amount
        elif self.type == 'purchase':
            self.customer.balance -= self.amount
        self.customer.save()
