from threading import Thread
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib import admin
import stocks
from stocks.models import Player, Floor, Stock
import sys

# Stock admin functions
def update(modeladmin, request, queryset):
    for i in queryset:
        i.update()
        print("Updated {}".format(i), file=sys.stderr)
def force_update(modeladmin, request, queryset):
    for i in queryset:
        i.force_update()

def accept(modeladmin, request, queryset):
    for i in queryset:
        i.accept()

def rollback_time(modeladmin, request, queryset):
    for s in queryset:
        s.last_updated -= timedelta(minutes=20)
        s.save()

def resetToFloor(modeladmin, request, queryset):
    for i in queryset:
        for p in Player.objects.filter(floor=i):
            p.stocks = []
            p.save()
        i.floorPlayer.stocks = []
        for s in i.stocks.all():
            i.floorPlayer.stocks.add(s)
        i.floorPlayer.save()
resetToFloor.short_description = "Move all stocks to floor"

def zero_score(modeladmin, request, queryset):
    for p in queryset:
        p.points = 0
        p.save()

@admin.register(stocks.models.Stock)
class StockAdmin(admin.ModelAdmin):
    actions = [update, force_update, rollback_time]
    list_display = ("__str__", "last_updated")

@admin.register(stocks.models.Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "points", "pk")
    fields = ("user", "floor", "points", "stocks")
    actions = [zero_score]

@admin.register(stocks.models.Floor)
class FloorAdmin(admin.ModelAdmin):
    actions = [resetToFloor]
    fields = ("name", "owner", "public", "floorPlayer", "stocks", "permissiveness", "num_stocks")

@admin.register(stocks.models.Trade)
class TradeAdmin(admin.ModelAdmin):
    fields = ("recipient", "recipientStocks", "floor", "sender", "senderStocks")
    actions = [accept]

@admin.register(stocks.models.StockSuggestion)
class StockSuggestionAdmin(admin.ModelAdmin):
    actions = [accept]

def checkForBug(email=True, obj=None):
    def threadFunc(email, obj):
        problems = []
        for s in Stock.objects.all():
            for f in Floor.objects.all():
                players = Player.objects.filter(floor=f, stocks__id=s.pk)
                if len(players) > 1:
                    problems.append("Stock {stock} has more than one owner on {floor}: {owners}".format(stock=s, floor=f, owners=", ".join(str(p) for p in players)))
        
        for i in problems:
            print(i)
        if email and problems:
            send_mail("Error on FantasyStocks!", "\n".join(problems), "errors@fantasystocks.com", ["ddsnowboard@gmail.com"], fail_silently=True)
    Thread(target=threadFunc, args=(email, obj)).start()
