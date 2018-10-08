import time

class onpm(object):

    def __init__(self):
        self.orders = []
        self.order_number = 0
        self.decay = 0.01
        self.max_pip_diff = 5

    def bestPriceFunc(self, bids, asks, order, side, tid):
        id = tid

        if not tid:
            id = self.order_number
            self.order_number += 1
            ordr = dict(
                current_order = order,
                id = id,
                last_price = 0,
                start_price = 0,
                start_time = time.time()
            )
            self.orders.append(ordr)
        self.orders[id]['current_order'] = order
        if (time.time() - self.orders[id]['start_time']) / 60 >= 10:
            cancel = True
        else:
            cancel = False

        best_ask, best_bid = None, None
        # Mutation protection
        while True:
            try:
                best_bid = float(bids(0)[0][0]['price'])
                best_ask = float(asks(0)[0][0]['price'])
                break
            except:
                print ("rofl")
                pass

        spread = round(best_ask - best_bid, 2)
        price = self.orders[id]['last_price']
        if side == "buy":
            if self.orders[id]['start_price'] - self.orders[id]['last_price'] <= -self.max_pip_diff:
                cancel = True
            elif spread == 0.01:
                price = best_bid
            else:
                price = best_bid + self.decay
        elif side == "sell":
            if self.orders[id]['last_price'] - self.orders[id]['start_price'] <= -self.max_pip_diff:
                cancel = True
            elif spread == 0.01:
                price = best_ask
            else:
                price = best_ask + self.decay
        price = round(price, 2)
        self.orders[id]['last_price'] = price
        if not tid:
            self.orders[id]['start_price'] = price
        return price, cancel, id
