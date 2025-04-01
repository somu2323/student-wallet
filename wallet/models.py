from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet"

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        UserWallet.objects.get_or_create(user=instance, defaults={'balance': 1000.00})

@receiver(post_save, sender=User)
def save_user_wallet(sender, instance, **kwargs):
    UserWallet.objects.get_or_create(user=instance, defaults={'balance': 1000.00})

class Transaction(models.Model):
    sender = models.ForeignKey(User, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.amount}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new transactions
            try:
                sender_wallet = UserWallet.objects.get(user=self.sender)
                receiver_wallet = UserWallet.objects.get(user=self.receiver)

                if sender_wallet.balance >= self.amount:
                    sender_wallet.balance -= self.amount
                    receiver_wallet.balance += self.amount

                    sender_wallet.save()
                    receiver_wallet.save()
                    super().save(*args, **kwargs)
                else:
                    raise ValueError('Insufficient balance')
            except UserWallet.DoesNotExist:
                raise ValueError('User wallet not found')
        else:
            super().save(*args, **kwargs)
