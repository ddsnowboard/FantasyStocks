from stocks.models import Trade
from django.db.models.signals import post_save
from .models import AndroidToken
from django.dispatch import receiver

@receiver(post_save, sender=Trade)
def afterSaveTrade(sender, **kwargs):
    trade = kwargs["instance"]
    if not trade.recipient.isFloor():
        if kwargs["created"] and not kwargs["raw"]:
            tokens = AndroidToken.objects.filter(user=trade.recipient.user)
            for token in tokens:
                token.ping("{} sent you a trade on {}!".format(trade.sender.get_name(), trade.floor.name), "")
