from django.test import TestCase
from stocks.models import *
import json

class ScoringStressTestCase(TestCase):
    def setUp(self):
        with open("./static/stocks.json") as f:
            available_stocks = [Stock.objects.create(symbol=i["symbol"]) for i in json.load(f)]
        floor_user = User.objects.create_user("Floor", "floor@floors.net", "flooring")
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
