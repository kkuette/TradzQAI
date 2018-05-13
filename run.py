import os
import sys
import time

import argparse

# Hide TF loading logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

agent = "PPO"
device = '/cpu:0'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="TradzQAI, all model configuration are in conf.cfg")
    parser.add_argument("-g", "--gui", type=str, help="Display gui, default not displaying", default='off', choices=['on', 'off'])
    parser.add_argument("-v", "--verbose", type=int, help="Verbosity mode, default : 0", default=0, choices=[0, 1])
    parser.add_argument("-m", "--mode", type=str, help="Training or eval mode, default is training. Uselfull only without gui displayed", default='train', choices=['train', 'eval'])
    parser.add_argument("-s", "--session", type=str, help="Session live or local. Default local", default='local', choices=['local', 'live'])
    args = parser.parse_args()

    if 'on' in args.gui:
        raise NotImplementedError
        import qdarkstyle
        from PyQt5 import QtGui
        from PyQt5.QtWidgets import QApplication
        from GUI import MainWindow

        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        launch = MainWindow()
        launch.show()
        sys.exit(app.exec_())

    else:
        if "local" in args.session:
            from core import Local_session as Session
        else:
            from core import Live_session as Session
        session = Session(mode=args.mode)
        session.setAgent(agent="TRPO")
        session.loadSession()
        session.start()
        sys.exit(0)
