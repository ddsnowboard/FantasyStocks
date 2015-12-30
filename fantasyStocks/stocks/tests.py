from django.test import TestCase, Client
from django import test
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
from stocks.models import *
from stocks.views import join_floor
from stocks.forms import TradeForm
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
            stock = available_stocks.pop()
            player.stocks.add(stock)
            user.save()
            player.save()
            floor.stocks.add(stock)
            floor.save()
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
                self.assertAlmostEqual(p.points, reduce(lambda x, y: x + y, [s.get_score() for s in p.stocks.all()]), delta=1)
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
        playerA = [p for p in Player.objects.filter(floor=floor) if not p.isFloor()][0]
        playerB = [p for p in Player.objects.filter(floor=floor) if not p.isFloor()][1]
        origAStocks = list(playerA.stocks.all())
        origBStocks = list(playerB.stocks.all())
        trade = Trade.objects.create(floor=floor, sender=playerA, recipient=playerB)
        trade.senderStocks = playerA.stocks.all()
        trade.recipientStocks = playerB.stocks.all()
        trade.save()
        trade.accept()
        self.assertEqual(list(playerB.stocks.all()), origAStocks)
        self.assertEqual(list(playerA.stocks.all()), origBStocks)
    def test_private_floor(self):
        floor = Floor.objects.all()[0]
        floor.public = False
        floor.save()
        client = Client()
        user = User.objects.create_user("privateFloorUser", "privateer@mailmail.mail", "thePasswordIs")
        client.force_login(user)
        response = client.get(reverse("joinFloor"))
        # This has to be number 2 because there are three templates: base (0), loggedIn (1), and joinFloor (2). 
        self.assertListEqual(response.context[2]["floors"], [])
        floor.public = True
        floor.save()
        response = client.get(reverse("joinFloor"))
        self.assertListEqual(response.context[2]["floors"], [floor])
    def test_suggestions(self):
        floor = Floor.objects.all()[0]
        floor.permissiveness = "permissive"
        floor.save()
        player = Player.objects.filter(floor=floor)[0]
        user = player.user
        for i in Stock.objects.all():
            if not i in floor.stocks.all():
                new_stock = i
                break
            else:
                continue
        form = TradeForm({"other_user": floor.floorPlayer.user.username, "other_stocks": new_stock.symbol, "user_stocks": ""})
        if form.is_valid(pkFloor=floor.pk, user=user):
            trade = form.to_trade(pkFloor=floor.pk, user=user)
        else:
            raise RuntimeError("There was an error in validation. {}".format(form.errors))
        # If this fails, the trade isn't getting automatically accepted by the floor. 
        self.assertQuerysetEqual(Trade.objects.all(), [])
        self.assertNotIn(new_stock, player.stocks.all())
        self.assertNotIn(new_stock, floor.stocks.all())
        self.assertNotEqual(StockSuggestion.objects.all(), [])
        self.assertNotIn(new_stock, floor.stocks.all())
        StockSuggestion.objects.filter(stock=new_stock)[0].accept()
        self.assertIn(new_stock, player.stocks.all())
        self.assertIn(new_stock, floor.stocks.all())
