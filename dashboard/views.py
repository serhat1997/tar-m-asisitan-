from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal, InvalidOperation
from transactions.models import Transaction
from customers.models import Customer
from .models import PaymentPlan

@login_required
def dashboard(request):
    # Admin tüm işlemleri görebilir, normal kullanıcılar sadece kendilerinkileri
    if request.user.is_staff:
        transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.filter(user=request.user)
    
    total_sales = transactions.filter(type='sale').aggregate(Sum('amount'))['amount__sum'] or 0
    total_purchases = transactions.filter(type='purchase').aggregate(Sum('amount'))['amount__sum'] or 0
    profit = total_sales - total_purchases

    def format_turkish_number(value):
        formatted = f"{value:,.2f}"
        return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

    return render(request, 'dashboard/dashboard.html', {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'profit': profit,
        'formatted_total_sales': format_turkish_number(total_sales),
        'formatted_total_purchases': format_turkish_number(total_purchases),
        'formatted_profit': format_turkish_number(profit),
        'greeting': f"Merhaba {request.user.first_name or request.user.get_full_name() or request.user.username} Hoş Geldin 👋",
        'logged_user_name': request.user.username,
    })

@login_required
def statement(request):
    if request.user.is_staff:
        transactions = Transaction.objects.all().order_by('-date')
    else:
        transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    def format_turkish_number(value):
        formatted = f"{value:,.2f}"
        return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

    for transaction in transactions:
        transaction.formatted_amount = format_turkish_number(transaction.amount)
        transaction.formatted_unit_price = format_turkish_number(transaction.unit_price)

    return render(request, 'dashboard/statement.html', {
        'transactions': transactions,
        'greeting': f"Merhaba {request.user.first_name or request.user.get_full_name() or request.user.username} 👋",
        'logged_user_name': request.user.username,
    })

@login_required
def payments(request):
    if request.user.is_staff:
        plans = PaymentPlan.objects.all().order_by('-created_at')
    else:
        plans = PaymentPlan.objects.filter(user=request.user).order_by('-created_at')

    def format_turkish_number(value):
        formatted = f"{value:,.2f}"
        return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')

    for plan in plans:
        plan.formatted_amount = format_turkish_number(plan.amount)

    return render(request, 'dashboard/payments.html', {
        'plans': plans,
        'greeting': f"Merhaba {request.user.first_name or request.user.get_full_name() or request.user.username} 👋",
        'logged_user_name': request.user.username,
    })

@login_required
def payment_create(request):
    errors = []
    form_data = {
        'customer': request.POST.get('customer', ''),
        'plan_type': request.POST.get('plan_type', ''),
        'payment_category': request.POST.get('payment_category', ''),
        'installments': request.POST.get('installments', '1'),
        'amount': request.POST.get('amount', ''),
        'due_date': request.POST.get('due_date', ''),
        'description': request.POST.get('description', ''),
    }

    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        plan_type = request.POST.get('plan_type')
        payment_category = request.POST.get('payment_category')
        installments_text = request.POST.get('installments', '1')
        amount_text = request.POST.get('amount', '0')
        due_date = request.POST.get('due_date') or None
        description = request.POST.get('description', '')

        if not customer_id:
            errors.append('Cari seçimi zorunludur.')
        if not plan_type:
            errors.append('Plan türü seçilmelidir.')
        if not payment_category:
            errors.append('Ödeme kategorisi seçilmelidir.')

        try:
            installments = int(installments_text or 1)
            if installments < 1:
                raise ValueError()
        except ValueError:
            errors.append('Taksit sayısı için geçerli bir sayı girin.')
            installments = 1

        normalized_amount = amount_text.strip().replace('₺', '').replace(' ', '')
        if normalized_amount.count(',') and normalized_amount.count('.'):
            normalized_amount = normalized_amount.replace('.', '').replace(',', '.')
        else:
            normalized_amount = normalized_amount.replace(',', '.')

        try:
            amount = Decimal(normalized_amount or '0')
            if amount <= 0:
                errors.append('Tutar sıfırdan büyük olmalıdır.')
        except (InvalidOperation, ValueError):
            errors.append('Geçerli bir tutar girin.')
            amount = Decimal('0')

        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                errors.append('Seçilen cari bulunamadı.')

        if customer and not request.user.is_staff and customer.user != request.user:
            return redirect('dashboard')

        if not errors and customer:
            PaymentPlan.objects.create(
                user=request.user,
                customer=customer,
                plan_type=plan_type,
                payment_category=payment_category,
                installments=installments,
                amount=amount,
                due_date=due_date,
                description=description,
            )
            return redirect('payments')

        for error in errors:
            messages.error(request, error)

    if request.user.is_staff:
        customers = Customer.objects.all()
    else:
        customers = Customer.objects.filter(user=request.user)

    return render(request, 'dashboard/payment_form.html', {
        'customers': customers,
        'form_data': form_data,
    })
