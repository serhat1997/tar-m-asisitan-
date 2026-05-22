from django.db import models


class Field(models.Model):
    name = models.CharField(max_length=150)
    area = models.DecimalField(max_digits=8, decimal_places=2, help_text='Dönüm')
    crop_type = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_harvest_revenue(self):
        return sum(e.amount for e in self.harvests.all())

    @property
    def total_expenses(self):
        return sum(e.amount for e in self.expenses.all())

    @property
    def net_profit(self):
        return self.total_harvest_revenue - self.total_expenses


PRODUCT_CHOICES = [
    ('cilek', 'Çilek'),
    ('elma', 'Elma'),
    ('kiraz', 'Kiraz'),
    ('seftali', 'Şeftali'),
    ('diger', 'Diğer'),
]

UNIT_CHOICES = [
    ('kg', 'Kg'),
    ('adet', 'Adet'),
    ('lt', 'Lt'),
    ('paket', 'Paket'),
    ('m', 'Metre'),
]

EXPENSE_CATEGORIES = [
    ('iscilik', 'İşçilik'),
    ('gubre', 'Gübre'),
    ('sulama', 'Sulama'),
    ('ilac', 'İlaç'),
    ('yakit', 'Yakıt'),
    ('ekipman', 'Ekipman'),
    ('diger', 'Diğer'),
]


class HarvestEntry(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='harvests')
    date = models.DateField()
    product = models.CharField(max_length=50, choices=PRODUCT_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    @property
    def amount(self):
        return self.quantity * self.unit_price


class FieldExpense(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    category = models.CharField(max_length=50, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
