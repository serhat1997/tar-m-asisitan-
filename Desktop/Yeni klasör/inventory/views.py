from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
import datetime

from .models import InventoryItem, CATEGORIES, UNITS


@login_required
def inventory_list(request):
    cat_filter = request.GET.get('cat', '')
    status_filter = request.GET.get('status', '')

    items = InventoryItem.objects.filter(user=request.user)
    if cat_filter and cat_filter != 'all':
        items = items.filter(category=cat_filter)

    items = list(items)
    if status_filter == 'elde':
        items = [i for i in items if not i.is_sold]
    elif status_filter == 'satildi':
        items = [i for i in items if i.is_sold]

    # Summary stats
    total_purchase = sum(i.purchase_price for i in items)
    sold_items     = [i for i in items if i.is_sold]
    held_items     = [i for i in items if not i.is_sold]
    total_sold_rev = sum(i.sale_price for i in sold_items)
    total_held_val = sum(i.purchase_price for i in held_items)
    total_profit   = sum(i.profit for i in sold_items if i.profit is not None)

    ctx = {
        'items': items,
        'categories': CATEGORIES,
        'units': UNITS,
        'cat_filter': cat_filter,
        'status_filter': status_filter,
        'total_purchase': total_purchase,
        'total_sold_rev': total_sold_rev,
        'total_held_val': total_held_val,
        'total_profit': total_profit,
        'sold_count': len(sold_items),
        'held_count': len(held_items),
        'today': datetime.date.today().isoformat(),
    }
    return render(request, 'inventory/inventory_list.html', ctx)


@login_required
def inventory_create(request):
    if request.method == 'POST':
        return _save_item(request, None)
    return render(request, 'inventory/inventory_form.html', {
        'categories': CATEGORIES,
        'units': UNITS,
        'today': datetime.date.today().isoformat(),
    })


@login_required
def inventory_edit(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk, user=request.user)
    if request.method == 'POST':
        return _save_item(request, item)
    return render(request, 'inventory/inventory_form.html', {
        'item': item,
        'categories': CATEGORIES,
        'units': UNITS,
        'today': datetime.date.today().isoformat(),
    })


@login_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk, user=request.user)
    if request.method == 'POST':
        name = item.name
        item.delete()
        messages.success(request, f'"{name}" envanterden silindi.')
    return redirect('inventory_list')


def _save_item(request, item):
    name           = request.POST.get('name', '').strip()
    category       = request.POST.get('category', 'diger').strip()
    model_info     = request.POST.get('model_info', '').strip()
    quantity_raw   = request.POST.get('quantity', '1').strip().replace(',', '.')
    unit           = request.POST.get('unit', 'adet').strip()
    purchase_raw   = request.POST.get('purchase_price', '').strip().replace(',', '.')
    purchase_date  = request.POST.get('purchase_date', '').strip()
    sale_raw       = request.POST.get('sale_price', '').strip().replace(',', '.')
    sale_date_raw  = request.POST.get('sale_date', '').strip()
    notes          = request.POST.get('notes', '').strip()

    errors = []
    if not name:
        errors.append('Envanter adı zorunludur.')
    if not purchase_raw:
        errors.append('Alış tutarı zorunludur.')
    if not purchase_date:
        errors.append('Alınış tarihi zorunludur.')

    try:
        qty_val = Decimal(quantity_raw) if quantity_raw else Decimal('1')
    except InvalidOperation:
        errors.append('Geçerli bir adet değeri girin.')
        qty_val = Decimal('1')

    try:
        purchase_val = Decimal(purchase_raw) if purchase_raw else Decimal('0')
    except InvalidOperation:
        errors.append('Geçerli bir alış tutarı girin.')
        purchase_val = Decimal('0')

    try:
        purchase_date_val = datetime.date.fromisoformat(purchase_date) if purchase_date else None
    except ValueError:
        errors.append('Geçerli bir alış tarihi girin.')
        purchase_date_val = None

    sale_val = None
    if sale_raw:
        try:
            sale_val = Decimal(sale_raw)
        except InvalidOperation:
            errors.append('Geçerli bir satış tutarı girin.')

    sale_date_val = None
    if sale_date_raw:
        try:
            sale_date_val = datetime.date.fromisoformat(sale_date_raw)
        except ValueError:
            errors.append('Geçerli bir satış tarihi girin.')

    if errors:
        for e in errors:
            messages.error(request, e)
        ctx = {
            'item': item,
            'categories': CATEGORIES,
            'units': UNITS,
            'form_data': request.POST,
            'today': datetime.date.today().isoformat(),
        }
        return render(request, 'inventory/inventory_form.html', ctx)

    if item is None:
        InventoryItem.objects.create(
            user=request.user,
            name=name, category=category, model_info=model_info,
            quantity=qty_val, unit=unit,
            purchase_price=purchase_val, purchase_date=purchase_date_val,
            sale_price=sale_val, sale_date=sale_date_val,
            notes=notes,
        )
        messages.success(request, f'"{name}" envantere eklendi.')
    else:
        item.name           = name
        item.category       = category
        item.model_info     = model_info
        item.quantity       = qty_val
        item.unit           = unit
        item.purchase_price = purchase_val
        item.purchase_date  = purchase_date_val
        item.sale_price     = sale_val
        item.sale_date      = sale_date_val
        item.notes          = notes
        item.save()
        messages.success(request, f'"{name}" güncellendi.')

    return redirect('inventory_list')
