from django.apps import AppConfig


class StocksapiConfig(AppConfig):
    name = 'stocksApi'
    def ready(self):
        from stocksApi import signals
