from datetime import datetime
from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from stocksApi.models import SessionId, AndroidToken
from stocks.models import *
from json import loads, dumps
from django.core.urlresolvers import reverse
from stocksApi.views import tradeInvolvesUser
from concurrent.futures import ThreadPoolExecutor

def createStocks(n):
    # Create a bunch of stocks and return them
    GOOD_STOCKS = ["MMM", "ABT", "ABBV", "ACN", "ATVI", "AYI", "ADBE", "AMD", "AAP", "AES", "AET", "AMG", "AFL", "A", "APD", "AKAM", "ALK", "ALB", "ARE", "ALXN", "ALGN", "ALLE", "AGN", "ADS", "LNT", "ALL", "GOOGL", "GOOG", "MO", "AMZN", "AEE", "AAL", "AEP", "AXP", "AIG", "AMT", "AWK", "AMP", "ABC", "AME", "AMGN", "APH", "APC", "ADI", "ANDV", "ANSS", "ANTM", "AON", "AOS", "APA", "AIV", "AAPL", "AMAT", "APTV", "ADM", "ARNC", "AJG", "AIZ", "T", "ADSK", "ADP", "AZO", "AVB", "AVY", "BHGE", "BLL", "BAC", "BK", "BCR", "BAX", "BBT", "BDX", "BBY", "BIIB", "BLK", "HRB", "BA", "BWA", "BXP", "BSX", "BHF", "BMY", "AVGO", "CHRW", "CA", "COG", "CDNS", "CPB", "COF", "CAH", "CBOE", "KMX", "CCL", "CAT", "CBG", "CBS", "CELG", "CNC", "CNP", "CTL", "CERN", "CF", "SCHW", "CHTR", "CHK", "CVX", "CMG", "CB", "CHD", "CI", "XEC", "CINF", "CTAS", "CSCO", "C", "CFG", "CTXS", "CLX", "CME", "CMS", "KO", "CTSH", "CL", "CMCSA", "CMA", "CAG", "CXO", "COP", "ED", "STZ", "COO", "GLW", "COST", "COTY", "CCI", "CSRA", "CSX", "CMI", "CVS", "DHI", "DHR", "DRI", "DVA", "DE", "DAL", "XRAY", "DVN", "DLR", "DFS", "DISCA", "DISCK", "DISH", "DG", "DLTR", "D", "DOV", "DWDP", "DPS", "DTE", "DRE", "DUK", "DXC", "ETFC", "EMN", "ETN", "EBAY", "ECL", "EIX", "EW", "EA", "EMR", "ETR", "EVHC", "EOG", "EQT", "EFX", "EQIX", "EQR", "ESS", "EL", "ES", "RE", "EXC", "EXPE", "EXPD", "ESRX", "EXR", "XOM", "FFIV", "FB", "FAST", "FRT", "FDX", "FIS", "FITB", "FE", "FISV", "FLIR", "FLS", "FLR", "FMC", "FL", "F", "FTV", "FBHS", "BEN", "FCX", "GPS", "GRMN", "IT", "GD", "GE", "GGP", "GIS", "GM", "GPC", "GILD", "GPN", "GS", "GT", "GWW", "HAL", "HBI", "HOG", "HRS", "HIG", "HAS", "HCA", "HCP", "HP", "HSIC", "HSY", "HES", "HPE", "HLT", "HOLX", "HD", "HON", "HRL", "HST", "HPQ", "HUM", "HBAN", "IDXX", "INFO", "ITW", "ILMN", "IR", "INTC", "ICE", "IBM", "INCY", "IP", "IPG", "IFF", "INTU", "ISRG", "IVZ", "IQV", "IRM", "JEC", "JBHT", "SJM", "JNJ", "JCI", "JPM", "JNPR", "KSU", "K", "KEY", "KMB", "KIM", "KMI", "KLAC", "KSS", "KHC", "KR", "LB", "LLL", "LH", "LRCX", "LEG", "LEN", "LUK", "LLY", "LNC", "LKQ", "LMT", "L", "LOW", "LYB", "MTB", "MAC", "M", "MRO", "MPC", "MAR", "MMC", "MLM", "MAS", "MA", "MAT", "MKC", "MCD", "MCK", "MDT", "MRK", "MET", "MTD", "MGM", "KORS", "MCHP", "MU", "MSFT", "MAA", "MHK", "TAP", "MDLZ", "MON", "MNST", "MCO", "MS", "MOS", "MSI", "MYL", "NDAQ", "NOV", "NAVI", "NTAP", "NFLX", "NWL", "NFX", "NEM", "NWSA", "NWS", "NEE", "NLSN", "NKE", "NI", "NBL", "JWN", "NSC", "NTRS", "NOC", "NCLH", "NRG", "NUE", "NVDA", "ORLY", "OXY", "OMC", "OKE", "ORCL", "PCAR", "PKG", "PH", "PDCO", "PAYX", "PYPL", "PNR", "PBCT", "PEP", "PKI", "PRGO", "PFE", "PCG", "PM", "PSX", "PNW", "PXD", "PNC", "RL", "PPG", "PPL", "PX", "PCLN", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PSA", "PHM", "PVH", "QRVO", "PWR", "QCOM", "DGX", "RRC", "RJF", "RTN", "O", "RHT", "REG", "REGN", "RF", "RSG", "RMD", "RHI", "ROK", "COL", "ROP", "ROST", "RCL", "CRM", "SBAC", "SCG", "SLB", "SNI", "STX", "SEE", "SRE", "SHW", "SIG", "SPG", "SWKS", "SLG", "SNA", "SO", "LUV", "SPGI", "SWK", "SBUX", "STT", "SRCL", "SYK", "STI", "SYMC", "SYF", "SNPS", "SYY", "TROW", "TPR", "TGT", "TEL", "FTI", "TXN", "TXT", "TMO", "TIF", "TWX", "TJX", "TMK", "TSS", "TSCO", "TDG", "TRV", "TRIP", "FOXA", "FOX", "TSN", "UDR", "ULTA", "USB", "UA", "UAA", "UNP", "UAL", "UNH", "UPS", "URI", "UTX", "UHS", "UNM", "VFC", "VLO", "VAR", "VTR", "VRSN", "VRSK", "VZ", "VRTX", "VIAB", "V", "VNO", "VMC", "WMT", "WBA", "DIS", "WM", "WAT", "WEC", "WFC", "HCN", "WDC", "WU", "WRK", "WY", "WHR", "WMB", "WLTW", "WYN", "WYNN", "XEL", "XRX", "XLNX", "XL", "XYL", "YUM", "ZBH", "ZION", "ZTS"]
    if n > len(GOOD_STOCKS):
        raise Exception("You can't have {} stocks".format(n))

    out = [Stock(symbol=sym) for sym in GOOD_STOCKS[:n]]
    # I thought this would be unnecessary, but I was wrong 
    for s in out: 
        s.save()

    with ThreadPoolExecutor() as pool:
        pool.map(lambda x: x.force_update(), out)

    return out

def createFloorUser():
    floorUser = User.objects.create_user("Floor")
    floorGroup, _ = Group.objects.get_or_create(name="Floor")
    floorUser.groups.add(floorGroup)
    floorUser.save()
    return floorUser

def createUsers(n):
    floorUser = createFloorUser()
    otherUsers = [User.objects.create_user("user{}".format(i)) for i in range(n)]
    map(lambda x: x.save(), otherUsers)
    return otherUsers

def createTrade(floor):
    USERNAME = "username"
    players = [p for p in Player.objects.all() if not p.isFloor()]
    player1 = players[0]
    player2 = players[1]
    assert player1 != player2
    randomTrade = Trade(sender=player1, recipient=player2, floor=floor)
    randomTrade.save()

    print(player1)
    randomTrade.senderStocks.add(player1.stocks.all().first())
    randomTrade.recipientStocks.add(player2.stocks.all().first())
    return randomTrade

def reverseWithSession(name, sessionId, **kwargs):
    url = reverse(name, **kwargs)
    return url + "?sessionId={}".format(sessionId.id_string)

def makeUser(username):
    PASSWORD = "apples"
    retval = User.objects.create_user(username, "thisisanaddress@koolaid.church", PASSWORD)
    retval.save()
    return retval

def createFloor(owner):
    def randomString(length):
        from random import choice
        import string
        s = ""
        for _ in range(length):
            s += choice(string.ascii_letters)
        return s

    LENGTH = 5
    testFloor = Floor(name="TestFloor" + randomString(LENGTH))
    testFloor.permissiveness = Floor.OPEN
    testFloor.owner = owner
    testFloor.save()
    return testFloor

def setUpClass(cls):
    N = 10
    cls.otherUsers = createUsers(N)
    cls.testFloor = createFloor(cls.otherUsers[0])
    cls.testUser = cls.otherUsers[0]
    # I don't want to end up with a user in the list twice, as it were
    cls.otherUsers = cls.otherUsers[1:]
    # We don't need to save this since we can trivially get the players back whenever we want
    players = list(map(lambda u: Player(user=u, floor=cls.testFloor), cls.otherUsers))
    for p in players:
        p.save()
    cls.stocks = createStocks(N)
    cls.testFloor.stocks.add(*cls.stocks)
    cls.testFloor.save()
    assignStocks(players, cls.stocks)

def assignStocks(players, stocks):
    from itertools import cycle
    playerCycle = cycle(players)

    for p, s in zip(playerCycle, stocks):
        p.stocks.add(s)

    for p in players:
        p.save()


class AuthTests(TestCase):

    def test_get_session_id(self):
        c = Client()
        user = makeUser()
        response = c.post("/api/v1/auth/getKey", dumps({"username": USERNAME, "password": PASSWORD}), content_type="application/json")
        jsonObj = loads(response.content.decode("utf-8"))
        self.assertEquals(jsonObj["user"]["id"], user.pk)
        ids = SessionId.objects.filter(associated_user=user).order_by("-exp_date")
        self.assertTrue(ids)
        self.assertFalse(ids[0].is_expired())

class ViewingTests(TestCase):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        self.maxDiff = None

    @classmethod
    def setUpTestData(cls):
        setUpClass(cls)

    def test_view_simple(self):
        USERNAME = "melvyn"
        c = Client()
        user = makeUser(USERNAME)

        response = c.get(reverse("viewUser", args=(user.pk, )))
        jsonObj = loads(response.content.decode("UTF-8"))
        self.assertEquals(jsonObj, userJSON(user))

    def test_bad_view(self):
        c = Client()
        user1 = makeUser("melvyn")
        badPk = user1.pk + 1
        response = c.get(reverse("viewUser", args=(badPk, )))
        jsonObj = loads(response.content.decode("UTF-8"))
        if not "error" in jsonObj:
            self.fail()

    def test_all_players_blocks_trades(self):
        c = Client()
        player1 = Player.objects.get(user=self.otherUsers[0])
        player2 = Player.objects.get(user=self.otherUsers[1])

        trade = createTrade(self.testFloor)
        response = c.get(reverse("viewAllPlayers"))
        jsonObj = loads(response.content.decode("UTF-8"))
        for i in jsonObj:
            self.assertFalse(i["sentTrades"])
            self.assertFalse(i["receivedTrades"])


        session = SessionId(associated_user=player1.user)
        session.save()

        response = c.get(reverseWithSession("viewAllPlayers", session))
        jsonObj = loads(response.content.decode("UTF-8"))

        # Make sure the user can see trades for himself and himself only
        for i in jsonObj:
            if i["id"] != player.id:
                self.assertFalse([i for i in i["sentTrades"] if not tradeInvolvesUser(Trade.objects.get(pk=i["id"]), player.user)])
                self.assertFalse([i for i in i["receivedTrades"] if not tradeInvolvesUser(Trade.objects.get(pk=i["id"]), player.user)])

                self.assertEquals([i for i in i["sentTrades"] if tradeInvolvesUser(Trade.objects.get(pk=i["id"]), player.user)], i["sentTrades"])
                self.assertEquals([i for i in i["receivedTrades"] if tradeInvolvesUser(Trade.objects.get(pk=i["id"]), player.user)], i["receivedTrades"])
            else:
                self.assertEquals(len(i["sentTrades"]),
                                  Trade.objects.filter(sender=player).count())

                self.assertEquals(len(i["receivedTrades"]),
                                  Trade.objects.filter(recipient=player).count())
    
    def test_view_one_player(self):
        c = Client() 
        trade = createTrade(self.testFloor)
        for p in Player.objects.all():
            session = SessionId(associated_user=p.user)
            session.save()
            response = c.get(reverseWithSession("viewPlayer", session, args=(p.pk, )))
            self.assertEquals(loads(response.content.decode("UTF-8")), loads(JsonResponse(p.toJSON()).content.decode("UTF-8")))

    def test_no_user_breaks_trade(self):
        """
        Make sure than an unauthenticated user can't read trades
        """

        c = Client()
        response = c.get(reverse("viewAllTrades"))
        self.assertTrue("error" in response.content.decode("UTF-8"))

        randomTrade = createTrade(self.testFloor)
        randomTrade.save()

        response = c.get(reverse("viewTrade", args=(randomTrade.pk, )))
        self.assertTrue("error" in response.content.decode("UTF-8"))

        otherPlayer = Player.objects.all(). \
            exclude(pk=randomTrade.sender.pk). \
            exclude(pk=randomTrade.recipient.pk). \
            filter(floor=randomTrade.floor).first() 

        id = SessionId(associated_user=otherPlayer.user)
        id.save()

        response = c.get(reverseWithSession("viewTrade", id, args=(randomTrade.pk, )))
        self.assertTrue("error" in response.content.decode("UTF-8"))

    def test_only_shows_right_trades(self):
        c = Client()
        trade = createTrade(self.testFloor)
        trade.save()
        otherTrade = createTrade()
        otherPlayer = Player.objects.all().exclude(pk=trade.sender.pk).exclude(pk=trade.recipient.pk).filter(floor=trade.floor).first()
        otherTrade.sender = otherPlayer
        otherTrade.senderStocks.clear()
        otherTrade.senderStocks.add(otherPlayer.stocks.all().first())

        playerWithTrade = trade.sender
        sessionId = SessionId(associated_user=playerWithTrade.user)
        sessionId.save()
        response = c.get(reverseWithSession("viewAllTrades", sessionId))
        returnedTrades = [Trade.objects.get(pk=i["id"]) for i in loads(response.content.decode("UTF-8"))]
        for i in returnedTrades:
            self.assertTrue(i.sender == playerWithTrade or i.recipient == playerWithTrade)

    def test_stock_suggestions_only_shows_to_owner(self):
        c = Client()
        response = c.get(reverse("viewAllStockSuggestions"))
        self.assertTrue("error" in response.content.decode("UTF-8"))

        permissiveFloor = self.testFloor
        permissiveFloor.permissiveness = "permissive"
        permissiveFloor.save()
        owner = permissiveFloor.owner
        newStock = Stock(symbol="SF")
        newStock.save()
        goodSuggestion = StockSuggestion(stock=newStock, 
                                         floor=self.testFloor,
                                         requesting_player=Player.objects.filter(floor=self.testFloor).exclude(user=owner).first())
        goodSuggestion.save()
        goodSessionId = SessionId(associated_user=owner)
        goodSessionId.save()

        badUser = User.objects.create_user(username="testTest", password="Thisisnotapassword")
        badSessionId = SessionId(associated_user=badUser)
        badSessionId.save()

        response = c.get(reverseWithSession("viewStockSuggestion", badSessionId, args=(goodSuggestion.pk, )))
        self.assertTrue("error" in response.content.decode("UTF-8"))

        response = c.get(reverseWithSession("viewStockSuggestion", goodSessionId, args=(goodSuggestion.pk, )))
        self.assertEquals(loads(response.content.decode("UTF-8")), loads(JsonResponse(goodSuggestion.toJSON()).content.decode("UTF-8")))

    def test_hides_private_floors(self):
        c = Client()
        user = User.objects.all().first()
        privateFloor = Floor(name="hiddenFloor", permissiveness="open", owner=user, public=False)
        privateFloor.save()
        response = c.get(reverse("viewAllFloors"))
        floors = map(lambda x: Floor.objects.get(pk=x["id"]), loads(response.content.decode("UTF-8")))
        for f in floors: 
            self.assertTrue(f.public)
        # Test shows private floors that user is on
        sessionId = SessionId(associated_user=user)
        sessionId.save()
        response = c.get(reverseWithSession("viewAllFloors", sessionId))
        self.assertTrue(privateFloor.pk in [f["id"] for f in loads(response.content.decode("UTF-8"))])

    def test_players_shows_floor_player(self):
        c = Client()
        floor = Floor.objects.all().first()
        for p in Player.objects.filter(floor=floor):
            response = c.get(reverse("viewPlayer", args=(p.pk, )))
            if loads(response.content.decode("UTF-8"))["isFloor"]:
                return
        self.fail()

class CreationTests(TestCase):
    fixtures = ["fixture.json"]
    def test_create_user(self):
        c = Client()
        email = "test@test.net"
        password = "thisisapassword"
        username = "test"
        data = {}
        data["email"] = email
        data["password"] = password
        data["username"] = username

        response = c.post(reverse("createUser"), dumps(data), content_type="application/json")

        try:
            newUser = User.objects.get(email=email)
        except ObjectDoesNotExist:
            self.assertTrue(False)

        self.assertEquals(loads(response.content.decode("UTF-8")), loads(JsonResponse(userJSON(newUser)).content.decode("UTF-8")))

    def test_bad_create_user(self):
        email = "test@test.net"
        password = "thisisapassword"
        username = "test"
        c = Client()
        data = {}

        # Test demands username
        data["email"] = email
        data["password"] = password
        response = c.post(reverse("createUser"), dumps(data), content_type="applcation/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        data["username"] = User.objects.all().first().username

        response = c.post(reverse("createUser"), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

    def test_create_player(self):
        c = Client()
        username = "username"
        password = "password"
        u = User.objects.create_user(username=username, password=password)
        sessionId = SessionId(associated_user=u)
        sessionId.save()

        data = {}
        floor = Floor.objects.all().first()
        data["user"] = u.pk
        data["floor"] = floor.pk
        response = c.post(reverseWithSession("createPlayer", sessionId), dumps(data), content_type="application/json")

        returnedPlayer = Player.objects.get(floor=floor, user=u)
        self.assertEquals(loads(response.content.decode("UTF-8")), loads(JsonResponse(returnedPlayer.toJSON(), safe=False).content.decode("UTF-8")))

    def test_bad_create_player(self):
        c = Client()
        username = "username"
        password = "password"
        u = User.objects.create_user(username=username, password=password)
        sessionId = SessionId(associated_user=u)
        sessionId.save()

        data = {}
        floor = Floor.objects.all().first()
        data["user"] = u.pk
        data["floor"] = floor.pk
        
        # Test no session
        response = c.post(reverse("createPlayer"), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Test wrong session
        otherUser = User.objects.create_user(username=username + "1", password=password)
        otherSessionId = SessionId(associated_user=otherUser)
        response = c.post(reverseWithSession("createPlayer", otherSessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Test data that it shouldn't get
        data["points"] = 52
        response = c.post(reverseWithSession("createPlayer", sessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))
        del data["points"]

        # Test creating player that already exists on floor
        player = Player(floor=floor, user=u)
        player.save()
        response = c.post(reverseWithSession("createPlayer", sessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))
        player.delete()

        # Test missing data
        del data["user"]
        response = c.post(reverseWithSession("createPlayer", sessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

    def test_create_trade(self):
        c = Client()
        username = "username"
        password = "password"
        u = User.objects.create_user(username=username, password=password)
        sessionId = SessionId(associated_user=u)
        sessionId.save()

        floor = Floor.objects.all().first()

        player1 = Player(user=u, floor=floor)
        player1.save()
        stocksToReturn = list(player1.stocks.all())

        player2 = Player.objects.filter(floor=floor).exclude(user=u).first()
        stocksToSend = list(player2.stocks.all())

        data = {}
        data["senderPlayer"] = player1.pk
        data["senderStocks"] = tuple(map(lambda x: x.pk, stocksToReturn))

        data["recipientPlayer"] = player2.pk
        data["recipientStocks"] = tuple(map(lambda x: x.pk, stocksToSend))

        data["floor"] = floor.pk

        response = c.post(reverseWithSession("createTrade", sessionId), dumps(data), content_type="application/json")
        jsonObj = loads(response.content.decode("UTF-8"))
        returnedTrade = Trade.objects.get(pk=jsonObj["id"])
        self.assertEquals(jsonObj, loads(JsonResponse(returnedTrade.toJSON(), safe=False).content.decode("UTF-8")))

    def test_bad_create_trade(self):
        c = Client()
        username = "username"
        password = "password"
        u = User.objects.create_user(username=username, password=password)
        sessionId = SessionId(associated_user=u)
        sessionId.save()

        # Creating an ideal data dict
        floor = Floor.objects.all().first()

        player1 = Player(user=u, floor=floor)
        player1.save()
        stocksToReturn = list(player1.stocks.all())

        player2 = Player.objects.filter(floor=floor).exclude(user=u).first()
        stocksToSend = list(player2.stocks.all())

        idealData = {}
        idealData["senderPlayer"] = player1.pk
        idealData["senderStocks"] = tuple(map(lambda x: x.pk, stocksToReturn))

        idealData["recipientPlayer"] = player2.pk
        idealData["recipientStocks"] = tuple(map(lambda x: x.pk, stocksToSend))

        idealData["floor"] = floor.pk

        # Make sure the right data works
        response = c.post(reverseWithSession("createTrade", sessionId), dumps(idealData), content_type="application/json")
        jsonObj = loads(response.content.decode("UTF-8"))
        try:
            t = Trade.objects.get(pk=jsonObj["id"])
            t.delete()
        except ObjectDoesNotExist:
            self.assertTrue(False)

        # No sessionId
        response = c.post(reverse("createTrade"), dumps(idealData), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Wrong sessionId
        badUser = User.objects.create_user(username=username + "2", password=password)
        badSession = SessionId(associated_user=badUser)
        badSession.save()
        response = c.post(reverseWithSession("createTrade", badSession), dumps(idealData), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Missing data
        questionableData = idealData.copy()
        del questionableData["senderPlayer"]
        response = c.post(reverseWithSession("createTrade", badSession), dumps(idealData), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Bad stocks
        questionableData = idealData.copy()
        questionableData["senderStocks"] = []
        questionableData["recipientStocks"] = []
        response = c.post(reverseWithSession("createTrade", badSession), dumps(idealData), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))


        questionableData = idealData.copy()
        questionableData["senderStocks"], questionableData["recipientStocks"] = questionableData["recipientStocks"], questionableData["senderStocks"]
        response = c.post(reverseWithSession("createTrade", badSession), dumps(idealData), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Send date
        questionableData = idealData.copy()
        questionableData["date"] = datetime.utcnow().isoformat()
        response = c.post(reverseWithSession("createTrade", badSession), dumps(idealData), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

    def test_create_floor(self):
        c = Client()
        username = "username"
        password = "password"
        u = User.objects.create_user(username=username, password=password)
        sessionId = SessionId(associated_user=u)
        sessionId.save()

        floorName = "Four on the Floor"
        data = {}
        data["name"] = floorName
        data["permissiveness"] = "Permissive"
        data["owner"] = u.pk
        data["public"] = True
        data["numStocks"] = 10
        data["stocks"] = [s.pk for s in Stock.objects.all()[:15]]

        response = c.post(reverseWithSession("ApiCreateFloor", sessionId), dumps(data), content_type="application/json")

        jsonObj = loads(response.content.decode("UTF-8"))
        newFloor = Floor.objects.get(pk=jsonObj["id"])
        self.assertEquals(floorName, newFloor.name)
        self.assertEquals(data["permissiveness"] , newFloor.permissiveness)
        self.assertEquals(data["owner"] , newFloor.owner.pk)

        self.assertDictEqual({i: True for i in map(lambda x: Stock.objects.get(pk=x), data["stocks"])}, {i: True for i in newFloor.stocks.all()})

    def test_bad_create_floor(self):
        c = Client()
        username = "username"
        password = "password"
        u = User.objects.create_user(username=username, password=password)
        sessionId = SessionId(associated_user=u)
        sessionId.save()

        floorName = "Four on the Floor"
        idealData = {}
        idealData["name"] = floorName
        idealData["permissiveness"] = "Permissive"
        idealData["owner"] = u.pk
        idealData["public"] = True
        idealData["numStocks"] = 10
        idealData["stocks"] = [s.pk for s in Stock.objects.all()[:15]]

        # Test empty stocks on closed floor
        data = idealData.copy()
        data["permissiveness"] = "Closed"
        data["stocks"] = []
        response = c.post(reverseWithSession("ApiCreateFloor", sessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # User tries to create floor as someone else
        data = idealData.copy()
        data["owner"] = User.objects.all().exclude(pk=u.pk).first().pk
        response = c.post(reverseWithSession("ApiCreateFloor", sessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Miss stuff
        data = idealData.copy()
        del data["numStocks"]
        response = c.post(reverseWithSession("ApiCreateFloor", sessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Pass a floorPlayer
        floorPlayer = Player(user=u, floor=Floor.objects.all().first())
        floorPlayer.save()
        data = idealData.copy()
        data["floorPlayer"] = floorPlayer.pk

        response = c.post(reverseWithSession("ApiCreateFloor", sessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

    def test_create_suggestion(self):
        c = Client()
        u = User.objects.create_user(username=USERNAME, password=PASSWORD)
        sessionId = SessionId(associated_user=u)
        sessionId.save()

        randomFloor = Floor.objects.filter(permissiveness="permissive").first()
        stockToSuggest = Stock.objects.all().exclude(pk__in=map(lambda s: s.pk, randomFloor.stocks.all())).first()
        player = Player(floor=randomFloor, user=u)
        player.save()

        data = {}
        data["stock"] = stockToSuggest.pk
        data["requestingPlayer"] = player.pk
        data["floor"] = randomFloor.pk
        response = c.post(reverseWithSession("createStockSuggestion", sessionId), dumps(data), content_type="application/json")
        jsonObj = loads(response.content.decode("UTF-8"))
        newSuggestion = StockSuggestion.objects.get(pk=jsonObj["id"])
        self.assertEquals(newSuggestion.stock, stockToSuggest)
        self.assertEquals(newSuggestion.requesting_player, player)
        self.assertEquals(newSuggestion.floor, randomFloor)

    def test_bad_create_suggestion(self):
        c = Client()
        u = User.objects.create_user(username=USERNAME, password=PASSWORD)
        sessionId = SessionId(associated_user=u)
        sessionId.save()

        randomFloor = Floor.objects.filter(permissiveness="permissive").first()
        stockToSuggest = Stock.objects.all().exclude(pk__in=map(lambda s: s.pk, randomFloor.stocks.all())).first()
        player = Player(floor=randomFloor, user=u)
        player.save()

        idealData = {}
        idealData["stock"] = stockToSuggest.pk
        idealData["requestingPlayer"] = player.pk
        idealData["floor"] = randomFloor.pk

        # Test missing data
        data = idealData.copy()
        del data["stock"]
        response = c.post(reverseWithSession("createStockSuggestion", sessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Test wrong sessionId
        data = idealData.copy()
        badUser = Player.objects.filter(floor=randomFloor).exclude(pk=player.pk).first().user
        badSession = SessionId(associated_user=badUser)
        badSession.save()
        response = c.post(reverseWithSession("createStockSuggestion", badSession), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Test wrong floor
        data = idealData.copy()
        requestingPlayer = Player.objects.all().exclude(floor=randomFloor).first()
        data["requestingPlayer"] = requestingPlayer.pk
        otherSession = SessionId(associated_user=requestingPlayer.user)
        otherSession.save()
        response = c.post(reverseWithSession("createStockSuggestion", otherSession), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Test stock already on floor
        data = idealData.copy()
        badStock = randomFloor.stocks.all().first()
        data["stock"] = badStock.pk
        response = c.post(reverseWithSession("createStockSuggestion", sessionId), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Test not permissive floor
        data = idealData.copy()
        badFloor = Floor.objects.all().exclude(permissiveness="permissive").first()
        p = Player.objects.filter(floor=badFloor).first()
        s = Stock.objects.all().exclude(pk__in=map(lambda s: s.pk, p.floor.stocks.all())).first()
        data["floor"] = badFloor.pk
        data["requestingPlayer"] = p.pk
        data["stock"] = s.pk
        response = c.post(reverseWithSession("createStockSuggestion", badSession), dumps(data), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

    def test_accept_trade(self):
        trade = createTrade()
        sender = trade.sender
        recipient = trade.recipient
        originalSenderStocks = list(sender.stocks.all())
        originalRecipientStocks = list(recipient.stocks.all())
        trade.senderStocks = originalSenderStocks
        trade.recipientStocks = originalRecipientStocks
        trade.save()

        sessionId = SessionId(associated_user=recipient.user)
        sessionId.save()

        c = Client()
        response = c.post(reverseWithSession("acceptTrade", sessionId, args=(trade.pk, )))
        self.assertTrue("success" in response.content.decode("UTF-8"))

        try:
            Trade.objects.get(pk=trade.pk)
            self.fail()
        except ObjectDoesNotExist:
            pass

        sender.refresh_from_db()
        recipient.refresh_from_db()

        self.assertEquals(set(sender.stocks.all()), set(originalRecipientStocks))
        self.assertEquals(set(recipient.stocks.all()), set(originalSenderStocks))

    def test_bad_accept_trade(self):
        trade = createTrade()
        sender = trade.sender
        recipient = trade.recipient
        originalSenderStocks = list(sender.stocks.all())
        originalRecipientStocks = list(recipient.stocks.all())
        trade.senderStocks = originalSenderStocks
        trade.recipientStocks = originalRecipientStocks
        trade.save()

        sessionId = SessionId(associated_user=recipient.user)
        sessionId.save()

        c = Client()

        # No user
        response = c.post(reverse("acceptTrade", args=(trade.pk, )))
        self.assertTrue("error" in response.content.decode("UTF-8"))

        # Wrong user
        badSessionId = SessionId(associated_user=sender.user)
        badSessionId.save()
        response = c.post(reverseWithSession("acceptTrade", badSessionId, args=(trade.pk, )))
        self.assertTrue("error" in response.content.decode("UTF-8"))

    def test_decline_trade(self):
        trade = getTrade()
        sender = trade.sender
        recipient = trade.recipient
        originalSenderStocks = list(sender.stocks.all())
        originalRecipientStocks = list(recipient.stocks.all())
        trade.senderStocks = originalSenderStocks
        trade.recipientStocks = originalRecipientStocks
        trade.save()

        sessionId = SessionId(associated_user=recipient.user)
        sessionId.save()

        c = Client()
        response = c.post(reverseWithSession("declineTrade", sessionId, args=(trade.pk, )))
        self.assertTrue("success" in response.content.decode("UTF-8"))

        try:
            Trade.objects.get(pk=trade.pk)
            self.fail()
        except ObjectDoesNotExist:
            pass

        sender.refresh_from_db()
        recipient.refresh_from_db()

        self.assertEquals(set(sender.stocks.all()), set(originalSenderStocks))
        self.assertEquals(set(recipient.stocks.all()), set(originalRecipientStocks))

    def test_accept_suggestion(self):
        randomFloor = Floor.objects.all().first()
        randomStock = Stock.objects.all().exclude(pk__in=map(lambda x: x.pk, randomFloor.stocks.all())).first()
        u = User.objects.create_user(username=USERNAME, password=PASSWORD)
        player = Player(floor=randomFloor, user=u)
        player.save()
        suggestion = StockSuggestion(stock=randomStock, floor=randomFloor, requesting_player=player)
        suggestion.save()

        sessionId = SessionId(associated_user=randomFloor.owner)
        sessionId.save()

        c = Client()
        response = c.post(reverseWithSession("acceptStockSuggestion", sessionId, args=(suggestion.pk, )))
        self.assertTrue("success" in response.content.decode("UTF-8"))

        try:
            StockSuggestion.objects.get(pk=suggestion.pk)
            self.fail()
        except ObjectDoesNotExist:
            pass

        randomFloor.refresh_from_db()
        self.assertTrue(randomStock in randomFloor.stocks.all())

    def test_reject_suggestion(self):
        randomFloor = Floor.objects.all().first()
        randomStock = Stock.objects.all().exclude(pk__in=map(lambda x: x.pk, randomFloor.stocks.all())).first()
        u = User.objects.create_user(username=USERNAME, password=PASSWORD)
        player = Player(floor=randomFloor, user=u)
        player.save()
        suggestion = StockSuggestion(stock=randomStock, floor=randomFloor, requesting_player=player)
        suggestion.save()

        sessionId = SessionId(associated_user=randomFloor.owner)
        sessionId.save()

        c = Client()
        response = c.post(reverseWithSession("rejectStockSuggestion", sessionId, args=(suggestion.pk, )))
        self.assertTrue("success" in response.content.decode("UTF-8"))

        try:
            StockSuggestion.objects.get(pk=suggestion.pk)
            self.fail()
        except ObjectDoesNotExist:
            pass

        randomFloor.refresh_from_db()
        self.assertFalse(randomStock in randomFloor.stocks.all())

class AndroidTests(TestCase):
    FAKE_ANDROID_ID = "kajslfjoiehjfijlkfajsorijeifajsifjeoifjosjflkesajfoiewjfj";
    def test_register_token(self):
        user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        sessionId = SessionId(associated_user=user)
        sessionId.save()
        c = Client()
        old_len = AndroidToken.objects.filter(user=user).count()
        response = c.post(reverseWithSession("registerToken", sessionId), dumps({"registrationToken": AndroidTests.FAKE_ANDROID_ID}), content_type="application/json")

        tokens = AndroidToken.objects.filter(user=user)
        self.assertTrue(tokens.count() > old_len)
        newToken = tokens.first()
        self.assertEquals(newToken.token, AndroidTests.FAKE_ANDROID_ID)

    def test_register_token_twice(self):
        user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        sessionId = SessionId(associated_user=user)
        sessionId.save()
        c = Client()
        old_len = AndroidToken.objects.filter(user=user).count()
        response = c.post(reverseWithSession("registerToken", sessionId), dumps({"registrationToken": AndroidTests.FAKE_ANDROID_ID}), content_type="application/json")

        tokens = AndroidToken.objects.filter(user=user)
        self.assertTrue(tokens.count() > old_len)
        newToken = tokens.first()
        self.assertEquals(newToken.token, AndroidTests.FAKE_ANDROID_ID)

        response = c.post(reverseWithSession("registerToken", sessionId), dumps({"registrationToken": AndroidTests.FAKE_ANDROID_ID}), content_type="application/json")
        self.assertTrue(AndroidToken.objects.filter(token=AndroidTests.FAKE_ANDROID_ID).count() == 1)

    def test_bad_register_token(self):
        # Check if there is no user
        c = Client()
        response = c.post(reverse("registerToken"), dumps({"registrationToken": AndroidTests.FAKE_ANDROID_ID}), content_type="application/json")
        self.assertTrue("error" in response.content.decode("UTF-8"))

class TesterTests(TestCase):
    def test_get(self):
        c = Client()
        response = c.get(reverse("tester")+"?apples=pears&rocks=box")
        expected = {"get": {"apples": "pears", "rocks": "box"}, "post": {}}
        self.assertEquals(loads(response.content.decode("UTF-8")), expected)

    def test_both(self):
        c = Client()
        expected_post = {"helicopter": "airplane", "seesaw": "hat"}
        response = c.post(reverse("tester")+"?apples=pears&rocks=box", dumps(expected_post), content_type="application/json")
        expected = {"get": {"apples": "pears", "rocks": "box"}, "post": expected_post}
        self.assertEquals(loads(response.content.decode("UTF-8")), expected)

    def test_post(self):
        c = Client()
        expected_post = {"helicopter": "airplane", "seesaw": "hat"}
        response = c.post(reverse("tester"), dumps(expected_post), content_type="application/json")
        expected = {"get": {}, "post": expected_post}
        self.assertEquals(loads(response.content.decode("UTF-8")), expected)
