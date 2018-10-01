from ..cbpro import *
import json

import sys
import time
import datetime as dt
from copy import deepcopy
from threading import Thread, Event
from collections import deque
import numpy as np

class cbprowrapper(object):

    def __init__(self, key=None, b64=None, passphrase=None,
        url='https://api-public.sandbox.pro.coinbase.com', product_id=['BTC-EUR'], db=None):
        self.key = key
        self.b64 = b64
        self.passphrase = passphrase
        self.url = url
        self.product_id = product_id
        self.db = db
        self.authClient = None

        self.maxthreads = 20

        self.spread = 0

        self.last_bids = None
        self.last_asks = None

        self.ordernthreads = deque(maxlen=self.maxthreads)
        self.lasto_thread = 0

        self.oncthread = 0

        self.havetobuy = False
        self.havetosell = False

        self.order_size = 0

        self.is_running = False
        self.is_done = True

        self.event = Event()
        self.event.clear()

    def connectOrderBook(self):
        self.orderbook = OrderBookConsole(product_id=self.product_id, db=self.db)

    def connectAuthClient(self):
        if self.key and self.b64 and self.passphrase:
            self.authClient = AuthenticatedClient(self.key, self.b64,
                    self.passphrase, api_url=self.url)

    def buildNthread(self, n=20):
        for i in range(n):
            self.ordernthreads.append(dict(
                thread = Thread(target=self.order_managment),
                side = None,
                size = 0,
                event = self.event,
                manager = threadsManager(self.orderbook, self.authClient,
                    self.product_id),
                is_busy = False
                )
            )

    def getBestPrice(self, side):
        if "buy" in side:
            return float(self.last_bids[0])
            '''
            if float(self.spread) == float(0.01):
                return float(self.last_bids[0])
            elif float(self.spread) > 0.05:
                return round(float(self.last_bids[0]) + np.random.uniform(low=0.01,
                    high=0.05, size=1)[0], 2)
            else:
                return round(float(self.last_bids[0]) + np.random.uniform(low=0.01,
                    high=float(self.spread), size=1)[0], 2)
            '''
        else:
            return float(self.last_asks[0])
            '''
            if float(self.spread) == float(0.01):
                return float(self.last_asks[0])
            elif float(self.spread) > 0.05:
                return round(float(self.last_asks[0]) - np.random.uniform(low=0.01,
                    high=0.05, size=1)[0], 2)
            else:
                return round(float(self.last_asks[0]) - np.random.uniform(low=0.01,
                    high=float(self.spread), size=1)[0], 2)
            '''

    def buy_checking(self, order, price):
        if self.last_bids != price and \
            float(order['price']) < self.last_asks:
            return True
        return False
        '''
        if self.last_bids[0] > float(order['price']) or (float(order['price']) - self.last_bids[0]) > float(0.05) \
                or self.last_asks[0] <= float(order['price']):
            self.cancel_managment(order['id'])
            return True
        return False
        '''

    def sell_checking(self, order, price):
        if self.last_asks != price:
            return True
        return False
        '''
        if self.last_asks[0] < float(order['price']) or (self.last_asks[0] - float(order['price'])) > float(0.05) \
                or self.last_bids[0] >= float(order['price']):
            self.cancel_managment(order['id'])
            return True
        return False
        '''

    def orderManagment(self, side, volume):
        for i in range(len(self.ordernthreads)):
            if not self.ordernthreads[i]['is_busy']:
                self.oncthread += 1
                self.lasto_thread = i
                self.ordernthreads[i]['size'] = volume
                self.ordernthreads[i]['side'] = side
                self.ordernthreads[i]['is_busy'] = True
                self.ordernthreads[i]['thread'].start()
                break

    def order_managment(self):
        cthread = self.lasto_thread
        if "buy" in self.ordernthreads[cthread]['side']:
            checking_func = self.buy_checking
            open_func = self.ordernthreads[cthread]['manager'].buy_managment
        elif "sell" in self.ordernthreads[cthread]['side']:
            checking_func = self.sell_checking
            open_func = self.ordernthreads[cthread]['manager'].sell_managment

        self.ordernthreads[cthread]['manager'].setSize(self.ordernthreads[cthread]['size'])
        havetoopen = True
        while self.is_running:
            self.ordernthreads[cthread]['event'].wait()
            self.ordernthreads[cthread]['manager'].setLasts(self.last_bids,
                self.last_asks)
            orders = deepcopy(self.ordernthreads[cthread]['manager'].order)
            if len(orders) > 0:
                havetoopen = checking_func(orders[len(orders) - 1],
                    self.ordernthreads[cthread]['manager'].price)

            if self.ordernthreads[cthread]['manager'].rejected:
                havetoopen = True
                self.ordernthreads[cthread]['manager'].rejected = False

            if havetoopen:
                #print ("runner : %s opening on %s" % (cthread, self.last_asks))
                havetoopen = False
                open_func()

            self.ordernthreads[cthread]['manager'].cleanOrders()


        self.ordernthreads[cthread]['manager'].close()

        self.ordernthreads[cthread] = dict(
            thread = Thread(target=self.order_managment),
            side = None,
            size = 0,
            manager = threadsManager(self.orderbook, self.authClient,
                self.product_id),
            is_busy = False
            )

    def runOrderBook(self):
        while self.is_running:
            self.orderbook.start()
            try:
                while not self.orderbook.stop:
                    for i in range(10):
                        time.sleep(0.1)
                        if self.orderbook.stop:
                            break
                #print ("\n -- reset orderbook -- \n")
            except KeyboardInterrupt:
                pass
            except:
                print ("\n -- websocket reconnexion -- \n")
                self.connectOrderBook()
        self.orderbook.close()

    def runAuthClient(self):
        while self.is_running:
            if self.orderbook:
                if self.orderbook.message_recieved:
                    self.event.set()
                    self.orderbook.message_recieved = False
                    self.last_asks = round(float(self.orderbook.get_ask()), 2)
                    self.last_bids = round(float(self.orderbook.get_bid()), 2)
                    #print (self.last_asks, self.last_bids)
                    #print (self.last_asks, self.orderbook.last_bids)
                    if self.last_asks and self.last_bids:
                        self.spread = round(self.last_asks - self.last_bids, 2)
                        if self.havetobuy:
                            self.havetobuy = False
                            self.orderManagment("buy", self.order_size)
                        elif self.havetosell:
                            self.havetosell = False
                            self.orderManagment("sell", self.order_size)
                    self.event.clear()

    def stop(self):
        self.is_running = False
        self.event.set()
        self.orderbook.stop = True

    def run(self):
        self.is_running = True
        self.connectOrderBook()
        self.connectAuthClient()
        if self.authClient:
            Thread(target=self.runAuthClient).start()
            self.buildNthread(n=self.maxthreads)
        self.runOrderBook()


class OrderBookConsole(OrderBook):
    ''' Logs real-time changes to the bid-ask spread to the console '''

    def __init__(self, product_id=None, db=None):

        super(OrderBookConsole, self).__init__(product_id=product_id)

        self._product = product_id
        self.db = db

        # latest values of bid-ask spread
        self._bid = None
        self._ask = None
        self._bid_depth = None
        self._ask_depth = None
        self._last_ticker = None
        self.message_recieved = False
        if db:
            self.db.addDB(db='ticker')
            self.db.addCollection(collection=self._product)
            self.db.addRunner()
            #self.db.addDB(db='orderbook')
            #self.db.addCollection(collection=self._product)
            #self.db.addRunner()
            self.db.startAllRunner()


    def on_message(self, message):
        super(OrderBookConsole, self).on_message(message)

        # Calculate newest bid-ask spread
        bid = self.get_bid()
        bids = self.get_bids(bid)
        bid_depth = sum([b['size'] for b in bids])
        ask = self.get_ask()
        asks = self.get_asks(ask)
        ask_depth = sum([a['size'] for a in asks])
        self.message_recieved = True

        if self._bid == bid and self._ask == ask and self._bid_depth == bid_depth and self._ask_depth == ask_depth:
            # If there are no changes to the bid-ask spread since the last update, no need to print
            pass
        else:
            # If there are differences, update the cache
            self._bid = bid
            self._ask = ask
            self._bid_depth = bid_depth
            self._ask_depth = ask_depth

            print('{} {} bid: {:.3f} @ {:.2f}  ask: {:.3f} @ {:.2f}'.format(
                dt.datetime.now(), self.product_id, bid_depth, bid, ask_depth, ask))


class threadsManager(object):

    def __init__(self, orderbook=None, authClient=None, product_id=['BTC-EUR']):
        self.orderbook = orderbook
        self.authClient = authClient
        self.id = id

        self.product_id = product_id

        self.maxthreads = 100

        self.lastb_thread = 0
        self.lasts_thread = 0
        self.lastc_thread = 0

        self.order = []
        self.cacheOrder = []
        self.size = 0
        self.price = 0
        self.rejected = False

        self.last_bids = None
        self.last_asks = None

        self.should_arrive = []

        self.bnthreads = deque(maxlen=self.maxthreads)
        self.snthreads = deque(maxlen=self.maxthreads)
        self.cancelnthreads = deque(maxlen=self.maxthreads)

        self.is_running = True

        self.buildThreads(n=self.maxthreads)

    def setLasts(self, bid, ask):
        self.last_bids = bid
        self.last_asks = ask

    def close(self):
        self.is_running = False

    def setSize(self, size):
        self.size = size

    def buildThreads(self, n=20):
        for i in range(n):
            self.bnthreads.append(dict(
                thread = Thread(target=self.buy),
                price = 0,
                order_id = None,
                is_busy = False
                )
            )
            self.snthreads.append(dict(
                thread = Thread(target=self.sell),
                price = 0,
                order_id = None,
                is_busy = False
                )
            )
            self.cancelnthreads.append(dict(
                thread = Thread(target=self.cancelOrder),
                order = None,
                is_busy = False
                )
            )

    def sortOrders(self, last=None):
        co = self.cacheOrder
        o = self.order
        idx = 0
        for i in range(len(o)):
            if round(float(o[i]['price']), 2) != co[i] and \
                    last != co[i]:
                self.order.append(self.order[i])
                idx = self.sortOrders(last=co[i])
                break
            idx = i
        if idx == 0:
            idx = 1
        return idx

    def cleanOrders(self):
        l = self.sortOrders()
        while len(self.order) > (len(self.order) - l) + 1:
            self.cancel_managment(self.order[0]['id'])
            self.order.pop(0)
            self.cacheOrder.pop(0)

    def cancelOrder(self):
        cthread = self.lastc_thread
        self.authClient.cancel_order(self.cancelnthreads[cthread]['order'])

        self.cancelnthreads[cthread] = dict(
            thread = Thread(target=self.cancelOrder),
            is_busy = False
            )

    def buy(self):
        cthread = self.lastb_thread
        self.price = self.last_bids
        self.cacheOrder.append(self.price)
        m=self.authClient.buy(price=self.last_bids,
                            size=self.size,
                            order_type='limit',
                            product_id=self.product_id[0],
                            post_only=True)
        #print (time.time()-t)
        #print (json.dumps(m, indent=4))
        if len(m) > 2:
            if m['status'] == "rejected":
                self.rejected = True
            else:
                self.rejected = False
                self.order.append(m)
        else:
            self.rejected = True

        self.bnthreads[cthread] = dict(
            thread = Thread(target=self.buy),
            is_busy = False
            )

    def sell(self):
        cthread = self.lasts_thread
        self.price = self.last_asks
        self.cacheOrder.append(self.price)
        m = self.authClient.sell(price=self.last_asks,
                            size=self.size,
                            order_type='limit',
                            product_id=self.product_id[0],
                            post_only=True)

        if len(m) > 2:
            if m['status'] == "rejected":
                self.rejected = True
            else:
                self.rejected = False
                self.order.append(m)
        else:
            self.rejected = True

        self.snthreads[cthread] =dict(
            thread = Thread(target=self.sell),
            is_busy = False
            )

    def cancel_managment(self, id):
        for i in range(len(self.cancelnthreads)):
            if not self.cancelnthreads[i]['is_busy']:
                self.lastc_thread = i
                self.cancelnthreads[i]['is_busy'] = True
                self.cancelnthreads[i]['order'] = id
                self.cancelnthreads[i]['thread'].start()
                return
        print ("All cancel threads are busy")

    def buy_managment(self):
        for i in range(len(self.bnthreads)):
            if not self.bnthreads[i]['is_busy']:
                self.lastb_thread = i
                self.bnthreads[i]['is_busy'] = True
                self.bnthreads[i]['thread'].start()
                return
        print ("All buy threads are busy")

    def sell_managment(self):
        for i in range(len(self.snthreads)):
            if not self.snthreads[i]['is_busy']:
                self.lasts_thread = i
                self.snthreads[i]['is_busy'] = True
                self.snthreads[i]['thread'].start()
                return
        print ("All sell threads are busy")
