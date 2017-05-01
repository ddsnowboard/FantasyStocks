from django.contrib import admin
import stocksApi

def deleteAllSessionIds(admin, request, queryset):
    stocksApi.models.SessionId.objects.all().delete()
deleteAllSessionIds.short_description = "Delete all session ids"

def pingAndroids(admin, request, queryset):
    for i in queryset:
        i.ping("Admin", "This is a test ping")
pingAndroids.short_description = "Ping"

# Register your models here.

@admin.register(stocksApi.models.AndroidToken)
class AndroidTokenAdmin(admin.ModelAdmin):
    fields = ("user", "token")
    actions = [pingAndroids]

@admin.register(stocksApi.models.SessionId)
class SessionIdAdmin(admin.ModelAdmin):
    fields = ("id_string", "associated_user", "exp_date")
    actions = [deleteAllSessionIds]
