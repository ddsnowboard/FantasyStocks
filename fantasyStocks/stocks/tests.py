import json
from django.test import TestCase, Client
from django import test
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
from stocks.models import *
from stocks.views import join_floor
from stocks.forms import TradeForm, LoginForm, RegistrationForm
import json
import time
from functools import reduce
import urllib

class TradeTestCase(StaticLiveServerTestCase):
    fixtures = ["fixture.json"]
    def set_trade(self):
        self.floor = Floor.objects.all()[0]
        available_players = [p for p in Player.objects.filter(floor=self.floor) if not p.isFloor()]
        self.sender = available_players[0]
        self.recipient = available_players[1]
        self.sender_stocks = list(self.sender.stocks.all())
        self.recipient_stocks = list(self.recipient.stocks.all())
        self.trade = Trade.objects.create(floor=self.floor, sender=self.sender, recipient=self.recipient)
        self.trade.senderStocks = self.sender.stocks.all()
        self.trade.recipientStocks = self.recipient.stocks.all()
        self.trade.save()
    def test_trade_simple(self):
        self.set_trade()
        self.trade.accept()
        self.assertEqual(list(self.recipient.stocks.all()), self.sender_stocks)
        self.assertEqual(list(self.sender.stocks.all()), self.recipient_stocks)
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
    def test_private_floor(self):
        floor = Floor.objects.all()[0]
        floor.public = False
        floor.save()
        client = Client()
        user = User.objects.create_user("privateFloorUser", "privateer@mailmail.mail", "thePasswordIs")
        client.force_login(user)
        response = client.get(reverse("floorsJson"))
        # This has to be number 2 because there are three templates: base (0), loggedIn (1), and joinFloor (2). 
        self.assertListEqual([Floor.objects.get(name=i["name"]) for i in json.loads(response.content.decode("UTF-8"))], [])
        floor.public = True
        floor.save()
        response = client.get(reverse("floorsJson"))
        self.assertListEqual([Floor.objects.get(name=i["name"]) for i in json.loads(response.content.decode("UTF-8"))], [floor])
    def test_trade_counter(self):
        self.set_trade()
        old_recipientStocks = list(self.trade.recipientStocks.all())
        old_senderStocks = list(self.trade.senderStocks.all())
        client = Client()
        client.force_login(self.recipient.user)
        response = client.get(reverse("receivedTrade", kwargs={"pkTrade": self.trade.pk}))
        self.assertEqual(self.trade.toFormDict(), response.context[-1]["form"].data)
        self.assertContains(response, reverse("counterTrade", kwargs={"pkTrade": self.trade.pk, "pkFloor": self.trade.floor.pk}))
        response = client.get(reverse("counterTrade", kwargs={"pkTrade": self.trade.pk, "pkFloor": self.trade.floor.pk}))
        response = client.post(reverse("trade", kwargs={"pkCountering": self.trade.pk, "pkFloor": self.trade.floor.pk}), {"other_user": self.trade.sender.user.username, "user_stocks": ",".join(i.symbol for i in self.trade.recipientStocks.all()), "other_stocks": ",".join(i.symbol for i in self.trade.senderStocks.all())})
        self.assertRedirects(response, reverse("dashboard"))
        self.assertQuerysetEqual(Trade.objects.filter(pk=self.trade.pk), [])
        newTrade = Trade.objects.all()[0]
        self.assertEqual(list(newTrade.senderStocks.all()), old_recipientStocks)
        self.assertEqual(list(newTrade.recipientStocks.all()), old_senderStocks)

class PlayerTestCase(StaticLiveServerTestCase):
    fixtures = ["fixture.json"]
    def test_join_empty_floor(self):
        floor = Floor.objects.all()[0]
        user = User.objects.all().exclude(username="Floor")[0]
        player = Player.objects.get(user=user, floor=floor)
        client = Client()
        client.force_login(user)
        for i in [f for f in Floor.objects.all() if not f in [p for p in Player.objects.filter(user=user)]]:
            client.get(reverse("join", args=[i.pk]))

        response = client.get(reverse("joinFloor"))
        self.assertFalse(response.context[-1]["floors_exist"])
        Player.objects.filter(user=user).delete()
        response = client.get(reverse("joinFloor"))
        self.assertTrue(response.context[-1]["floors_exist"])
    def test_scoring(self):
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
class SuggestionTestCase(StaticLiveServerTestCase):
    fixtures = ["fixture.json"]
    def setUp(self):
        self.floor = Floor.objects.all()[0]
        self.floor.permissiveness = "permissive"
        self.floor.save()
        self.player = [p for p in Player.objects.filter(floor=self.floor) if not p.isFloor()][0]
        self.user = self.player.user
        for i in Stock.objects.all():
            if not i in self.floor.stocks.all():
                self.new_stock = i
                break
            else:
                continue
        self.form = TradeForm({"other_user": self.floor.floorPlayer.user.username, "other_stocks": self.new_stock.symbol, "user_stocks": ""})
        if self.form.is_valid(pkFloor=self.floor.pk, user=self.user):
            self.trade = self.form.to_trade(pkFloor=self.floor.pk, user=self.user)
        else:
            raise RuntimeError("There was an error in validation. {}".format(form.errors))
    def test_suggestions(self):
        # If this fails, the trade isn't getting automatically accepted by the floor. 
        self.assertQuerysetEqual(Trade.objects.all(), [])
        self.assertNotIn(self.new_stock, self.player.stocks.all())
        self.assertNotIn(self.new_stock, self.floor.stocks.all())
        self.assertNotEqual(StockSuggestion.objects.all(), [])
        self.assertNotIn(self.new_stock, self.floor.stocks.all())
        StockSuggestion.objects.filter(stock=self.new_stock)[0].accept()
        self.assertIn(self.new_stock, self.player.stocks.all())
        self.assertIn(self.new_stock, self.floor.stocks.all())
    def test_capped_suggestion(self):
        SMALL_NUMBER = 2
        self.floor.num_stocks = SMALL_NUMBER
        self.floor.save()
        suggestion = StockSuggestion.objects.all()[0]
        for i in Player.objects.all():
            if i != self.player and not i.isFloor():
                otherPlayer = i
                break
            else:
                continue
        newTrade = Trade.objects.create(recipient=otherPlayer, floor=self.floor, sender=self.player)
        newStock = otherPlayer.stocks.all()[0]
        newTrade.recipientStocks.add(newStock)
        newTrade.save()
        newTrade.verify()
        newTrade.accept()
        self.assertEqual(list(otherPlayer.stocks.all()), [])
        self.assertIn(newStock, self.player.stocks.all())
        self.assertEqual(self.player.stocks.count(), SMALL_NUMBER)
        suggestion.accept()
        self.assertNotIn(self.new_stock, self.player.stocks.all())
        self.assertIn(self.new_stock, self.floor.stocks.all())
        self.assertIn(self.new_stock, self.floor.floorPlayer.stocks.all())

class UserTestCase(StaticLiveServerTestCase):
    fixtures = ["fixture.json"]
    def test_login_page(self):
        user = User.objects.all().exclude(username="Floor")[0]
        client = Client()
        origResponse = client.get(reverse("dashboard"), follow=True)
        self.assertTemplateUsed(origResponse, "index.html")
        self.assertTrue(origResponse.context[-1]["registrationForm"])
        self.assertTrue(origResponse.context[-1]["loginForm"])
        response = client.post(origResponse.redirect_chain[-1][0], {"username": "notAusername", "password": "certainlynotapassword", "nextPage": reverse("dashboard")})
        self.assertFormError(response, "loginForm", None, "That username does not exist") 

        response = client.get(reverse("dashboard"), follow=True)
        response = client.post(origResponse.redirect_chain[-1][0], {"username": user.username, "password": "certainlynotapassword", "nextPage": reverse("dashboard")})
        self.assertFormError(response, "loginForm", None, "That is the wrong password") 

        response = client.get(reverse("dashboard"), follow=True)
        # See the code I used to create the fixture for how I'm getting the password
        response = client.post(origResponse.redirect_chain[-1][0], {"username": user.username, "password": "thePasswordIs{}".format(user.username.split("_")[1]), "nextPage": reverse("dashboard")}, follow=True)
        self.assertEqual(response.redirect_chain[-1][0], reverse("dashboard")) 





# This is stuff I don't need anymore. If I need to change the standard database
# setup, I might though. 
# class OldTests(StaticLiveServerTestCase):
#   def test_serialize(self):
#       from django.core.serializers import serialize
#       l = []
#       for i in [Stock, User, Group, Floor, Player]:
#           l += list(i.objects.all())
#       with open("fixture", "w") as w:
#           w.write(serialize("json", l))
#   def setUp(self):
#      NUMBER_OF_USERS = 100
#      with urllib.request.urlopen(self.live_server_url + static("stocks.json")) as f:
#          available_stocks = [Stock.objects.create(symbol=i["symbol"]) for i in json.loads(f.read().decode("UTF-8"))]
#      floor_user = User.objects.create_user("Floor", "floor@floors.net", "flooring")
#      floor_group = Group.objects.create(name="Floor")
#      floor_group.save()
#      floor_user.groups.add(floor_group)
#      floor_user.save()
#      floor = Floor.objects.create(name="TestingFloor", permissiveness="open")
#      floor_player = Player.objects.create(user=floor_user, points=0, floor=floor)
#      floor.floorPlayer = floor_player
#      floor_player.save()
#      floor.save()
#      print("start creating users")
#      for i in range(NUMBER_OF_USERS):
#          user = User.objects.create_user("user_{}".format(i), "user_{}@mailmail.mail".format(i), "thePasswordIs{}".format(i))
#          player = Player.objects.create(user=user, floor=floor)
#          stock = available_stocks.pop()
#          player.stocks.add(stock)
#          user.save()
#          player.save()
#          floor.stocks.add(stock)
#          floor.save()
#      print("done creating users")
