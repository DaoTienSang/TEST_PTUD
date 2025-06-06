from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.core.paginator import Paginator
from datetime import timedelta
import uuid
from django.db import transaction

from .models import Wallet, BankAccount, WalletTransaction
from .forms import BankAccountForm, DepositForm, WithdrawForm
from .templatetags.currency_filters import dinh_dang_tien

@login_required
def wallet(request):
    # Lấy hoặc tạo ví cho người dùng
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Lấy danh sách tài khoản ngân hàng
    bank_accounts = BankAccount.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    # Lấy giao dịch gần đây
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Lọc giao dịch theo loại nếu có tham số trong query
    transaction_type = request.GET.get('type')
    if transaction_type in ['deposit', 'withdraw']:
        transactions = transactions.filter(type=transaction_type)
    
    # Phân trang giao dịch
    paginator = Paginator(transactions, 10)  # 10 giao dịch mỗi trang
    page_number = request.GET.get('page')
    paged_transactions = paginator.get_page(page_number)
    
    # Tính tổng nạp/rút
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    total_deposit = WalletTransaction.objects.filter(
        user=request.user, 
        type='deposit', 
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_withdraw = WalletTransaction.objects.filter(
        user=request.user, 
        type='withdraw', 
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_deposit = WalletTransaction.objects.filter(
        user=request.user, 
        type='deposit', 
        status='completed',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_withdraw = WalletTransaction.objects.filter(
        user=request.user, 
        type='withdraw', 
        status='completed',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'wallet': wallet,
        'bank_accounts': bank_accounts,
        'transactions': paged_transactions,
        'total_deposit': total_deposit,
        'total_withdraw': total_withdraw,
        'monthly_deposit': monthly_deposit,
        'monthly_withdraw': monthly_withdraw
    }
    
    return render(request, 'portfolio/wallet.html', context)

@login_required
def deposit_money(request):
    # Lấy hoặc tạo ví cho người dùng
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Lấy danh sách tài khoản ngân hàng
    bank_accounts = BankAccount.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    if request.method == 'POST':
        print("POST request received for deposit_money")
        print("POST data:", request.POST)
        
        form = DepositForm(request.user, request.POST)
        if form.is_valid():
            print("Form is valid, processing deposit...")
            # Xử lý form nạp tiền
            amount = form.cleaned_data['amount']
            payment_method = form.cleaned_data['payment_method']
            bank_account = form.cleaned_data.get('bank_account')
            agree_terms = form.cleaned_data['agree_terms']
            
            # Tạo transaction_id duy nhất để tránh giao dịch trùng lặp
            transaction_id = f"DEP{uuid.uuid4().hex[:8].upper()}"
            
            # Kiểm tra xem giao dịch có trùng lặp không (trong vòng 5 phút gần đây)
            five_minutes_ago = timezone.now() - timedelta(minutes=5)
            recent_deposits = WalletTransaction.objects.filter(
                user=request.user,
                type='deposit',
                amount=amount,
                payment_method=payment_method,
                created_at__gte=five_minutes_ago
            )
            
            if recent_deposits.exists():
                messages.warning(request, 'Một giao dịch nạp tiền tương tự đã được thực hiện trong vòng 5 phút qua. Vui lòng đợi một lát và kiểm tra số dư của bạn trước khi thử lại.')
                return redirect('wallet')
            
            # Nếu là phương thức thanh toán chuyển khoản ngân hàng nhưng không chọn tài khoản nào
            if payment_method == 'bank_transfer' and not bank_account:
                # Xử lý tài khoản ngân hàng mới
                bank_name = form.cleaned_data.get('new_bank_name')
                other_bank_name = form.cleaned_data.get('new_other_bank_name')
                account_name = form.cleaned_data.get('new_account_name')
                account_number = form.cleaned_data.get('new_account_number')
                branch = form.cleaned_data.get('new_branch')
                is_default = form.cleaned_data.get('new_is_default', False)
                
                if bank_name and account_name and account_number:
                    if bank_name == 'other' and other_bank_name:
                        display_name = other_bank_name
                    else:
                        display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
                    
                    # Tạo tài khoản ngân hàng mới
                    bank_account = BankAccount.objects.create(
                        user=request.user,
                        bank_name=bank_name,
                        other_bank_name=other_bank_name,
                        account_name=account_name,
                        account_number=account_number,
                        branch=branch,
                        is_default=is_default
                    )
                    
                    messages.success(request, f'Đã thêm tài khoản {display_name} - {account_number}')
                else:
                    messages.error(request, 'Vui lòng chọn hoặc thêm tài khoản ngân hàng để tiếp tục nạp tiền.')
                    return redirect('deposit_money')
            
            # Sử dụng transaction.atomic để đảm bảo tính toàn vẹn dữ liệu
            with transaction.atomic():
                # Tạo giao dịch nạp tiền
                transaction_obj = WalletTransaction.objects.create(
                    user=request.user,
                    wallet=wallet,
                    type='deposit',
                    amount=amount,
                    fee=0,  # Miễn phí nạp tiền
                    net_amount=amount,
                    status='completed',  # Trạng thái hoàn thành thay vì pending
                    bank_account=bank_account,
                    payment_method=payment_method,
                    transaction_id=transaction_id,
                    notes=f"Nạp tiền qua {dict(WalletTransaction.PAYMENT_METHOD_CHOICES)[payment_method]}"
                )
            
            messages.success(request, f'Nạp tiền thành công! Số dư của bạn đã được cập nhật: {dinh_dang_tien(wallet.balance)} VNĐ với thông tin Balance Information<br>Số dư khả dụng: {dinh_dang_tien(wallet.balance)} VNĐ')
            return redirect('wallet')
        else:
            print("Form is invalid")
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = DepositForm(request.user)
    
    context = {
        'wallet': wallet,
        'bank_accounts': bank_accounts,
        'form': form
    }
    
    return render(request, 'portfolio/deposit.html', context)

@login_required
def withdraw_money(request):
    # Lấy hoặc tạo ví cho người dùng
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Lấy danh sách tài khoản ngân hàng
    bank_accounts = BankAccount.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    if request.method == 'POST':
        form = WithdrawForm(request.user, request.POST)
        if form.is_valid():
            # Xử lý form rút tiền
            amount = form.cleaned_data['amount']
            bank_account = form.cleaned_data.get('bank_account')
            withdraw_note = form.cleaned_data.get('notes', '')
            
            # Kiểm tra số dư
            if amount > wallet.balance:
                messages.error(request, 'Số dư của bạn không đủ để thực hiện giao dịch này.')
                return redirect('withdraw_money')
            
            # Nếu không chọn tài khoản nào
            if not bank_account:
                # Xử lý tài khoản ngân hàng mới
                bank_name = form.cleaned_data.get('new_bank_name')
                other_bank_name = form.cleaned_data.get('new_other_bank_name')
                account_name = form.cleaned_data.get('new_account_name')
                account_number = form.cleaned_data.get('new_account_number')
                branch = form.cleaned_data.get('new_branch')
                is_default = form.cleaned_data.get('new_is_default', False)
                
                if bank_name and account_name and account_number:
                    if bank_name == 'other' and other_bank_name:
                        display_name = other_bank_name
                    else:
                        display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
                    
                    # Tạo tài khoản ngân hàng mới
                    bank_account = BankAccount.objects.create(
                        user=request.user,
                        bank_name=bank_name,
                        other_bank_name=other_bank_name,
                        account_name=account_name,
                        account_number=account_number,
                        branch=branch,
                        is_default=is_default
                    )
                    
                    messages.success(request, f'Đã thêm tài khoản {display_name} - {account_number}')
                else:
                    messages.error(request, 'Vui lòng chọn hoặc thêm tài khoản ngân hàng để tiếp tục rút tiền.')
                    return redirect('withdraw_money')
            
            # Không tính phí rút tiền
            fee = 0
            net_amount = amount
            
            # Tạo transaction_id duy nhất để tránh giao dịch trùng lặp
            transaction_id = f"WIT{uuid.uuid4().hex[:8].upper()}"
            
            # Kiểm tra xem giao dịch có trùng lặp không (trong vòng 5 phút gần đây)
            five_minutes_ago = timezone.now() - timedelta(minutes=5)
            recent_withdrawals = WalletTransaction.objects.filter(
                user=request.user,
                type='withdraw',
                amount=amount,
                created_at__gte=five_minutes_ago
            )
            
            if recent_withdrawals.exists():
                messages.warning(request, 'Một giao dịch rút tiền tương tự đã được thực hiện trong vòng 5 phút qua. Vui lòng đợi một lát và kiểm tra số dư của bạn trước khi thử lại.')
                return redirect('wallet')
            
            # Sử dụng transaction.atomic để đảm bảo tính toàn vẹn dữ liệu
            with transaction.atomic():
                # Tạo giao dịch rút tiền
                transaction_obj = WalletTransaction.objects.create(
                    user=request.user,
                    wallet=wallet,
                    type='withdraw',
                    amount=amount,
                    fee=fee,
                    net_amount=net_amount,
                    status='completed',  # Trạng thái hoàn thành thay vì pending
                    bank_account=bank_account,
                    payment_method='bank_transfer',
                    transaction_id=transaction_id,
                    notes=withdraw_note
                )
            
            messages.success(
                request, 
                f'Rút tiền thành công! '
                f'<br>Số tiền rút: {dinh_dang_tien(amount)} VNĐ'
                f'<br>Số tiền thực nhận: {dinh_dang_tien(net_amount)} VNĐ'
                f'<br>Số dư còn lại: {dinh_dang_tien(wallet.balance)} VNĐ'
            )
            return redirect('wallet')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = WithdrawForm(request.user)
    
    context = {
        'wallet': wallet,
        'bank_accounts': bank_accounts,
        'form': form
    }
    
    return render(request, 'portfolio/withdraw.html', context)

@login_required
def bank_account_list(request):
    bank_accounts = BankAccount.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    context = {
        'bank_accounts': bank_accounts
    }
    
    return render(request, 'portfolio/bank_account_list.html', context)

@login_required
def bank_account_create(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            bank_account = form.save(commit=False)
            bank_account.user = request.user
            bank_account.save()
            
            bank_name = form.cleaned_data['bank_name']
            if bank_name == 'other':
                display_name = form.cleaned_data['other_bank_name']
            else:
                display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
                
            account_number = form.cleaned_data['account_number']
            
            messages.success(request, f'Đã thêm tài khoản {display_name} - {account_number}')
            return redirect('bank_account_list')
    else:
        form = BankAccountForm()
    
    context = {
        'form': form,
        'title': 'Thêm tài khoản ngân hàng'
    }
    
    return render(request, 'portfolio/bank_account_form.html', context)

@login_required
def update_bank_account(request, pk):
    bank_account = get_object_or_404(BankAccount, id=pk, user=request.user)
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=bank_account)
        if form.is_valid():
            form.save()
            
            bank_name = form.cleaned_data['bank_name']
            if bank_name == 'other':
                display_name = form.cleaned_data['other_bank_name']
            else:
                display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
                
            account_number = form.cleaned_data['account_number']
            
            messages.success(request, f'Đã cập nhật tài khoản {display_name} - {account_number}')
            return redirect('bank_account_list')
    else:
        form = BankAccountForm(instance=bank_account)
    
    context = {
        'form': form,
        'bank_account': bank_account,
        'title': 'Cập nhật tài khoản ngân hàng'
    }
    
    return render(request, 'portfolio/bank_account_form.html', context)

@login_required
def delete_bank_account(request, pk):
    bank_account = get_object_or_404(BankAccount, id=pk, user=request.user)
    
    if request.method == 'POST':
        # Kiểm tra xem có giao dịch đang sử dụng tài khoản này không
        transactions_using_account = WalletTransaction.objects.filter(
            bank_account=bank_account,
            status='pending'
        ).exists()
        
        if transactions_using_account:
            messages.error(request, 'Không thể xóa tài khoản này vì có giao dịch đang xử lý.')
            return redirect('bank_account_list')
        
        # Lưu thông tin để hiển thị thông báo
        bank_name = bank_account.bank_name
        if bank_name == 'other':
            display_name = bank_account.other_bank_name
        else:
            display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
            
        account_number = bank_account.account_number
        
        # Xóa tài khoản
        bank_account.delete()
        
        messages.success(request, f'Đã xóa tài khoản {display_name} - {account_number}')
        return redirect('bank_account_list')
    
    context = {
        'bank_account': bank_account
    }
    
    return render(request, 'portfolio/bank_account_confirm_delete.html', context)

@login_required
def set_default_bank_account(request, pk):
    bank_account = get_object_or_404(BankAccount, id=pk, user=request.user)
    
    # Đặt tất cả tài khoản khác thành không mặc định
    BankAccount.objects.filter(user=request.user).update(is_default=False)
    
    # Đặt tài khoản hiện tại thành mặc định
    bank_account.is_default = True
    bank_account.save()
    
    bank_name = bank_account.bank_name
    if bank_name == 'other':
        display_name = bank_account.other_bank_name
    else:
        display_name = dict(BankAccount.BANK_CHOICES)[bank_name]
        
    account_number = bank_account.account_number
    
    messages.success(request, f'Đã đặt {display_name} - {account_number} làm tài khoản mặc định')
    
    return redirect('bank_account_list')

@login_required
def wallet_transactions(request):
    # Lấy tất cả giao dịch của người dùng
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at')
    
    # Lọc theo loại giao dịch nếu có
    transaction_type = request.GET.get('type')
    if transaction_type in ['deposit', 'withdraw']:
        transactions = transactions.filter(type=transaction_type)
    
    # Lọc theo trạng thái nếu có
    status = request.GET.get('status')
    if status in ['pending', 'completed', 'failed', 'cancelled']:
        transactions = transactions.filter(status=status)
    
    # Lọc theo ngày
    from_date = request.GET.get('from_date')
    if from_date:
        transactions = transactions.filter(created_at__gte=from_date)
    
    to_date = request.GET.get('to_date')
    if to_date:
        transactions = transactions.filter(created_at__lte=to_date)
    
    # Phân trang
    paginator = Paginator(transactions, 10)  # 10 giao dịch mỗi trang
    page_number = request.GET.get('page')
    paged_transactions = paginator.get_page(page_number)
    
    context = {
        'transactions': paged_transactions,
        'transaction_types': WalletTransaction.TYPE_CHOICES,
        'status_choices': WalletTransaction.STATUS_CHOICES
    }
    
    return render(request, 'portfolio/wallet_transactions.html', context)