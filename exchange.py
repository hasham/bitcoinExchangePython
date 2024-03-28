from enum import Enum, auto


class ExchangeType(Enum):
    ENUM = auto()
    COINBASE = auto()
    GEMINI = auto()
    KRAKEN = auto()


class Exchange:

    @classmethod
    def get_all_exchanges(cls):
        # Mapping of CryptoExchange enum members to their URLs
        # note: hardcoding Bitcoin
        return {
            ExchangeType.COINBASE: "https://api.exchange.coinbase.com/products/BTC-USD/book?level=2",
            ExchangeType.GEMINI: "https://api.gemini.com/v1/book/BTCUSD",
            ExchangeType.KRAKEN: "https://api.kraken.com/0/public/Depth?pair=XBTUSD",
        }
