from django.contrib import admin
from agent.models import Agent, AgentAccount, Transaction

# Register your models here.

admin.site.register(Agent)
admin.site.register(AgentAccount)
admin.site.register(Transaction)
