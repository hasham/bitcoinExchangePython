import requests

from exchange import Exchange, ExchangeType


def fetch_data_from_exchange(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong", err)


def parse_coinbase_orders(data):
    bids = [{"price": float(bid[0]), "quantity": float(bid[1])} for bid in data["bids"]]
    asks = [{"price": float(ask[0]), "quantity": float(ask[1])} for ask in data["asks"]]
    return bids, asks


def parse_gemini_orders(data):
    bids = [{"price": float(bid["price"]), "quantity": float(bid["amount"])} for bid in data["bids"]]
    asks = [{"price": float(ask["price"]), "quantity": float(ask["amount"])} for ask in data["asks"]]
    return bids, asks


def parse_kraken_orders(data):
    bids = [{"price": float(bid[0]), "quantity": float(bid[1])} for bid in data["result"]["XXBTZUSD"]["bids"]]
    asks = [{"price": float(ask[0]), "quantity": float(ask[1])} for ask in data["result"]["XXBTZUSD"]["asks"]]
    return bids, asks


def merge_and_sort_books(books, key, reverse=False):
    merged = sum(books, [])
    return sorted(merged, key=lambda x: x[key], reverse=reverse)


def calculate_order_price(orders, quantity):
    total_cost = 0
    remaining_quantity = quantity
    for order in orders:
        if order["quantity"] >= remaining_quantity:
            total_cost += remaining_quantity * order["price"]
            break
        else:
            total_cost += order["quantity"] * order["price"]
            remaining_quantity -= order["quantity"]
    return total_cost


def main(quantity=10.0):
    exchanges = Exchange().get_all_exchanges()
    coinbase = exchanges.get(ExchangeType.COINBASE, None)
    gemini = exchanges.get(ExchangeType.GEMINI, None)
    kraken = exchanges.get(ExchangeType.KRAKEN, None)

    coinbase_bids, coinbase_asks = [], []
    gemini_bids, gemini_asks = [], []
    kraken_bids, kraken_asks = [], []

    if coinbase is not None:
        response = fetch_data_from_exchange(coinbase)
        coinbase_bids, coinbase_asks = parse_coinbase_orders(response)

    if gemini is not None:
        response = fetch_data_from_exchange(gemini)
        gemini_bids, gemini_asks = parse_gemini_orders(response)

    if kraken is not None:
        response = fetch_data_from_exchange(kraken)
        kraken_bids, kraken_asks = parse_kraken_orders(response)

    bids = merge_and_sort_books([coinbase_bids, gemini_bids, kraken_bids], key="price", reverse=True)
    asks = merge_and_sort_books([gemini_asks, gemini_asks, kraken_asks], key="price")

    buy_price = calculate_order_price(asks, quantity)
    sell_price = calculate_order_price(bids, quantity)

    print(f"Price to buy {quantity} BTC: ${round(buy_price, 2)}")
    print(f"Price to sell {quantity} BTC: ${round(sell_price, 2)}")


if __name__ == "__main__":
    while True:
        try:
            quantity = float(input("Enter the quantity of BTC to buy/sell: ").strip())
            break  # Exit loop if input is successfully parsed
        except ValueError:
            print("Invalid quantity. Please enter a valid number.")

    main(quantity)
