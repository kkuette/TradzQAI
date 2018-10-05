import time

class onpm(object):

    def __init__(self):
        self.orders = []
        self.order_number = 0
        self.decay = 0.01

    def bestPriceFunc(self, bids, asks, order, side, id):
        if not id:
            id = self.order_number
            self.order_number += 1
            ordr = dict(
                current_order = order,
                id = id,
                last_price = 0,
                start_time = time.time()
            )
            self.orders.append(ordr)
        self.orders[id]['current_order'] = order
        if (time.time() - self.orders[id]['start_time']) / 10 >= 1:
            cancel = True
        else:
            cancel = False
        best_bid = round(float(bids(0)[0][0]['price']), 2)
        best_ask = round(float(asks(0)[0][0]['price']), 2)
        spread = round(best_ask - best_bid, 2)
        price = self.orders[id]['last_price']
        if side == "buy":
            if spread == 0.01:
                price = best_bid
            else:
                price = best_bid + self.decay
        elif side == "sell":
            if spread == 0.01:
                price = best_ask
            else:
                price = best_ask + self.decay
        self.orders[id]['last_price'] = price
        return price, cancel, id
