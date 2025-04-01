from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db import transaction, models
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import UserWallet, Transaction
from decimal import Decimal

@login_required
def settings(request):
    user_wallet = UserWallet.objects.get(user=request.user)
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            request.user.first_name = request.POST.get('fullname', '').split()[0]
            request.user.last_name = ' '.join(request.POST.get('fullname', '').split()[1:]) if len(request.POST.get('fullname', '').split()) > 1 else ''
            request.user.email = request.POST.get('email', '')
            request.user.profile.phone = request.POST.get('phone', '')
            request.user.save()
            request.user.profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('wallet:settings')
    return render(request, 'wallet/settings.html', {'wallet': user_wallet})

@login_required
def support(request):
    user_wallet = UserWallet.objects.get(user=request.user)
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        # Here you can add logic to handle the support message
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('wallet:support')
    return render(request, 'wallet/support.html', {'wallet': user_wallet})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserWallet.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'wallet/signup.html', {'form': form})

@login_required
def dashboard(request):
    user_wallet = UserWallet.objects.get(user=request.user)
    transactions = Transaction.objects.filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    ).order_by('-timestamp')[:5]
    
    return render(request, 'wallet/dashboard.html', {
        'wallet': user_wallet,
        'transactions': transactions
    })

@login_required
def transfer_money(request):
    user_wallet = UserWallet.objects.get(user=request.user)
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        amount = Decimal(request.POST.get('amount'))
        
        try:
            receiver = User.objects.get(username=receiver_username)
            if receiver == request.user:
                messages.error(request, 'You cannot transfer money to yourself')
                return redirect('transfer_money')
                
            with transaction.atomic():
                Transaction.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    amount=amount
                )
                messages.success(request, f'Successfully transferred {amount} to {receiver_username}')
                return redirect('dashboard')
        except User.DoesNotExist:
            messages.error(request, 'Recipient not found')
        except ValueError as e:
            messages.error(request, str(e))
    
    return render(request, 'wallet/transfer.html', {'wallet': user_wallet})

@login_required
def transaction_history(request):
    user_wallet = UserWallet.objects.get(user=request.user)
    transactions = Transaction.objects.filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    ).order_by('-timestamp')
    
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'wallet/transaction_history.html', {
        'page_obj': page_obj,
        'wallet': user_wallet
    })
