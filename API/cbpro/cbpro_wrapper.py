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

    def __init__(self,
                 key=None,
                 b64=None,
                 passphrase=None,
                 url="https://api.pro.coinbase.com",
                 product_id=['BTC-EUR'],
                 db=None,
                 max_orders=5,
                 max_request_per_sec=5):

        self.key = key
        self.b64 = b64
        self.passphrase = passphrase
        self.url = url
        self.product_id = product_id
        self.db = db
        self.authClient = None

        self.maxthreads = max_orders
        self.maxrequestpersec = max_request_per_sec

        self.spread = 0

        self.last_bids = None
        self.last_asks = None

        self.ordernthreads = deque(maxlen=self.maxthreads)
        self.lasto_thread = 0

        self.oncthread = 0

        self.order_size = 0

        self.is_running = False
        self.is_done = True

        self.requestTime = time.time()

        self.event = Event()
        self.event.clear()

    def connectOrderBook(self):
        self.orderbook = OrderBookConsole(product_id=self.product_id, db=self.db,
                event=self.event)

    def connectAuthClient(self):
        if self.key and self.b64 and self.passphrase:
            self.authClient = AuthenticatedClient(self.key, self.b64,
                    self.passphrase, api_url=self.url)

    def addOrder(self, side, volume):
        self.orderManagment(side, volume)

    def buildNthread(self, n=20):
        for i in range(n):
            self.ordernthreads.append(dict(
                thread = Thread(target=self.order_managment),
                side = None,
                size = 0,
                manager = threadsManager(self.authClient,
                    product_id=self.product_id),
                is_busy = False
                )
            )

    def buy_checking(self, order, price):
        if self.last_bids != price:
            return True
        return False

    def sell_checking(self, order, price):
        if self.last_asks != price:
            return True
        return False

    def orderManagment(self, side, volume):
        for i in range(len(self.ordernthreads)):
            if not self.ordernthreads[i]['is_busy']:
                self.lasto_thread = i
                self.ordernthreads[i]['size'] = volume
                self.ordernthreads[i]['side'] = side
                self.ordernthreads[i]['is_busy'] = True
                self.ordernthreads[i]['thread'].start()
                break

    def order_managment(self):
        self.oncthread += 1
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
            self.event.wait()
            self.ordernthreads[cthread]['manager'].setLasts(self.last_bids,
                self.last_asks)
            orders = deepcopy(self.ordernthreads[cthread]['manager'].order)
            if len(orders) > 0:
                havetoopen = checking_func(orders[len(orders) - 1],
                    self.ordernthreads[cthread]['manager'].price)
                if havetoopen:
                    self.ordernthreads[cthread]['manager'].cleanOrders()

            if self.ordernthreads[cthread]['manager'].rejected:
                havetoopen = True
                self.ordernthreads[cthread]['manager'].rejected = False

            if havetoopen:
                havetoopen = False
                open_func()

        self.ordernthreads[cthread] = dict(
            thread = Thread(target=self.order_managment),
            side = None,
            size = 0,
            manager = threadsManager(authClient=self.authClient,
                product_id=self.product_id),
            is_busy = False
            )

    def runOrderBook(self):
        while self.is_running:
            self.orderbook.start()
            try:
                while not self.orderbook.stop:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            except:
                print ("\n -- websocket reconnexion -- \n")
                self.connectOrderBook()
        self.orderbook.close()

    def runAuthClient(self):
        while self.is_running:
            if self.orderbook:
                self.event.wait()
                if (time.time()-self.requestTime) >= (1/self.maxrequestpersec)\
                        *(self.oncthread*2):
                    self.last_asks = round(float(self.orderbook.get_ask()), 2)
                    self.last_bids = round(float(self.orderbook.get_bid()), 2)
                    if self.last_asks and self.last_bids:
                        self.spread = round(self.last_asks - self.last_bids, 2)
                        self.requestTime = time.time()
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
        Thread(target=self.runOrderBook).start()


class OrderBookConsole(OrderBook):
    ''' Logs real-time changes to the bid-ask spread to the console '''

    def __init__(self, product_id=None, db=None, event=None):

        super(OrderBookConsole, self).__init__(product_id=product_id)

        self._product = product_id
        self.db = db

        # latest values of bid-ask spread
        self._bid = None
        self._ask = None
        self._bid_depth = None
        self._ask_depth = None
        self._last_ticker = None
        self.message_recieved = event
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
        self.message_recieved.set()

        if self._bid == bid and self._ask == ask and self._bid_depth == bid_depth and self._ask_depth == ask_depth:
            # If there are no changes to the bid-ask spread since the last update, no need to print
            pass
        else:
            # If there are differences, update the cache
            self._bid = bid
            self._ask = ask
            self._bid_depth = bid_depth
            self._ask_depth = ask_depth

            #print('{} {} bid: {:.3f} @ {:.2f}  ask: {:.3f} @ {:.2f}'.format(
            #    dt.datetime.now(), self.product_id, bid_depth, bid, ask_depth, ask))


class threadsManager(object):

    def __init__(self, authClient=None, product_id=None):

        self.authClient = authClient
        self.product_id = product_id

        self.maxthreads = 100

        self.lastb_thread = 0
        self.lasts_thread = 0
        self.lastc_thread = 0

        self.order = []
        self.size = 0
        self.price = 0
        self.rejected = False

        self.last_bids = None
        self.last_asks = None

        self.bnthreads = deque(maxlen=self.maxthreads)
        self.snthreads = deque(maxlen=self.maxthreads)
        self.cancelnthreads = deque(maxlen=self.maxthreads)

        self.buildThreads(n=self.maxthreads)

    def setLasts(self, bid, ask):
        self.last_bids = bid
        self.last_asks = ask

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

    def cleanOrders(self):
        while len(self.order) > 0:
            self.cancel_managment(self.order[0]['id'])
            self.order.pop(0)

    def cancelOrder(self):
        cthread = self.lastc_thread
        self.authClient.cancel_order(self.cancelnthreads[cthread]['order'])

        self.cancelnthreads[cthread] = dict(
            thread = Thread(target=self.cancelOrder),
            is_busy = False
            )

    def buy(self):
        cthread = self.lastb_thread
        p, self.price = self.last_bids, self.last_bids
        m=self.authClient.buy(price=p,
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

        self.bnthreads[cthread] = dict(
            thread = Thread(target=self.buy),
            is_busy = False
            )

    def sell(self):
        cthread = self.lasts_thread
        p, self.price = self.last_asks, self.last_asks
        m = self.authClient.sell(price=p,
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
