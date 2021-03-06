from random import choice
from django.test import TestCase, Client
from django import test
from django.core.urlresolvers import reverse
from stocks.models import *
from stocks.views import join_floor
from stocks.forms import TradeForm, LoginForm, RegistrationForm, EditFloorForm
import json
import time
from functools import reduce
import urllib
from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth.models import Group

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

def assignStocks(players, stocks):
    from itertools import cycle
    playerCycle = cycle(players)

    for p, s in zip(playerCycle, stocks):
        p.stocks.add(s)

    for p in players:
        p.save()

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

class TradeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        setUpClass(cls)

    def get_trade(self):
        floor = self.testFloor
        available_players = [p for p in Player.objects.filter(floor=floor) if not p.isFloor()]
        sender = available_players[0]
        recipient = available_players[1]
        sender_stocks = list(sender.stocks.all())
        recipient_stocks = list(recipient.stocks.all())
        trade = Trade.objects.create(floor=floor, sender=sender, recipient=recipient)
        trade.senderStocks = sender.stocks.all()
        trade.recipientStocks = recipient.stocks.all()
        return trade

    def test_self_trade(self):
        trade = self.get_trade()
        trade.sender = trade.recipient
        recipient = trade.recipient
        sender = trade.sender
        floor = trade.floor
        senderStocks = list(trade.senderStocks.all())
        recipientStocks = list(trade.recipientStocks.all())

        # I know this is a magic number. We can go to space when all the problems we have on Earth are solved.
        new_stock = Stock(symbol="SF")
        new_stock.save()

        floor.stocks.add(new_stock)
        sender.stocks.add(new_stock)
        floor.save()
        sender.save()

        recipientStocks = [recipient.stocks.all().exclude(symbol=new_stock.symbol)[0]]
        senderStocks = [new_stock]
        trade.delete()
        form = TradeForm({"other_user": recipient.user.username,
            "user_stocks": ",".join(s.symbol for s in senderStocks),
            "other_stocks": ",".join(s.symbol for s in recipientStocks)})
        self.assertFalse(form.is_valid(pkFloor=floor.pk, user=sender.user))
        self.assertIn("You can't send a trade to yourself", repr(form.errors))

    def test_trade_simple(self):
        trade = self.get_trade()
        recipient = trade.recipient
        sender = trade.sender
        senderStocks = list(trade.senderStocks.all())
        recipientStocks = list(trade.recipientStocks.all())
        trade.accept()
        trade.save()
        self.assertEqual(list(recipient.stocks.all()), senderStocks)
        self.assertEqual(set(sender.stocks.all()), set(recipientStocks))

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
        self.assertTrue(floor.name not in response.content.decode("UTF-8"))
        floor.public = True
        floor.save()
        response = client.get(reverse("floorsJson"))
        self.assertTrue(floor.name in response.content.decode("UTF-8"))

    def test_trade_counter(self):
        trade = self.get_trade()
        old_recipientStocks = list(trade.recipientStocks.all())
        old_senderStocks = list(trade.senderStocks.all())
        client = Client()
        client.force_login(trade.recipient.user)
        response = client.get(reverse("receivedTrade", kwargs={"pkTrade": trade.pk}))

        # The code for these should return the same thing, so I am checking them for equality
        self.assertEqual(trade.toFormDict(), response.context[-1]["form"].data)
        self.assertContains(response, reverse("counterTrade", kwargs={"pkTrade": trade.pk, "pkFloor": trade.floor.pk}))

        response = client.get(reverse("counterTrade", kwargs={"pkTrade": trade.pk, "pkFloor": trade.floor.pk}))
        response = client.post(reverse("trade", kwargs={"pkCountering": trade.pk, "pkFloor": trade.floor.pk}), {"other_user": trade.sender.user.username, "user_stocks": ",".join(i.symbol for i in trade.recipientStocks.all()), "other_stocks": ",".join(i.symbol for i in trade.senderStocks.all())})
        self.assertRedirects(response, reverse("dashboard"))
        self.assertQuerysetEqual(Trade.objects.filter(pk=trade.pk), [])
        newTrade = Trade.objects.all()[0]
        self.assertEqual(set(newTrade.senderStocks.all()), set(old_recipientStocks))
        self.assertEqual(list(newTrade.recipientStocks.all()), old_senderStocks)

    def test_add_stock(self):
        new_stock = Stock(symbol="SF")
        new_stock.save()
        floor = self.testFloor

        new_stocks = ",".join([s.symbol for s in floor.stocks.all()] + [new_stock.symbol])
        form = EditFloorForm({"name": floor.name, "privacy": not floor.public, "number_of_stocks": floor.num_stocks, "stocks": new_stocks, "permissiveness": floor.permissiveness})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['stocks'])
        form.apply(floor)
        stock = Stock.objects.get(symbol=new_stock.symbol)
        self.assertTrue(stock)
        self.assertIn(stock, floor.floorPlayer.stocks.all())

    def test_delete_stock(self):
        floor = Floor.objects.all()[0]
        stock_to_delete = choice(floor.stocks.all())
        new_stocks = ','.join(s.symbol for s in floor.stocks.all() if not s.pk == stock_to_delete.pk)
        form = EditFloorForm({"name": floor.name, "privacy": not floor.public, "number_of_stocks": floor.num_stocks, "stocks": new_stocks, "permissiveness": floor.permissiveness})
        self.assertIn(stock_to_delete, floor.stocks.all())
        self.assertTrue([p for p in Player.objects.filter(floor=floor) if stock_to_delete in p.stocks.all()])
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['stocks'])

        form.apply(floor)

        self.assertNotIn(stock_to_delete, floor.stocks.all())
        self.assertFalse([p for p in Player.objects.filter(floor=floor) if stock_to_delete in p.stocks.all()])

class PlayerTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        setUpClass(cls)

    def test_join_empty_floor(self):
        # Make a new floor with nobody on it
        floorOwner = self.otherUsers[1]
        floor = createFloor(floorOwner)
        user = self.otherUsers[0]

        client = Client()
        client.force_login(user)

        self.assertNotIn(user, (p.user for p in Player.objects.filter(floor=floor)))

        # Why is this a get? I don't think that's right...
        client.get(reverse("join", args=[floor.pk]))

        response = client.get(reverse("joinFloor"))
        self.assertFalse(response.context[-1]["floors_exist"])
        Player.objects.filter(user=user).delete()
        response = client.get(reverse("joinFloor"))
        self.assertTrue(response.context[-1]["floors_exist"])

    def test_scoring(self):
        floor = self.testFloor
        DEFAULT_PRICE = 5
        start = time.clock()
        for p in Player.objects.all():
            p.points = 0
            p.save()

        for s in floor.stocks.all():
            s.price = DEFAULT_PRICE
            s.update()

        for p in Player.objects.filter(floor=floor):
            if not p.isFloor():
                self.assertAlmostEqual(p.points,
                                       reduce(lambda x, y: x + y,
                                              [s.get_score() for s in p.stocks.all()], 0), delta=10)

        print("Finished! Took {} seconds!".format(time.clock() - start))

class SuggestionTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        setUpClass(cls)
        cls.testFloor.permissiveness = "permissive"
        cls.testFloor.save()

    def setUp(self):
        self.new_stock = Stock(symbol="SF")
        self.new_stock.save()

        self.form = TradeForm({"other_user": self.testFloor.floorPlayer.user.username, "other_stocks": self.new_stock.symbol, "user_stocks": ""})
        if self.form.is_valid(pkFloor=self.testFloor.pk, user=self.otherUsers[0]):
            self.trade = self.form.to_trade(pkFloor=self.testFloor.pk, user=self.otherUsers[0])
        else:
            raise RuntimeError("There was an error in validation. {}".format(form.errors))

    def test_suggestions(self):
        # Make sure that the trade was automatically accepted
        self.assertQuerysetEqual(Trade.objects.all(), [])

        # Make sure that the StockSuggestion wasn't automatically accepted
        player = Player.objects.get(floor=self.testFloor, user=self.otherUsers[0])
        self.assertNotIn(self.new_stock, player.stocks.all())
        self.assertNotIn(self.new_stock, self.testFloor.stocks.all())
        self.assertNotEqual(StockSuggestion.objects.all(), [])

        # Accept the only suggestion
        StockSuggestion.objects.filter(stock=self.new_stock)[0].accept()

        # Make sure the suggestion's acceptance worked like it was supposed to
        self.assertIn(self.new_stock, player.stocks.all())
        self.assertIn(self.new_stock, self.testFloor.stocks.all())

    def test_capped_suggestion(self):
        """
        Tests whether a player can get a stock suggested into their stable after they already have 
        the maximum number of stocks available.
        Imagine I'm capped at 2 stocks. I have 1 stock, then I ask the admin to accept a new stock onto the floor. 
        While that is going through, I trade for a second stock instantly with someone else. Now I have two stocks, 
        but the system owes me another, even though I can't have 3. What should it do? It should put the third 
        stock on floor owned by no one. What does it do? Let's find out. 
        """

        ONE_MORE_THAN_ONE = 2

        # Prepare
        self.testFloor.num_stocks = ONE_MORE_THAN_ONE
        self.testFloor.save()
        # Based on the setup method, we are guaranteed that everyone has one and exactly one stock. 
        # I think.

        # We have to start at 1 because the floor has more than 1 and this test won't work
        player = Player.objects.get(floor=self.testFloor, user=self.otherUsers[1])

        stockToAdd = Stock(symbol="SF")
        stockToAdd.save()

        # Make the suggestion that will later be accepted
        suggestion = StockSuggestion(stock=stockToAdd, requesting_player=player, floor=player.floor)
        suggestion.save()

        otherPlayer = Player.objects.get(floor=self.testFloor, user=self.otherUsers[2])
        self.assertNotEqual(otherPlayer, player)

        newTrade = Trade.objects.create(recipient=otherPlayer, floor=self.testFloor, sender=player)

        # Give the first player the other player's one stock, leaving the first player with 2, the max
        otherStock = otherPlayer.stocks.all()[0]
        newTrade.recipientStocks.add(otherStock)
        newTrade.save()
        newTrade.verify()
        newTrade.accept()

        self.assertEqual(list(otherPlayer.stocks.all()), [])
        self.assertIn(otherStock, player.stocks.all())
        self.assertEqual(player.stocks.count(), ONE_MORE_THAN_ONE)

        suggestion.accept()
        self.assertNotIn(stockToAdd, player.stocks.all())
        self.assertIn(stockToAdd, self.testFloor.stocks.all())
        self.assertIn(stockToAdd, self.testFloor.floorPlayer.stocks.all())

class UserTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        setUpClass(cls)

    def test_login_page(self):
        USERNAME = "thisIsAUsername"
        PASSWORD = "thisISAPassword"

        user = User.objects.create_user(USERNAME, "test@test.net", PASSWORD)
        player = Player(user=user, floor=self.testFloor)
        player.save()

        client = Client()
        # Make sure that you see the login page on first load
        origResponse = client.get(reverse("dashboard"), follow=True)
        self.assertTemplateUsed(origResponse, "index.html")
        self.assertTrue(origResponse.context[-1]["registrationForm"])
        self.assertTrue(origResponse.context[-1]["loginForm"])

        # Make sure bad username and password works right
        response = client.post(origResponse.redirect_chain[-1][0], {"username": "notAusername", "password": "certainlynotapassword", "nextPage": reverse("dashboard")})
        self.assertFormError(response, "loginForm", None, "That username does not exist") 

        # Make sure bad password works
        response = client.get(reverse("dashboard"), follow=True)
        response = client.post(origResponse.redirect_chain[-1][0], {"username": user.username, "password": "certainlynotapassword", "nextPage": reverse("dashboard")})
        self.assertFormError(response, "loginForm", None, "That is the wrong password") 

        # Make sure logging in properly works
        response = client.get(reverse("dashboard"), follow=True)
        response = client.post(origResponse.redirect_chain[-1][0],
                               {"username": USERNAME, "password": PASSWORD, "nextPage": reverse("dashboard")}, follow=True)
        self.assertEqual(response.redirect_chain[-1][0], reverse("dashboard")) 
