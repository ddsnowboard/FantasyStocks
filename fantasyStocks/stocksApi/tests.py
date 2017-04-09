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
        user = User.objects.all()[0]
        c.get(reverse("viewUser", args=(user.pk, )))
        # Make sure that this returns the one user we asked for
