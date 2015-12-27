from django.test import TestCase
from django import test
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.staticfiles.templatetags.staticfiles import static
from stocks.models import *
import json
import time
from functools import reduce
import urllib

class MainTestCase(StaticLiveServerTestCase):
    def setUp(self):
        NUMBER_OF_USERS = 100
        with urllib.request.urlopen(self.live_server_url + static("stocks.json")) as f:
            available_stocks = [Stock.objects.create(symbol=i["symbol"]) for i in json.loads(f.read().decode("UTF-8"))]
        floor_user = User.objects.create_user("Floor", "floor@floors.net", "flooring")
        floor_group = Group.objects.create(name="Floor")
        floor_group.save()
        floor_user.groups.add(floor_group)
        floor_user.save()
        floor = Floor.objects.create(name="TestingFloor", permissiveness="open")
        floor_player = Player.objects.create(user=floor_user, points=0, floor=floor)
        floor.floorPlayer = floor_player
        floor_player.save()
        floor.save()
        print("start creating users")
        for i in range(NUMBER_OF_USERS):
            user = User.objects.create_user("user_{}".format(i), "user_{}@mailmail.mail".format(i), "thePasswordIs{}".format(i))
            player = Player.objects.create(user=user, floor=floor)
            player.stocks.add(available_stocks.pop())
            user.save()
            player.save()
        print("done creating users")
    def test_scoring_time(self):
        start = time.clock()
        floor = Floor.objects.all()[0]
        DEFAULT_PRICE = 5
        for s in floor.stocks.all():
            s.price = DEFAULT_PRICE
            s.update()
        for p in Player.objects.filter(floor=floor):
            if not p.isFloor():
                self.assertEqual(p.points, reduce(lambda x, y: x + y, [s.price for s in p.stocks.all()]))
        print("Finished! Took {} seconds!".format(time.clock() - start))
    def test_stock_cap_simple(self):
        SMALL_NUMBER = 2
        floor = Floor.objects.all()[0]
        floor.num_stocks = SMALL_NUMBER
        floor.save()
        player = Player.objects.all()[0]
        for i in range(SMALL_NUMBER):
            player.stocks.add(Stock.objects.all()[i])
        player.save()
        with self.assertRaises(TradeError):
            trade = Trade.objects.create(sender=player, floor=floor, recipient=floor.floorPlayer)
            trade.recipientStocks = [Stock.objects.all()[SMALL_NUMBER + 1]]
            trade.verify()
    def test_trade_simple(self):
        floor = Floor.objects.all()[0]
        playerA = Player.objects.filter(floor=floor)[0]
        playerB = Player.objects.filter(floor=floor)[1]
        origAStocks = list(playerA.stocks.all())
        origBStocks = list(playerB.stocks.all())
        trade = Trade.objects.create(floor=floor, sender=playerA, recipient=playerB)
        trade.senderStocks = playerA.stocks.all()
        trade.recipientStocks = playerB.stocks.all()
        trade.save()
        trade.accept()
        self.assertEqual(origAStocks, playerB.stocks.all())
        self.assertEqual(origBStocks, playerA.stocks.all())
