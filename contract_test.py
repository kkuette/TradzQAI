from API import Api
import time
import sys

passphrase = ""
key = ""
b64 = ""

url = 'https://api-public.sandbox.pro.coinbase.com'

a = Api("cbpro", passphrase=passphrase, b64=b64,
    key=key, url=url)
a.start()
try:
    while True:
        time.sleep(0.2)
        o = input("buy or sell ? ")
        if "buy" in o:
            a.buy(float(input("Which size would you buy ? ")))
        elif "sell" in o:
            a.sell(float(input("Which size would you buy ? ")))
        else:
            print ("I don't understand, please retry\n")
        time.sleep(1)
except KeyboardInterrupt:
    a.stop()
    sys.exit(0)
