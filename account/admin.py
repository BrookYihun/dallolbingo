from django.contrib import admin

from account.models import Account, UserGameCounter, Deposit

admin.site.register(Account)
admin.site.register(UserGameCounter)
admin.site.register(Deposit)
