from django.db import models
from django.contrib.auth.models import User


CATEGORIES = [
    ('arac',     'Araç & Ekipman'),
    ('boru',     'Boru & Sulama'),
    ('malzeme',  'Malzeme'),
    ('elektronik','Elektronik'),
    ('diger',    'Diğer'),
]

UNITS = [
    ('adet',  'Adet'),
    ('metre', 'Metre'),
    ('kg',    'Kg'),
    ('lt',    'Litre'),
    ('paket', 'Paket'),
    ('takim', 'Takım'),
]


class InventoryItem(models.Model):
    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    name          = models.CharField(max_length=150, verbose_name='Envanter Adı')
    category      = models.CharField(max_length=20, choices=CATEGORIES, default='diger', verbose_name='Kategori')
    model_info    = models.CharField(max_length=150, blank=True, verbose_name='Model / Marka')
    quantity      = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='Adet / Miktar')
    unit          = models.CharField(max_length=10, choices=UNITS, default='adet', verbose_name='Birim')
    purchase_price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Alış Tutarı (₺)')
    purchase_date  = models.DateField(verbose_name='Alınış Tarihi')
    sale_price    = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name='Satış Tutarı (₺)')
    sale_date     = models.DateField(null=True, blank=True, verbose_name='Satış Tarihi')
    notes         = models.TextField(blank=True, verbose_name='Notlar')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchase_date', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    @property
    def is_sold(self):
        return self.sale_date is not None

    @property
    def profit(self):
        if self.sale_price is not None:
            return self.sale_price - self.purchase_price
        return None

    @property
    def profit_pct(self):
        if self.sale_price is not None and self.purchase_price:
            return ((self.sale_price - self.purchase_price) / self.purchase_price) * 100
        return None

    @property
    def unit_purchase_price(self):
        if self.quantity:
            return self.purchase_price / self.quantity
        return self.purchase_price

    @property
    def unit_sale_price(self):
        if self.sale_price is not None and self.quantity:
            return self.sale_price / self.quantity
        return None
