from django.contrib import admin
import stocksApi

# Register your models here.

@admin.register(stocksApi.models.AndroidToken)
class AndroidTokenAdmin(admin.ModelAdmin):
    fields = ("user", "token")
    actions = [stocksApi.models.AndroidToken.ping]
