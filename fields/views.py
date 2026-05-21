from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
import datetime

from .models import Field, HarvestEntry, FieldExpense, PRODUCT_CHOICES, UNIT_CHOICES, EXPENSE_CATEGORIES


@login_required
def field_list(request):
    fields = Field.objects.prefetch_related('harvests', 'expenses').all()
    return render(request, 'fields/field_list.html', {'fields': fields})


@login_required
def field_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        area = request.POST.get('area', '').strip().replace(',', '.')
        crop_type = request.POST.get('crop_type', '').strip()
        notes = request.POST.get('notes', '').strip()
        if not name or not area:
            messages.error(request, 'Tarla adı ve alan zorunludur.')
            return render(request, 'fields/field_form.html', {'form_data': request.POST})
        try:
            area_val = Decimal(area)
        except InvalidOperation:
            messages.error(request, 'Geçerli bir alan değeri girin.')
            return render(request, 'fields/field_form.html', {'form_data': request.POST})
        Field.objects.create(name=name, area=area_val, crop_type=crop_type, notes=notes)
        messages.success(request, f'"{name}" tarlası eklendi.')
        return redirect('field_list')
    return render(request, 'fields/field_form.html', {})


@login_required
def field_detail(request, pk):
    field = get_object_or_404(Field, pk=pk)
    harvests = field.harvests.all()
    expenses = field.expenses.all()
    total_revenue = sum(h.amount for h in harvests)
    total_expense = sum(e.amount for e in expenses)
    net = total_revenue - total_expense
    ctx = {
        'field': field,
        'harvests': harvests,
        'expenses': expenses,
        'total_revenue': total_revenue,
        'total_expense': total_expense,
        'net': net,
        'product_choices': PRODUCT_CHOICES,
        'unit_choices': UNIT_CHOICES,
        'expense_categories': EXPENSE_CATEGORIES,
        'today': datetime.date.today().isoformat(),
    }
    return render(request, 'fields/field_detail.html', ctx)


@login_required
def field_edit(request, pk):
    field = get_object_or_404(Field, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        area = request.POST.get('area', '').strip().replace(',', '.')
        crop_type = request.POST.get('crop_type', '').strip()
        notes = request.POST.get('notes', '').strip()
        if not name or not area:
            messages.error(request, 'Tarla adı ve alan zorunludur.')
            return render(request, 'fields/field_form.html', {'field': field, 'form_data': request.POST})
        try:
            field.area = Decimal(area)
        except InvalidOperation:
            messages.error(request, 'Geçerli bir alan değeri girin.')
            return render(request, 'fields/field_form.html', {'field': field, 'form_data': request.POST})
        field.name = name
        field.crop_type = crop_type
        field.notes = notes
        field.save()
        messages.success(request, f'"{name}" güncellendi.')
        return redirect('field_detail', pk=field.pk)
    return render(request, 'fields/field_form.html', {'field': field})


@login_required
def field_delete(request, pk):
    field = get_object_or_404(Field, pk=pk)
    if request.method == 'POST':
        name = field.name
        field.delete()
        messages.success(request, f'"{name}" tarlası silindi.')
        return redirect('field_list')
    return redirect('field_detail', pk=pk)


@login_required
def harvest_add(request, pk):
    field = get_object_or_404(Field, pk=pk)
    if request.method == 'POST':
        date_str = request.POST.get('date', '').strip()
        product = request.POST.get('product', '').strip()
        quantity = request.POST.get('quantity', '').strip().replace(',', '.')
        unit = request.POST.get('unit', 'kg').strip()
        unit_price = request.POST.get('unit_price', '0').strip().replace(',', '.')
        notes = request.POST.get('notes', '').strip()
        try:
            date_val = datetime.date.fromisoformat(date_str)
            qty_val = Decimal(quantity)
            price_val = Decimal(unit_price) if unit_price else Decimal('0')
        except (ValueError, InvalidOperation):
            messages.error(request, 'Geçersiz tarih veya miktar.')
            return redirect('field_detail', pk=pk)
        HarvestEntry.objects.create(
            field=field, date=date_val, product=product,
            quantity=qty_val, unit=unit, unit_price=price_val, notes=notes
        )
        messages.success(request, 'Hasat kaydı eklendi.')
    return redirect('field_detail', pk=pk)


@login_required
def expense_add(request, pk):
    field = get_object_or_404(Field, pk=pk)
    if request.method == 'POST':
        date_str = request.POST.get('date', '').strip()
        category = request.POST.get('category', '').strip()
        amount = request.POST.get('amount', '').strip().replace(',', '.')
        description = request.POST.get('description', '').strip()
        try:
            date_val = datetime.date.fromisoformat(date_str)
            amount_val = Decimal(amount)
        except (ValueError, InvalidOperation):
            messages.error(request, 'Geçersiz tarih veya tutar.')
            return redirect('field_detail', pk=pk)
        FieldExpense.objects.create(
            field=field, date=date_val, category=category,
            amount=amount_val, description=description
        )
        messages.success(request, 'Gider kaydı eklendi.')
    return redirect('field_detail', pk=pk)


@login_required
def harvest_delete(request, pk, hpk):
    entry = get_object_or_404(HarvestEntry, pk=hpk, field__pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Hasat kaydı silindi.')
    return redirect('field_detail', pk=pk)


@login_required
def expense_delete(request, pk, epk):
    expense = get_object_or_404(FieldExpense, pk=epk, field__pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Gider kaydı silindi.')
    return redirect('field_detail', pk=pk)
