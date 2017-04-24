from django.contrib import admin
import stocksApi

# Register your models here.

@admin.register(stocksApi.models.AndroidToken)
class AndroidTokenAdmin(admin.ModelAdmin):
    fields = ("user", "token")
    actions = [stocksApi.models.AndroidToken.ping]

@admin.register(stocksApi.models.SessionId)
class SessionIdAdmin(admin.ModelAdmin):
    fields = ("id_string", "associated_user", "exp_date")
    actions = []
