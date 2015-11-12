from django.contrib import admin
import stocks

# Register your models here.
def update(modeladmin, request, queryset):
    for i in queryset:
        i.update()
def force_update(modeladmin, request, queryset):
    for i in queryset:
        i.force_update()

@admin.register(stocks.models.Stock)
class StockAdmin(admin.ModelAdmin):
    actions = [update, force_update]

@admin.register(stocks.models.Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "points", "pk")
    fields = ("user", "floor", "points")

@admin.register(stocks.models.Floor)
class FloorAdmin(admin.ModelAdmin):
    fields = ("name", "owner", "stocks", "permissiveness")
