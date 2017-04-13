from django.test import TestCase, Client
from stocksApi.models import SessionId
from stocks.models import *
from json import loads
from django.core.urlresolvers import reverse

USERNAME = "user123"
PASSWORD = "thePasswordIs"

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

    def test_view_simple(self):
        c = Client()
        user = User.objects.first()
        response = c.get(reverse("viewUser", args=(user.pk, )))
        # Make sure that this returns the one user we asked for
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
        session = SessionId.objects.filter(associated_user=player.user).first()
        response = c.get(reverse("viewPlayer")+"?sessionId=" + session.id_string)
        jsonObj = loads(response.content.decode("UTF-8"))
        for i in jsonObj:
            if i["id"] != player.id:
                self.assertFalse(i["sentTrades"])
                self.assertFalse(i["receivedTrades"])
            else:
                self.assertTrue(i["sentTrades"])
                self.assertTrue(i["receivedTrades"])

