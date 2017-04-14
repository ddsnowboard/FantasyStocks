from django.test import TestCase, Client
from django.http import JsonResponse
from stocksApi.models import SessionId
from stocks.models import *
from json import loads
from django.core.urlresolvers import reverse

USERNAME = "user123"
PASSWORD = "thePasswordIs"

def getTrade():
        floor = Floor.objects.all().first()
        player1 = Player.objects.filter(floor=floor).first()
        player2 = Player.objects.filter(floor=floor).last()
        randomTrade = Trade(sender=player1, recipient=player2, floor=floor)
        randomTrade.save()
        randomTrade.senderStocks.add(player1.stocks.all().first())
        randomTrade.recipientStocks.add(player2.stocks.all().first())

        return randomTrade

class AuthTests(TestCase):
    fixtures = ["fixture.json"]

    def makeUser(self):
        retval = User.objects.create_user(USERNAME, "thisisanaddress@koolaid.church", PASSWORD)
        return retval

    def test_get_session_id(self):
        c = Client()
        user = self.makeUser()
        response = c.post("/api/v1/auth/getKey", {"username": USERNAME, "password": PASSWORD})
        jsonObj = loads(response.content.decode("utf-8"))
        self.assertEquals(jsonObj["user"]["id"], user.pk)
        ids = SessionId.objects.filter(associated_user=user).order_by("-exp_date")
        self.assertTrue(ids)
        self.assertFalse(ids[0].is_expired())

class ViewingTests(TestCase):
    fixtures = ["fixture.json"]
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        self.maxDiff = None

    def test_view_simple(self):
        c = Client()
        user = User.objects.first()
        response = c.get(reverse("viewUser", args=(user.pk, )))
        jsonObj = loads(response.content.decode("UTF-8"))
        self.assertEquals(jsonObj, userJSON(user))

    def test_bad_view(self):
        c = Client()
        badPk = User.objects.all().order_by("pk").last().pk + 1
        response = c.get(reverse("viewUser", args=(badPk, )))
        jsonObj = loads(response.content.decode("UTF-8"))
        if not "error" in jsonObj:
            self.fail()

    def test_all_players_blocks_trades(self):
        c = Client()
        response = c.get(reverse("viewAllPlayers"))
        jsonObj = loads(response.content.decode("UTF-8"))
        for i in jsonObj:
            self.assertFalse(i["sentTrades"])
            self.assertFalse(i["receivedTrades"])



        player = Player.objects.all().first()
        session = SessionId(associated_user=player.user)
        session.save()
        response = c.get(reverse("viewAllPlayers")+"?sessionId=" + session.id_string)
        jsonObj = loads(response.content.decode("UTF-8"))
        for i in jsonObj:
            if i["id"] != player.id:
                self.assertFalse(i["sentTrades"])
                self.assertFalse(i["receivedTrades"])
            else:
                self.assertEquals(len(i["sentTrades"]),
                                  Trade.objects.filter(sender=player).count())

                self.assertEquals(len(i["receivedTrades"]),
                                  Trade.objects.filter(recipient=player).count())
    
    def test_one_player_blocks_trades(self):
        c = Client() 
        for p in Player.objects.all():
            session = SessionId(associated_user=p.user)
            session.save()
            response = c.get(reverse("viewPlayer", args=(p.pk, ))+"?sessionId=" + session.id_string)
            self.assertEquals(loads(response.content.decode("UTF-8")), loads(JsonResponse(p.toJSON()).content.decode("UTF-8")))

    def test_no_user_breaks_trade(self):
        c = Client()
        response = c.get(reverse("viewAllTrades"))
        self.assertTrue("error" in response.content.decode("UTF-8"))

        randomTrade = getTrade()
        randomTrade.save()

        response = c.get(reverse("viewTrade", args=(randomTrade.pk, )))
        self.assertTrue("error" in response.content.decode("UTF-8"))

        otherPlayer = Player.objects.all(). \
        exclude(pk=randomTrade.sender.pk). \
        exclude(pk=randomTrade.recipient.pk). \
        filter(floor=randomTrade.floor).first() 

        id = SessionId(associated_user=otherPlayer.user)
        id.save()

        response = c.get(reverse("viewTrade", args=(randomTrade.pk, ))+"?sessionId={}".format(id.id_string))
        self.assertTrue("error" in response.content.decode("UTF-8"))

    def test_only_shows_right_trades(self):
        c = Client()
        trade = getTrade()
        trade.save()
        otherTrade = getTrade()
        otherPlayer = Player.objects.all().exclude(pk=trade.sender.pk).exclude(pk=trade.recipient.pk).filter(floor=trade.floor).first()
        otherTrade.sender = otherPlayer
        otherTrade.senderStocks.clear()
        otherTrade.senderStocks.add(otherPlayer.stocks.all().first())

        playerWithTrade = trade.sender
        sessionId = SessionId(associated_user=playerWithTrade.user)
        sessionId.save()
        response = c.get(reverse("viewAllTrades") + "?sessionId={}".format(sessionId.id_string))
        returnedTrades = [Trade.objects.get(pk=i["id"]) for i in loads(response.content.decode("UTF-8"))]
        for i in returnedTrades:
            self.assertTrue(i.sender == playerWithTrade or i.recipient == playerWithTrade)
