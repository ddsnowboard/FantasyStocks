from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.staticfiles.templatetags.staticfiles import static
from stocks.models import *
import json
import time
from functools import reduce
import urllib

class ScoringStressTestCase(StaticLiveServerTestCase):
    def setUp(self):
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
        for i in range(1000):
            user = User.objects.create_user("user_{}".format(i), "user_{}@mailmail.mail".format(i), "thePasswordIs{}".format(i))
            player = Player.objects.create(user=user, floor=floor)
            player.stocks.add(available_stocks.pop())
            user.save()
            player.save()
    def test_players_get_scores(self):
        start = time.clock()
        floor = Floor.objects.all()[0]
        DEFAULT_PRICE = 5
        for s in floor.stocks.all():
            s.price = DEFAULT_PRICE
            s.update()
        for p in Player.objects.filter(floor=floor):
            if not p.isFloor():
                self.assertEqual(p.points, reduce(lambda x, y: x + y, [s.price for s in p.stocks.all()]))
        print("Took {} seconds!".format(time.clock() - start))
