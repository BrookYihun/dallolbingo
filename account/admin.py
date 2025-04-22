from django.contrib import admin

from account.models import Account, Profile, UserGameCounter

admin.site.register(Account)
admin.site.register(UserGameCounter)
admin.site.register(Profile)
