from django.contrib import admin
import stocks

# Register your models here.
def update(modeladmin, request, queryset):
    for i in queryset:
        i.update()
@admin.register(stocks.models.Stock)
class StockAdmin(admin.ModelAdmin):
    actions = [update]
