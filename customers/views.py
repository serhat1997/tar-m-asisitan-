from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Customer
from transactions.models import Transaction

@login_required
def customer_list(request):
    if request.user.is_staff:
        # Admin tüm müşterileri görebilir
        customers = Customer.objects.all()
    else:
        # Normal kullanıcılar sadece kendi müşterilerini görebilir
        customers = Customer.objects.filter(user=request.user)
    return render(request, 'customers/customer_list.html', {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        Customer.objects.create(
            user=request.user,
            name=name,
            address=address,
            phone=phone,
            email=email
        )
        return redirect('customer_list')
    return render(request, 'customers/customer_form.html')

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    # Yetki kontrolü: admin veya müşteri sahibi erişebilir
    if not request.user.is_staff and customer.user != request.user:
        raise Http404("Bu müşteriyi görüntüleme izniniz yok!")
    
    transactions = Transaction.objects.filter(customer=customer).order_by('-date')
    return render(request, 'customers/customer_detail.html', {'customer': customer, 'transactions': transactions})
