import os
import sys

import argparse

# Hide TF loading logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Set cpu
#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="TradzQAI, all model configuration are in conf.cfg")
    parser.add_argument("-g", "--GUI", type=int, help="Display GUI, default not displaying", default=0, choices=[0, 1])
    parser.add_argument("-v", "--verbose", type=int, help="Verbosity mode, default is not verbose", default=0, choices=[0, 1])
    parser.add_argument("-m", "--mode", type=int, help="Training or eval mode, default is training. Uselfull only without GUI displayed", default=0, choices=[0, 1])
    args = parser.parse_args()

    if args.GUI == 1:
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
        from environnement import Environnement
        from core import Local_Worker

        env = Environnement(0)
        if env.mode == 1:
            env.mode = "eval"
            env.episode_count = 1
        else:
            env.mode = "train"
        worker = Local_Worker(env)
        worker.run(env)
