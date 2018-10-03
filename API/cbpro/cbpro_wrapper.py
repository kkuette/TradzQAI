from ..cbpro import *
import json

import sys, os
import time
import datetime as dt
from copy import deepcopy
from threading import Thread, Event
from collections import deque
import numpy as np
from datetime import datetime

class cbprowrapper(object):

    def __init__(self,
                 key=None,
                 b64=None,
                 passphrase=None,
                 url="https://api.pro.coinbase.com",
                 product_id=['BTC-EUR'],
                 db=None,
                 max_orders=5,
                 max_request_per_sec=5,
                 mode="maker",
                 auto_cancel=True):

        self.key = key
        self.b64 = b64
        self.passphrase = passphrase
        self.url = url
        self.product_id = product_id
        self.auto_cancel = auto_cancel
        self.db = db
        self.authClient = None
        self.mode = mode
        self.maxthreads = max_orders
        self.maxRequestPerSec = max_request_per_sec
        self.spread = 0
        self.last_bids = None
        self.last_asks = None
        self.ordernthreads = deque(maxlen=self.maxthreads)
        self.lasto_thread = 0
        self.oncthread = 0
        self.selector_id = 0
        self.unused_manager = 0
        self.no_thread_used = False
        self.order_size = 0
        self.is_running = False
        self.is_done = True
        self.bpfunc = None
        self.bestprice = 0
        self.eur_wallet = None
        self.btc_wallet = None
        self.wallet = None
        self.requestTime = time.time()
        self.event = Event()
        self.event.clear()
        self.connectOrderBook()
        self.connectAuthClient()
        self.setBestPriceFunc(self.getBestPrice)

    def connectOrderBook(self):
        self.orderbook = OrderBookConsole(product_id=self.product_id,
            db=self.db, event=self.event)

    def connectAuthClient(self):
        if self.key and self.b64 and self.passphrase:
            self.authClient = AuthenticatedClient(self.key, self.b64,
                    self.passphrase, api_url=self.url)

    def getWallet(self):
        if self.authClient:
            return self.authClient.get_accounts()

    def getHistorical(self):
        return self.orderbook.getHistorical()

    def getTicks(self):
        if self.orderbook:
            return self.orderbook.getTicks()

    def setBestPriceFunc(self, function):
        self.bpfunc = function

    def addOrder(self, side, volume):
        if self.authClient and self.mode == "maker":
            self.orderManagment(side, volume)
        elif self.authClient and self.mode == "taker":
            self.takerManagment(side, volume)
        else:
            print ("We cannot open any orders, there is no client")

    def buildNthread(self, n=20):
        for i in range(n):
            self.ordernthreads.append(dict(
                thread = Thread(target=self.order_managment),
                side = None,
                size = 0,
                best_price = 0,
                event = Event(),
                manager = threadsManager(authClient=self.authClient,
                    product_id=self.product_id,
                    userorder=self.orderbook.addUserOrder),
                is_busy = False
                )
            )

    def price_checking(self, new_price, current_price):
        if new_price != current_price:
            return True
        return False

    def getBestPrice(self, bids, asks):
        idx = 5
        #idx = np.random.randint(low=1, high=30, size=1)[0]
        if self.ordernthreads[0]['side'] == "buy":
            return round(float(bids(idx)[idx-1][0]['price']), 2)
        elif self.ordernthreads[0]['side'] == "sell":
            return round(float(asks(idx)[idx-1][0]['price']), 2)

    def orderManagment(self, side, volume, order=None, price=0):
        for i in range(len(self.ordernthreads)):
            if not self.ordernthreads[i]['is_busy']:
                self.lasto_thread = i
                self.ordernthreads[i]['size'] = volume
                self.ordernthreads[i]['side'] = side
                self.ordernthreads[i]['manager'].price = price
                self.ordernthreads[i]['manager'].order = [order]
                self.ordernthreads[i]['is_busy'] = True
                self.ordernthreads[i]['thread'].start()
                return
        print ("All order threads are busy")

    def order_managment(self):
        self.oncthread += 1
        cthread = self.lasto_thread
        if "buy" in self.ordernthreads[cthread]['side']:
            open_func = self.ordernthreads[cthread]['manager'].buy_managment
        elif "sell" in self.ordernthreads[cthread]['side']:
            open_func = self.ordernthreads[cthread]['manager'].sell_managment
        self.ordernthreads[cthread]['event'].clear()
        self.ordernthreads[cthread]['manager'].setSize(self.ordernthreads[cthread]['size'])
        if not self.ordernthreads[cthread]['manager'].order[0]:
            havetoopen = True
        while self.ordernthreads[cthread]['is_busy'] and self.is_running:
            self.ordernthreads[cthread]['event'].wait()
            self.ordernthreads[cthread]['best_price'] = self.bpfunc(self.last_bids,
                self.last_asks)
            self.ordernthreads[cthread]['manager'].setBestPrice(self.ordernthreads[cthread]['best_price'])
            havetoopen = self.price_checking(self.ordernthreads[cthread]['best_price'],
                self.ordernthreads[cthread]['manager'].price)
            if self.ordernthreads[cthread]['manager'].rejected:
                havetoopen = True
                self.ordernthreads[cthread]['manager'].rejected = False
            if havetoopen:
                self.no_thread_used = False
                self.unused_manager = 0
                self.ordernthreads[cthread]['manager'].cleanOrders()
                havetoopen = False
                open_func()
            elif self.ordernthreads[cthread]['is_busy'] and self.is_running:
                self.unused_manager += 1
                self.managerSelector()
            self.ordernthreads[cthread]['event'].clear()

        if self.auto_cancel:
            time.sleep(1)
            self.ordernthreads[cthread]['manager'].cleanOrders()
        self.ordernthreads[cthread] = dict(
            thread = Thread(target=self.order_managment),
            side = None,
            size = 0,
            best_price = 0,
            event = Event(),
            manager = threadsManager(authClient=self.authClient,
                product_id=self.product_id,
                userorder=self.orderbook.addUserOrder),
            is_busy = False
            )
        self.oncthread -= 1

    def takerManagment(self, side, volume):
        if self.orderbook and not self.orderbook.stop and self.authClient:
            if side == 'buy':
                self.authClient.buy(price=round(float(self.last_bids(1)[0][0]['price']), 2),
                                    size=volume,
                                    order_type='market',
                                    product_id=self.product_id[0])
            else:
                self.authClient.sell(price=round(float(self.last_asks(1)[0][0]['price']), 2),
                                    size=volume,
                                    order_type='market',
                                    product_id=self.product_id[0])

    def managerSelector(self, timeout=0):
        if timeout == self.maxthreads:
            return
        elif self.unused_manager == self.oncthread:
            self.unused_manager = 0
            self.no_thread_used = True
            return
        else:
            self.selector_id += 1
            if not self.ordernthreads[self.selector_id % self.maxthreads]['is_busy']:
                self.managerSelector(timeout=timeout+1)
            else:
                self.ordernthreads[self.selector_id % self.maxthreads]['event'].set()
                return

    def closeAllManagers(self):
        for thread in self.ordernthreads:
            thread['event'].set()
            thread['is_busy'] = False

    def closeManager(self, id):
        self.ordernthreads[i]['is_busy'] = False

    def checkFills(self):
        fills = self.orderbook.getUserFills()
        if fills and self.oncthread > 0:
            for idx in range(len(fills)):
                for i in range(len(self.ordernthreads)):
                    if self.ordernthreads[i]['is_busy']:
                        if self.ordernthreads[i]['manager'].order[0]['id'] == \
                            fills[idx]:
                            self.ordernthreads[i]['is_busy'] = False
                            self.ordernthreads[i]['event'].set()
                            break
            self.orderbook.DeleteFill(len(fills))

    def checkChanges(self):
        changes = self.orderbook.getUserOrderChange()
        if changes and self.oncthread > 0:
            for idx in range(len(changes)):
                for i in range(len(self.ordernthreads)):
                    if self.ordernthreads[i]['is_busy']:
                        if self.ordernthreads[i]['manager'].order[0]['id'] == \
                            changes[idx][0]:
                            self.ordernthreads[i]['manager'].size -= float(changes[idx][1])
                            if self.ordernthreads[i]['manager'].size < 0.001:
                                self.ordernthreads[i]['is_busy'] = False
                                self.ordernthreads[i]['event'].set()
                            break
            self.orderbook.DeleteChange(len(changes))

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

    def runAuthClient(self):
        self.last_asks = self.orderbook.get_nasks
        self.last_bids = self.orderbook.get_nbids
        while self.is_running:
            if self.orderbook:
                self.event.wait()
                self.checkFills()
                self.checkChanges()
                if (time.time()-self.requestTime) >= (1/self.maxRequestPerSec)*2\
                        or self.no_thread_used:
                    self.requestTime = time.time()
                    self.managerSelector()
                if self.is_running:
                    self.event.clear()

    def stop(self):
        self.closeAllManagers()
        self.is_running = False
        self.event.set()
        self.orderbook.stop = True


    def run(self):
        self.is_running = True
        if self.authClient:
            Thread(target=self.runAuthClient).start()
            self.buildNthread(n=self.maxthreads)
            for order in self.authClient.get_orders():
                self.orderManagment(order['side'], order['size'], order=order,
                    price=order['price'])
        Thread(target=self.runOrderBook, daemon=True).start()

class OrderBookConsole(OrderBook):
    ''' Logs real-time changes to the bid-ask spread to the console '''

    def __init__(self,
                 product_id=None,
                 db=None,
                 event=None,
                 url="wss://ws-feed.pro.coinbase.com",
                 api_key="",
                 api_secret="",
                 api_passphrase="",
                 channels=None):

        #"wss://ws-feed-public.sandbox.pro.coinbase.com"

        super(OrderBookConsole, self).__init__(product_id=product_id,
            url=url, api_key=api_key, api_secret=api_secret,
            api_passphrase=api_passphrase, channels=channels)

        self._product = product_id
        self.db = db

        # latest values of bid-ask spread
        self._bid = None
        self._ask = None
        self._bid_depth = None
        self._ask_depth = None
        self._last_ticker = None
        self.publicClient = None
        self.ticks = []
        self.user_orders = []
        self.user_fills = []
        self.user_order_change = []

        self.message_recieved = event
        if db:
            self.db.addDB(db='ticker')
            self.db.addCollection(collection=self._product)
            self.db.addRunner()
            #self.db.addDB(db='orderbook')
            #self.db.addCollection(collection=self._product)
            #self.db.addRunner()
            self.db.startAllRunner()
        self.connectPublicClient()

    def on_message(self, message):
        super(OrderBookConsole, self).on_message(message)

        # Calculate newest bid-ask spread
        bid = self.get_bid()
        bids = self.get_bids(bid)
        bid_depth = sum([b['size'] for b in bids])
        ask = self.get_ask()
        asks = self.get_asks(ask)
        ask_depth = sum([a['size'] for a in asks])

        msg_type = message['type']
        if 'reason' in message:
            msg_reason = message['reason']
            if msg_reason == 'canceled' and msg_type == 'done':
                if message['order_id'] in self.user_orders:
                    self.deleteOrder(message['order_id'])
            elif msg_reason == 'filled' and msg_type == 'done':
                if message['order_id'] in self.user_orders:
                    self.addFills(message['order_id'])
                    self.deleteOrder(message['order_id'])
        elif msg_type == 'match':
            if message['maker_order_id'] in self.user_orders:
                self.addOrderChange(message['maker_order_id'], message['size'])

        #print ("Ordres en cour :", self.user_orders, "Ordres remplis :",
        #    self.user_fills, "Ordres changer :", self.user_order_change)

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

        if self._last_ticker != self._current_ticker and self._current_ticker:
            self.ticks.append(self._current_ticker)
            self._last_ticker = self._current_ticker

    def connectPublicClient(self):
        self.publicClient = PublicClient(api_url="https://api.pro.coinbase.com")

    def getHistorical(self):
        if self.publicClient:
            return self.publicClient.get_product_historic_rates(self.product_id,
                 granularity=60)

    def getTicks(self):
        return self.ticks

    def addUserOrder(self, order_id):
        self.user_orders.append(order_id)
        #print (self.user_orders)

    def addFills(self, order_id):
        self.user_fills.append(order_id)

    def addOrderChange(self, order_id, size):
        self.user_order_change.append([order_id, size])

    def DeleteFill(self, l):
        while len(self.user_fills) > 0 and \
            len(self.user_fills) > (len(self.user_fills) - l):
            self.user_fills.pop(0)

    def DeleteChange(self, l):
        while len(self.user_order_change) > 0 and \
            len(self.user_order_change) > (len(self.user_order_change) - l):
            self.user_order_change.pop(0)

    def deleteOrder(self, order_id):
        for idx in range(len(self.user_orders)):
            if order_id == self.user_orders[idx]:
                self.user_orders.pop(idx)
                return

    def getUserFills(self):
        if len(self.user_fills) > 0:
            return self.user_fills
        else:
            return None

    def getUserOrderChange(self):
        if len(self.user_order_change) > 0:
            return self.user_order_change
        else:
            None

class threadsManager(object):

    def __init__(self, authClient=None, product_id=None, userorder=None):

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
        self.adduserorder = userorder

        self.bnthreads = deque(maxlen=self.maxthreads)
        self.snthreads = deque(maxlen=self.maxthreads)
        self.cancelnthreads = deque(maxlen=self.maxthreads)

        self.buildThreads(n=self.maxthreads)

    def setBestPrice(self, bp):
        self.bp = bp

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
            if self.order[0]:
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
        p = self.bp
        self.price = p
        m=self.authClient.buy(price=p,
                            size=self.size,
                            order_type='limit',
                            product_id=self.product_id[0],
                            post_only=True)

        if 'message' in m:
            self.rejected = True
        if 'status' in m:
            if m['status'] == "rejected":
                self.rejected = True
            else:
                self.rejected = False
                self.order.append(m)
                self.adduserorder(m['id'])

        self.bnthreads[cthread] = dict(
            thread = Thread(target=self.buy),
            is_busy = False
            )

    def sell(self):
        cthread = self.lasts_thread
        p = self.bp
        self.price = p
        m = self.authClient.sell(price=p,
                            size=self.size,
                            order_type='limit',
                            product_id=self.product_id[0],
                            post_only=True)

        if 'message' in m:
            self.rejected = True
        if 'status' in m:
            if m['status'] == "rejected":
                self.rejected = True
            else:
                self.rejected = False
                self.order.append(m)
                self.adduserorder(m['id'])

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
