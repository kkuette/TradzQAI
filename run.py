import sys
import time
import argparse

device = "/cpu:0"

passphrase = ''
key = ''
b64 = ''
url = ''

product_id = ['BTC-EUR']

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="TradzQAI")
    parser.add_argument("-b", "--build", help="Build config files from a given agent, default PPO")
    parser.add_argument("-m", "--mode", help="Training or eval mode, default is training. Uselfull only without gui displayed", default='train', choices=['train', 'eval'])
    parser.add_argument("-s", "--session", help="Session live or local. Default local", default='local', choices=['local', 'live'])
    parser.add_argument("-c", "--config", help="Config directory to load from. Default config/", default='config/')
    args = parser.parse_args()

    if args.build:
        from TradzQAI import Local_session as Session
        session = Session(agent=args.build)
        session._stop()

    else:
        if "local" in args.session:
            from TradzQAI import Local_session as Session
            session = Session(mode=args.mode, config=args.config)
        else:
            from TradzQAI import Live_session as Session
            session = Session(mode=args.mode, config=args.config)
            session.initApi(key=key, b64=b64, passphrase=passphrase, url=url,
                product_id=product_id)
        session.setAgent(device=device)
        session.loadSession()
        session.start()
        try:
            while not session.env.stop:
                time.sleep(1)
        except:
            pass
        session.stop()
        sys.exit(0)
