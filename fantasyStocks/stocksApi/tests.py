from django.test import TestCase, Client
from stocksApi.models import SessionId
from stocks.models import *
from json import loads

class AuthTests(TestCase):
    fixtures = ["fixture.json"]
    def test_get_session_id(self):
        c = Client()
        username = "user123"
        password = "thePasswordIs"
        user = User.objects.create_user(username, "thisisanaddress@koolaid.church", password)
        response = c.post("/api/v1/auth/getKey", {"username": username, "password": password})
        jsonObj = loads(response.content.decode("utf-8"))
        self.assertEquals(jsonObj["user"]["id"], user.pk)
        ids = SessionId.objects.filter(associated_user=user).order_by("-exp_date")
        self.assertTrue(ids)
        self.assertFalse(ids[0].is_expired())
