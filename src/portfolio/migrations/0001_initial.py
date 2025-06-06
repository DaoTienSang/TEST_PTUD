# Generated by Django 4.2.7 on 2025-04-18 03:22

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('address', models.TextField(blank=True)),
            ],
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('stock', 'Cổ phiếu'), ('bond', 'Trái phiếu'), ('fund', 'Quỹ đầu tư')], max_length=10)),
                ('sector', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(choices=[('vietcombank', 'Vietcombank'), ('techcombank', 'Techcombank'), ('bidv', 'BIDV'), ('vietinbank', 'Vietinbank'), ('mbbank', 'MB Bank'), ('tpbank', 'TPBank'), ('acb', 'ACB'), ('sacombank', 'Sacombank'), ('vpbank', 'VPBank'), ('other', 'Ngân hàng khác')], max_length=100, verbose_name='Tên ngân hàng')),
                ('other_bank_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Tên ngân hàng khác')),
                ('account_name', models.CharField(max_length=255, verbose_name='Tên chủ tài khoản')),
                ('account_number', models.CharField(max_length=50, verbose_name='Số tài khoản')),
                ('branch', models.CharField(blank=True, max_length=255, null=True, verbose_name='Chi nhánh')),
                ('is_default', models.BooleanField(default=False, verbose_name='Là tài khoản mặc định')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bank_accounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Tài khoản ngân hàng',
                'verbose_name_plural': 'Tài khoản ngân hàng',
            },
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Tên danh mục')),
                ('description', models.TextField(blank=True, verbose_name='Mô tả')),
                ('investment_goal', models.CharField(blank=True, max_length=200, verbose_name='Mục tiêu đầu tư')),
                ('target_value', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Giá trị mục tiêu')),
                ('risk_tolerance', models.CharField(choices=[('low', 'Thấp'), ('medium', 'Trung bình'), ('high', 'Cao')], default='medium', max_length=10, verbose_name='Mức độ rủi ro')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolios', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Danh mục đầu tư',
                'verbose_name_plural': 'Danh mục đầu tư',
            },
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wallet', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ví điện tử',
                'verbose_name_plural': 'Ví điện tử',
            },
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('deposit', 'Nạp tiền'), ('withdraw', 'Rút tiền')], max_length=10, verbose_name='Loại giao dịch')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Số tiền')),
                ('fee', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Phí giao dịch')),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Số tiền thực nhận/thanh toán')),
                ('status', models.CharField(choices=[('pending', 'Đang xử lý'), ('completed', 'Hoàn thành'), ('failed', 'Thất bại'), ('cancelled', 'Đã hủy')], default='pending', max_length=10, verbose_name='Trạng thái')),
                ('payment_method', models.CharField(choices=[('bank_transfer', 'Chuyển khoản ngân hàng'), ('momo', 'Ví MoMo'), ('vnpay', 'VNPay'), ('other', 'Khác')], max_length=50, verbose_name='Phương thức thanh toán')),
                ('transaction_id', models.CharField(max_length=100, unique=True, verbose_name='Mã giao dịch')),
                ('reference_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='Mã tham chiếu')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Ghi chú')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Thời gian hoàn thành')),
                ('bank_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='portfolio.bankaccount', verbose_name='Tài khoản ngân hàng')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wallet_transactions', to=settings.AUTH_USER_MODEL)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='portfolio.wallet')),
            ],
            options={
                'verbose_name': 'Giao dịch ví điện tử',
                'verbose_name_plural': 'Giao dịch ví điện tử',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('buy', 'Mua'), ('sell', 'Bán')], max_length=4)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('transaction_date', models.DateTimeField()),
                ('notes', models.TextField(blank=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.asset')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.portfolio')),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('average_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('current_value', models.DecimalField(decimal_places=2, max_digits=15)),
                ('profit_loss', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.asset')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.portfolio')),
            ],
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['symbol'], name='portfolio_a_symbol_d2c1df_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['type'], name='portfolio_a_type_38f7d4_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['sector'], name='portfolio_a_sector_dd03c6_idx'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AddIndex(
            model_name='wallettransaction',
            index=models.Index(fields=['user'], name='portfolio_w_user_id_635388_idx'),
        ),
        migrations.AddIndex(
            model_name='wallettransaction',
            index=models.Index(fields=['wallet'], name='portfolio_w_wallet__8161fe_idx'),
        ),
        migrations.AddIndex(
            model_name='wallettransaction',
            index=models.Index(fields=['type'], name='portfolio_w_type_ff4dda_idx'),
        ),
        migrations.AddIndex(
            model_name='wallettransaction',
            index=models.Index(fields=['status'], name='portfolio_w_status_7e395f_idx'),
        ),
        migrations.AddIndex(
            model_name='wallettransaction',
            index=models.Index(fields=['transaction_id'], name='portfolio_w_transac_c7f850_idx'),
        ),
        migrations.AddIndex(
            model_name='wallettransaction',
            index=models.Index(fields=['created_at'], name='portfolio_w_created_2359b8_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['portfolio'], name='portfolio_t_portfol_40a214_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['asset'], name='portfolio_t_asset_i_590938_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['transaction_date'], name='portfolio_t_transac_374fda_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['transaction_type'], name='portfolio_t_transac_dded9c_idx'),
        ),
        migrations.AddIndex(
            model_name='portfolioasset',
            index=models.Index(fields=['portfolio'], name='portfolio_p_portfol_8c10b8_idx'),
        ),
        migrations.AddIndex(
            model_name='portfolioasset',
            index=models.Index(fields=['asset'], name='portfolio_p_asset_i_ba82d2_idx'),
        ),
        migrations.AddIndex(
            model_name='portfolio',
            index=models.Index(fields=['user'], name='portfolio_p_user_id_24fc7a_idx'),
        ),
        migrations.AddIndex(
            model_name='bankaccount',
            index=models.Index(fields=['user'], name='portfolio_b_user_id_541073_idx'),
        ),
        migrations.AddIndex(
            model_name='bankaccount',
            index=models.Index(fields=['account_number'], name='portfolio_b_account_ed6ace_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='portfolio_u_email_9eb857_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['username'], name='portfolio_u_usernam_41ed67_idx'),
        ),
    ]
