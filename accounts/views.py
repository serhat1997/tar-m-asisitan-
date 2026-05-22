from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, 'Şifreler eşleşmiyor!')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu kullanıcı adı zaten kullanılıyor!')
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Bu email zaten kayıtlı!')
            return render(request, 'accounts/register.html')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Kayıt başarılı! Lütfen giriş yapınız.')
        return redirect('login')

    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def about_view(request):
    return render(request, 'accounts/about.html')

def blog_view(request):
    return render(request, 'accounts/blog.html')

def contact_view(request):
    return render(request, 'accounts/contact.html')

@login_required
def user_list_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    users = User.objects.all().order_by('username')
    return render(request, 'accounts/users.html', {
        'users': users,
        'logged_user_name': request.user.username,
    })

@login_required
def user_suspend_view(request, user_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user.pk != request.user.pk:
            user.is_active = not user.is_active
            user.save()
            status = "askıya alındı" if not user.is_active else "aktif edildi"
            messages.success(request, f'"{user.username}" kullanıcısı {status}.')
        else:
            messages.error(request, 'Kendi hesabınızı askıya alamazsınız.')
    return redirect('user_list')

@login_required
def user_delete_admin_view(request, user_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user.pk != request.user.pk:
            username = user.username
            user.delete()
            messages.success(request, f'"{username}" kullanıcısı silindi.')
        else:
            messages.error(request, 'Kendi hesabınızı bu sayfadan silemezsiniz.')
    return redirect('user_list')

@login_required
def account_delete_view(request):
    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        if confirm == 'SIL':
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Hesabınız başarıyla silindi.')
            return redirect('login')
        else:
            messages.error(request, 'Onay metni hatalı. Hesabınız silinmedi.')
            return redirect('account_delete')
    return render(request, 'accounts/account_delete_confirm.html', {
        'logged_user_name': request.user.username,
    })
