from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    account = models.DecimalField(max_digits=15, decimal_places=2)
    prepaid = models.BooleanField(default=False)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    backup_password = models.CharField(max_length=255,default="")
    privilege = models.BooleanField(default=False)
    min_stake = models.DecimalField(max_digits=10, decimal_places=0,default=20)

    def __str__(self):
        return self.name

class AgentAccount(models.Model):
    PAYMENT_METHOD_CHOICES=[
        (1, 'TELEBIRR'),
        (2, 'CBE'),
        (3, 'BOA'),
        (4, 'CBE_BIRR'),
    ]
    id=models.AutoField(primary_key=True)
    account_number=models.CharField(max_length=255,blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)
    payment_method = models.SmallIntegerField(choices=PAYMENT_METHOD_CHOICES)
    updated_at=models.DateTimeField(auto_now=True)
    agent=models.ForeignKey(Agent, on_delete=models.CASCADE,related_name='accounts')
    account_owner_name=models.CharField(max_length=255,blank=True,null=True)

    class Meta:
        db_table='agent_accounts'
        verbose_name='Agent Account'
        verbose_name_plural='Agent Accounts'
        unique_together = ('agent', 'payment_method')
    def __str__(self):
        return self.account_number or f"Account {self.id}"

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES=[
        (0,'Automatic'),
        (1,'Manual'),
    ]
    id=models.AutoField(primary_key=True)
    amount=models.DecimalField(max_digits=38, decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    transaction_id=models.CharField(max_length=255,blank=True,null=True,unique=True)
    status=models.SmallIntegerField(default=0)  # 0-pending,1-success,2-failed

    agent_account=models.ForeignKey(
        'AgentAccount',
        on_delete=models.CASCADE,
        db_column='agent_account_id',
        null=True
    )
    shop=models.ForeignKey(
        'account.Account',
        on_delete=models.CASCADE,
        related_name='transactions',
        db_column='account_account_id',
    )
    transaction_type=models.SmallIntegerField(blank=True,null=True,choices=TRANSACTION_TYPE_CHOICES)

    class Meta:
        db_table = 'transaction'  # Your existing table name
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.transaction_id or 'MANUAL-' + str(self.id)} - {self.amount}"