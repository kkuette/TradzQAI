import os
import sys
import time
import datetime
import argparse

# Hide TF loading logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

agent = "PPO"
device = "/cpu:0"


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="TradzQAI, all model configuration are in conf.cfg")
    parser.add_argument("-g", "--gui", type=str, help="Display gui, default not displaying", default='off', choices=['on', 'off'])
    parser.add_argument("-b", "--build", type=str, help="Build config files from a given agent, default PPO", default='PPO')
    #parser.add_argument("-v", "--verbose", type=int, help="Verbosity mode, default : 0", default=0, choices=[0, 1])
    parser.add_argument("-m", "--mode", type=str, help="Training or eval mode, default is training. Uselfull only without gui displayed", default='train', choices=['train', 'eval'])
    parser.add_argument("-s", "--session", type=str, help="Session live or local. Default local", default='local', choices=['local', 'live'])
    parser.add_argument("-c", "--config", type=str, help="Config directory to load from. Default config/", default='config/')
    args = parser.parse_args()

    if 'on' in args.gui:
        #raise NotImplementedError("gui isnt fonctionnal with session yet")

        import qdarkstyle
        from PyQt5 import QtGui
        from PyQt5.QtWidgets import QApplication
        from GUI import MainWindow

        if "local" in args.session:
            from core import Local_session as Session
        else:
            from core import Live_session as Session

        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        launch = MainWindow(Session(mode=args.mode, config=args.config, contract_type='classic'))
        launch.show()
        sys.exit(app.exec_())

    elif args.build:
        from core import Local_session as Session
        session = Session(mode=args.mode, config=args.config, contract_type='classic', agent=args.build)
        session._stop()

    else:
        if "local" in args.session:
            from core import Local_session as Session
        else:
            from core import Live_session as Session
        session = Session(mode=args.mode, config=args.config, contract_type='classic')
        session.setAgent(device=device)
        session.loadSession()
        session.start()
        try:
            while not session.env.stop:
                time.sleep(1)
            session._stop()
        except (KeyboardInterrupt, ValueError, AttributeError):
            if session:
                session._stop()
        sys.exit(0)
