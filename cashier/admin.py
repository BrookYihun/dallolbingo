from django.contrib import admin

from cashier.models import Cashier
from game.models import CashierGame

# Register your models here.

admin.site.register(Cashier)
admin.site.register(CashierGame)