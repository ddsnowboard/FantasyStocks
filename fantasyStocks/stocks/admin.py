from django.contrib import admin
import stocks

# Register your models here.
def update(modeladmin, request, queryset):
    for i in queryset:
        i.update()
@admin.register(stocks.models.Stock)
class StockAdmin(admin.ModelAdmin):
    actions = [update]

@admin.register(stocks.models.Player)
class PlayerAdmin(admin.ModelAdmin):
    pass

@admin.register(stocks.models.Floor)
class FloorAdmin(admin.ModelAdmin):
    fields = ("name", "stocks", "permissiveness")
