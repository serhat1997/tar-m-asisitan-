from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
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
        
        reference_no = request.POST.get('reference_no', '').strip()
        Transaction.objects.create(
            user=request.user,
            customer=customer,
            type=type,
            product=product,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price,
            reference_no=reference_no,
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


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if not request.user.is_staff and transaction.user != request.user:
        raise Http404
    if request.method == 'POST':
        customer = transaction.customer
        if transaction.type == 'sale':
            customer.balance -= transaction.amount
        else:
            customer.balance += transaction.amount
        customer.save()
        transaction.delete()
        next_url = request.POST.get('next', '')
        if next_url:
            return redirect(next_url)
        return redirect('statement')
    return redirect('statement')
