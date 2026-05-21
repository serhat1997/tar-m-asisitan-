from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction
from customers.models import Customer
from decimal import Decimal

@login_required
def transaction_create(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        type = request.POST.get('type')
        product = request.POST.get('product')
        quantity = Decimal(request.POST.get('quantity', '1'))
        unit = request.POST.get('unit', 'adet')
        unit_price = Decimal(request.POST.get('unit_price', '0'))
        description = request.POST.get('description')
        
        # Yetki kontrolü: müşteri sadece kendi müşterilerine işlem ekleyebilir
        customer = Customer.objects.get(id=customer_id)
        if not request.user.is_staff and customer.user != request.user:
            return redirect('dashboard')
        
        Transaction.objects.create(
            user=request.user,
            customer=customer,
            type=type,
            product=product,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price,
            description=description
        )
        return redirect('dashboard')
    
    # Admin tüm müşterileri görebilir, normal kullanıcılar sadece kendilerinkileri
    if request.user.is_staff:
        customers = Customer.objects.all()
    else:
        customers = Customer.objects.filter(user=request.user)

    selected_type = request.GET.get('type', '')
    selected_product = request.GET.get('product', '')
    if selected_type not in ['sale', 'purchase']:
        selected_type = ''

    return render(request, 'transactions/transaction_form.html', {
        'customers': customers,
        'selected_type': selected_type,
        'selected_product': selected_product,
    })
