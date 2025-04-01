from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserWallet, Transaction

class UserWalletInline(admin.StackedInline):
    model = UserWallet
    can_delete = False
    verbose_name_plural = 'Wallet'

class CustomUserAdmin(UserAdmin):
    inlines = (UserWalletInline,)
    list_display = ('username', 'email', 'get_balance', 'is_staff')

    def get_balance(self, obj):
        try:
            return obj.userwallet.balance
        except UserWallet.DoesNotExist:
            return 0.00
    get_balance.short_description = 'Balance'

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'amount', 'timestamp')
    list_filter = ('timestamp', 'sender', 'receiver')
    search_fields = ('sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Transaction, TransactionAdmin)
