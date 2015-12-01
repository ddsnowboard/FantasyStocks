from django.contrib import admin
import stocks

# Stock admin functions
def update(modeladmin, request, queryset):
    for i in queryset:
        i.update()
def force_update(modeladmin, request, queryset):
    for i in queryset:
        i.force_update()

def accept(modeladmin, request, queryset):
    for i in queryset:
        i.accept()
@admin.register(stocks.models.Stock)
class StockAdmin(admin.ModelAdmin):
    actions = [update, force_update]
    list_display = ("__str__", "last_updated")

@admin.register(stocks.models.Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "points", "pk")
    fields = ("user", "floor", "points", "stocks")

@admin.register(stocks.models.Floor)
class FloorAdmin(admin.ModelAdmin):
    fields = ("name", "owner", "floorPlayer", "stocks", "permissiveness")

@admin.register(stocks.models.Trade)
class TradeAdmin(admin.ModelAdmin):
    fields = ("recipient", "recipientStocks", "floor", "sender", "senderStocks")
    actions = [accept]
