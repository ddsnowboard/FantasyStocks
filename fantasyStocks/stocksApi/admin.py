from django.contrib import admin
import stocksApi

def deleteAllSessionIds(admin, request, queryset):
    stocksApi.models.SessionId.objects.all().delete()
deleteAllSessionIds.short_description = "Delete all session ids"
# Register your models here.

@admin.register(stocksApi.models.AndroidToken)
class AndroidTokenAdmin(admin.ModelAdmin):
    fields = ("user", "token")
    actions = [stocksApi.models.AndroidToken.ping]

@admin.register(stocksApi.models.SessionId)
class SessionIdAdmin(admin.ModelAdmin):
    fields = ("id_string", "associated_user", "exp_date")
    actions = [deleteAllSessionIds]
