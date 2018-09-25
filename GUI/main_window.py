from .overview_window import OverviewWindow
from .model_window import ModelWindow
from .wallet_window import WalletWindow
from tools import *

import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

h = 950
w = 550
hp = 1855
wp = 1080 - 55
'''
if env._platform == 'win32':
    wp = 1080 - 55
elif env._platform == 'Linux':
    wp = 1080 - 30
'''

class MainWindow(QWidget):

    def __init__(self, session):
        super(MainWindow, self).__init__()
        self.session = session
        self.Set_UI()

    def Set_UI(self):
        self.resize(h, w)
        self.setWindowTitle(self.session.env.name)
        self.move(520, 300)
        Start_Window(self, self.session)

class Start_Window(QWidget):

    def __init__(self, root, session):
        super(QWidget, self).__init__(root)
        self.env = session.env
        self.env.gui = 1
        self.session = session
        self.root = root
        self.Wtrain = None
        self.Weval = None
        self.Build_Swindow()

    def Build_Swindow(self):
        self.StFrame = QFrame(self)

        gbox = QGroupBox("Settings")

        HBlayout = QHBoxLayout()
        VBlayout = QVBoxLayout()
        VBFrame = QFrame()

        self.VFLayout = QVBoxLayout()

        self.SFrame = QFrame()
        SVbox = QVBoxLayout()

        RBgbox = QGroupBox("Mode")
        HRBlayout = QHBoxLayout()

        self.rbtrain = QRadioButton("Train")
        self.rbeval = QRadioButton("Eval")

        self.rbtrain.toggled.connect(lambda: self.Show_f(self.rbtrain.text()))
        self.rbeval.toggled.connect(lambda: self.Show_f(self.rbeval.text()))

        HRBlayout.addWidget(self.rbtrain)
        HRBlayout.addWidget(self.rbeval)

        HRBlayout.setAlignment(Qt.AlignHCenter)
        HRBlayout.setSpacing(350)

        RBgbox.setLayout(HRBlayout)

        self.next = QPushButton('Next')
        self.leave = QPushButton('Exit')

        self.next.setStyleSheet("QPushButton {color: grey}")

        self.next.clicked.connect(self.lock_error)
        self.leave.clicked.connect(self._end)

        HBlayout.addWidget(self.leave)
        HBlayout.addWidget(self.next)

        VBFrame.setLayout(HBlayout)
        gbox.setLayout(self.VFLayout)
        SVbox.addWidget(gbox)
        self.SFrame.setLayout(SVbox)

        self.lerror = QLabel()

        self.SFrame.hide()

        VBlayout.addWidget(RBgbox)
        VBlayout.addWidget(self.lerror)
        VBlayout.addWidget(self.SFrame)
        VBlayout.addWidget(VBFrame)
        VBlayout.addStretch()

        self.lerror.setAlignment(Qt.AlignHCenter)

        self.StFrame.setLayout(VBlayout)

        self.StFrame.resize(h, w)
        self.root.resize(h, 150)

    def _Build(self, mode):
        Frame = QFrame()
        Frame.setObjectName("Frame"+mode)

        HLayout = QHBoxLayout()
        self.gbox_ms = QGroupBox("Model settings")
        gbox_es = self._build_env_settings(mode)
        gbox_ws = self._build_wallet_settings(mode)
        self.gbox_ms.setLayout(self._build_model_settings(mode))

        HLayout.addWidget(gbox_es)
        HLayout.addWidget(gbox_ws)
        HLayout.addWidget(self.gbox_ms)

        Frame.setLayout(HLayout)

        return Frame

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            else:
                clearLayout(child.layout())

    def Show_f(self, mode):
        if mode == "Train":
            self.StFrame.resize(h, w)
            self.root.resize(h, w)
            self.clearLayout(self.VFLayout)
            self.Wtrain = self.BuildTrain()
            self.VFLayout.addWidget(self.Wtrain)
        elif mode == "Eval":
            self.StFrame.resize(h, 435)
            self.root.resize(h, 435)
            self.clearLayout(self.VFLayout)
            self.Weval = self.BuildEval()
            self.VFLayout.addWidget(self.Weval)

        self.SFrame.show()
        self.error_lst = []
        self.error = False
        self.color_error()
        self.lerror.setText('')
        self.lerror.setStyleSheet("QLabel {background-color : }")

    def BuildTrain(self):
        self.env.mode = "train"
        return self._Build(self.env.mode)

    def BuildEval(self):
        self.env.mode = "eval"
        return self._Build(self.env.mode)

    def lock_error(self):
        if self.error is False:
            self.Build_Primary_Window()

    def check_error(self):
        if len(self.error_lst) > 0:
            self.error = True
        else:
            self.error = False
        self.color_error()

    def del_error(self, name):
        for idx in range(len(self.error_lst)):
            if self.error_lst[idx] == name:
                self.error_lst.pop(idx)
                break

    def add_error(self, name):
        for error in self.error_lst:
            if error == name:
                return 1
        return 0

    def color_error(self):
        if self.error is True:
            self.next.setStyleSheet("QPushButton {color: grey}")
            self.lerror.setStyleSheet("QLabel {background-color : red}")
            txt = ""
            for idx in range(len(self.error_lst)):
                txt += str(self.error_lst[idx])
                if idx + 1 < len(self.error_lst):
                    txt += "\n"
            self.lerror.setText(txt)
        else:
            self.next.setStyleSheet("QPushButton {color: }")
            self.lerror.setStyleSheet("QLabel {background-color : }")
            self.lerror.setText('')

    def check_changed_ur(self, value):
        ur1 = "Update rate >= 1"
        ur0 = "Update rate == 0"
        urnf = "Update rate is not a float"
        if is_float(value):
            ret = float(value)
            if ret >= 1:
                if self.add_error(ur1) == 0:
                    self.error_lst.append(ur1)
                if self.add_error(ur0) == 1:
                    self.del_error(ur0)
                elif self.add_error(urnf) == 1:
                    self.del_error(urnf)
                self.leur.setStyleSheet("QLineEdit {border-color : red}")
            elif ret == 0:
                if self.add_error(ur0) == 0:
                    self.error_lst.append(ur0)
                if self.add_error(ur1) == 1:
                    self.del_error(ur1)
                elif self.add_error(urnf) == 1:
                    self.del_error(urnf)
                self.leur.setStyleSheet("QLineEdit {border-color : red}")
            else:
                self.leur.setStyleSheet("QLineEdit {border-color : }")
                if self.add_error(ur1) == 1:
                    self.del_error(ur1)
                elif self.add_error(urnf) == 1:
                    self.del_error(urnf)
                elif self.add_error(ur0) == 1:
                    self.del_error(ur0)
        else:
            self.leur.setStyleSheet("QLineEdit {border-color : red}")
            if self.add_error(urnf) == 0:
                self.error_lst.append(urnf)
            if self.add_error(ur0) == 1:
                self.del_error(ur0)
            elif self.add_error(ur1) == 1:
                self.del_error(ur1)
        self.check_error()

    def check_changed_lr(self, value):
        lr1 = "Learning rate >= 1"
        lr0 = "Learning rate == 0"
        lrnf = "Learning rate is not a float"
        if is_float(value):
            ret = float(value)
            if ret >= 1:
                if self.add_error(lr1) == 0:
                    self.error_lst.append(lr1)
                if self.add_error(lr0) == 1:
                    self.del_error(lr0)
                elif self.add_error(lrnf) == 1:
                    self.del_error(lrnf)
                self.lelr.setStyleSheet("QLineEdit {border-color : red}")
            elif ret == 0:
                if self.add_error(lr0) == 0:
                    self.error_lst.append(lr0)
                if self.add_error(lr1) == 1:
                    self.del_error(lr1)
                elif self.add_error(lrnf) == 1:
                    self.del_error(lrnf)
                self.lelr.setStyleSheet("QLineEdit {border-color : red}")
            else:
                self.lelr.setStyleSheet("QLineEdit {border-color : }")
                if self.add_error(lr1) == 1:
                    self.del_error(lr1)
                elif self.add_error(lrnf) == 1:
                    self.del_error(lrnf)
                elif self.add_error(lr0) == 1:
                    self.del_error(lr0)
        else:
            self.lelr.setStyleSheet("QLineEdit {border-color : red}")
            if self.add_error(lrnf) == 0:
                self.error_lst.append(lrnf)
            if self.add_error(lr0) == 1:
                self.del_error(lr0)
            elif self.add_error(lr1) == 1:
                self.del_error(lr1)
        self.check_error()

    def check_changed_an(self, name):
        an = "Can\'t find agent"
        Dname = ['DRQN', 'DDRQN']
        names = ['DQN', 'DDQN', 'DDPG', 'EIIE']
        for agent in self.env.agents:
            if name == agent:
                self.lemn.setStyleSheet("QLineEdit {border-color : }")
                if self.add_error(an) == 1:
                    self.del_error(an)
                self.check_error()
                if self.env.mode == "train":
                    if (name in Dname and self.env.model_name not in names) or (name in names and self.env.model_name not in Dname):
                        self.env.model_name = name
                        #self.check_changed_ur(self.env.settings['env']['update_rate'])
                        #self.check_changed_lr(self.env.settings['env']['learning_rate'])
                        self.clearLayout(self.msGlayout)
                        self.gbox_ms.layout().removeItem(self.msGlayout)
                        self.gbox_ms.setLayout(self._build_model_settings(self.env.mode))
                    else:
                        self.env.model_name = name
                return
        self.lemn.setStyleSheet("QLineEdit {border-color : red}")
        if self.add_error(an) == 0:
            self.error_lst.append(an)
        self.check_error()

    def check_changed_dataset(self, data):
        ds = "Can\'t find dataset"
        if os.path.exists("data/"+data+".csv") == False:
            self.lem.setStyleSheet("QLineEdit {border-color : red}")
            if self.add_error(ds) == 0:
                self.error_lst.append(ds)
        else:
            self.lem.setStyleSheet("QLineEdit {border-color : }")
            if self.add_error(ds) == 1:
                self.del_error(ds)
        self.check_error()

    def check_changed_exposure(self):
        mov = "Can\'t take order"
        cap_exposure = self.sbc.value() - (self.sbc.value() * (1 - self.sbexposure.value() / 100))
        max_order_valid = cap_exposure // (self.sbcp.value() + (self.sbmpd.value() * self.sbpv.value()))
        if max_order_valid < self.sbmo.value() // 2:
            self.change_exposure_varcolor('red')
            if self.add_error(mov) == 0:
                self.error_lst.append(mov)
        else:
            self.change_exposure_varcolor('')
            if self.add_error(mov) == 1:
                self.del_error(mov)
        self.check_error()

    def change_exposure_varcolor(self, color):
        self.sbc.setStyleSheet("QSpinBox {border-color : " +color+ "}")
        self.sbexposure.setStyleSheet("QDoubleSpinBox {border-color :" +color +"}")
        self.sbmpd.setStyleSheet("QSpinBox {border-color : " +color+ "}")
        self.sbmo.setStyleSheet("QSpinBox {border-color : "+color+"}")
        self.sbcp.setStyleSheet("QSpinBox {border-color : "+color+"}")
        self.sbpv.setStyleSheet("QSpinBox {border-color : "+color+"}")

    def _build_wallet_settings(self, mode):
        Glayout = QGridLayout()
        gbox = QGroupBox("Wallet and risk settings")

        lc = QLabel('Capital : ')
        self.sbc = QSpinBox()
        self.sbc.setMinimum(100)
        self.sbc.setMaximum(10000000)
        self.sbc.setValue(self.env.wallet.settings['capital'])

        lexposure = QLabel('Exposure : ')
        self.sbexposure = QDoubleSpinBox()
        self.sbexposure.setMinimum(1)
        self.sbexposure.setMaximum(100)
        self.sbexposure.setSingleStep(0.1)
        self.sbexposure.setValue(self.env.wallet.risk_managment['exposure'])

        lmpd = QLabel('Stop loss : ')
        self.sbmpd = QSpinBox()
        self.sbmpd.setMinimum(5)
        self.sbmpd.setMaximum(400)
        self.sbmpd.setValue(self.env.wallet.risk_managment['stop_loss'])

        lmo = QLabel('Max pos : ')
        self.sbmo = QSpinBox()
        self.sbmo.setMinimum(1)
        self.sbmo.setMaximum(1000)
        self.sbmo.setValue(self.env.wallet.risk_managment['max_pos'])

        Glayout.addWidget(lc, 0, 0)
        Glayout.addWidget(self.sbc, 0, 1)
        Glayout.addWidget(lexposure, 1, 0)
        Glayout.addWidget(self.sbexposure, 1, 1)
        Glayout.addWidget(lmpd, 2, 0)
        Glayout.addWidget(self.sbmpd, 2, 1)
        Glayout.addWidget(lmo, 3, 0)
        Glayout.addWidget(self.sbmo, 3, 1)

        self.sbc.valueChanged.connect(self.check_changed_exposure)
        self.sbexposure.valueChanged.connect(self.check_changed_exposure)
        self.sbmpd.valueChanged.connect(self.check_changed_exposure)
        self.sbmo.valueChanged.connect(self.check_changed_exposure)

        gbox.setLayout(Glayout)

        return gbox

    def _build_model_settings(self, mode):
        self.msGlayout = QGridLayout()
        #gbox = QGroupBox("Model settings")

        lmn = QLabel('Agent : ')
        self.lemn = QLineEdit()
        self.lemn.setText(str(self.env.model_name))

        '''
        llr = QLabel('Learning rate : ')
        self.lelr = QLineEdit()
        self.lelr.setText(str(env.hyperparameters['learning_rate']))

        lur = QLabel('Update rate : ')
        self.leur = QLineEdit()
        self.leur.setText(str(env.hyperparameters['update_rate']))

        lg = QLabel('Gamma : ')
        self.leg = QDoubleSpinBox()
        self.leg.setMinimum(0.01)
        self.leg.setMaximum(1)
        self.leg.setSingleStep(0.01)
        self.leg.setValue(env.hyperparameters['gamma'])

        le = QLabel('Epsilon : ')
        self.lee = QDoubleSpinBox()
        self.lee.setMinimum(0.01)
        self.lee.setMaximum(1)
        self.lee.setSingleStep(0.01)
        self.lee.setValue(env.hyperparameters['epsilon'])
        '''

        self.msGlayout.addWidget(lmn, 0, 0)
        self.msGlayout.addWidget(self.lemn, 0, 1)
        '''
        if mode == "train":
            self.msGlayout.addWidget(llr, 1, 0)
            self.msGlayout.addWidget(self.lelr, 1, 1)
            if "DDRQN" == env.model_name or "DDQN" == env.model_name:
                self.msGlayout.addWidget(lur, 2, 0)
                self.msGlayout.addWidget(self.leur, 2, 1)
            self.msGlayout.addWidget(lg, 3, 0)
            self.msGlayout.addWidget(self.leg, 3, 1)
            self.msGlayout.addWidget(le, 4, 0)
            self.msGlayout.addWidget(self.lee, 4, 1)

        self.lelr.textChanged.connect(self.check_changed_lr)
        self.leur.textChanged.connect(self.check_changed_ur)
        '''
        self.lemn.textChanged.connect(self.check_changed_an)

        #gbox.setLayout(Glayout)

        return self.msGlayout

    def _build_env_settings(self, mode):
        Glayout = QGridLayout()
        gbox = QGroupBox("Environnement settings")

        lm = QLabel('Data : ')
        self.lem = QLineEdit()
        self.lem.setText(str(self.env.dataDirectory))

        lcp = QLabel('Contract price : ')
        self.sbcp = QSpinBox()
        self.sbcp.setMaximum(1000)
        self.sbcp.setMinimum(1)
        self.sbcp.setValue(self.env.contract_settings['contract_price'])

        lpv = QLabel('Pip value : ')
        self.sbpv = QSpinBox()
        self.sbpv.setMaximum(1000)
        self.sbpv.setMinimum(1)
        self.sbpv.setValue(self.env.contract_settings['pip_value'])

        ls = QLabel('Spread : ')
        self.sbs = QDoubleSpinBox()
        self.sbs.setMaximum(10)
        self.sbs.setMinimum(0.01)
        self.sbs.setSingleStep(0.01)
        self.sbs.setValue(self.env.contract_settings['spread'])

        lec = QLabel('Episodes : ')
        self.sbec = QSpinBox()
        self.sbec.setMinimum(1)
        self.sbec.setMaximum(10000)
        self.sbec.setValue(self.env.episode_count)

        lws = QLabel('Window size : ')
        self.sbws = QSpinBox()
        self.sbws.setMinimum(1)
        self.sbws.setMaximum(1000)
        self.sbws.setValue(self.env.window_size)

        lbs = QLabel('Batch size : ')
        self.sbbs = QSpinBox()
        self.sbbs.setMinimum(1)
        self.sbbs.setMaximum(1024)
        self.sbbs.setValue(self.env.batch_size)

        Glayout.addWidget(lm, 0, 0)
        Glayout.addWidget(self.lem, 0, 1)
        Glayout.addWidget(lcp, 1, 0)
        Glayout.addWidget(self.sbcp, 1, 1)
        Glayout.addWidget(lpv, 2, 0)
        Glayout.addWidget(self.sbpv, 2, 1)
        Glayout.addWidget(ls, 3, 0)
        Glayout.addWidget(self.sbs, 3, 1)
        if mode == "train":
            Glayout.addWidget(lec, 4, 0)
            Glayout.addWidget(self.sbec, 4, 1)
            Glayout.addWidget(lws, 5, 0)
            Glayout.addWidget(self.sbws, 5, 1)
            Glayout.addWidget(lbs, 6, 0)
            Glayout.addWidget(self.sbbs, 6, 1)

        self.lem.textChanged.connect(self.check_changed_dataset)
        self.sbcp.valueChanged.connect(self.check_changed_exposure)
        self.sbpv.valueChanged.connect(self.check_changed_exposure)

        gbox.setLayout(Glayout)

        return gbox

    def _resize(self):
        self.h = hp
        self.w = wp
        self.root.resize(self.h, self.w)
        self.resize(self.h, self.w)
        self.root.showMaximized()

    def Hide_Swindow(self):
        self.StFrame.hide()

    def Show_Swindow(self):
        self.StFrame.show()

    def _get_env_var(self):
        self.env.dataDirectory = self.lem.text()
        self.env.model_name = self.lemn.text()
        #env.hyperparameters['learning_rate'] = float(self.lelr.text())

        #env.hyperparameters['gamma'] = self.leg.value()
        #env.hyperparameters['epsilon'] = self.lee.value()
        self.env.episode_count = self.sbec.value()
        self.env.window_size = self.sbws.value()
        self.env.batch_size = self.sbbs.value()
        self.env.wallet.settings['capital'] = self.sbc.value()
        self.env.wallet.risk_managment['exposure'] = self.sbexposure.value()
        self.env.wallet.risk_managment['stop_loss'] = self.sbmpd.value()
        self.env.wallet.risk_managment['max_pos'] = self.sbmo.value()
        self.env.contract_settings['pip_value'] = self.sbpv.value()
        self.env.contract_settings['spread'] = self.sbs.value()
        self.env.contract_settings['contract_price'] = self.sbcp.value()

    def Build_Primary_Window(self):
        self.Hide_Swindow()
        self._resize()

        if self.env.mode == "eval":
            self.env.episode_count = 1

        # Getting env settings
        self._get_env_var()
        self.session.setAgent()
        self.session.loadSession()

        #env.init_logger()
        # Save configuration
        #env.logger._save_conf(env)

        self.worker = self.session.getWorker()

        self.worker.sig_step.connect(self.update)
        self.worker.sig_batch.connect(self.batch_up)
        self.worker.sig_episode.connect(self.episode_up)


        VLayout = QVBoxLayout(self)
        HLayout = QHBoxLayout()
        BF = QFrame()

        b_run = QPushButton('Run')
        b_pause = QPushButton('Pause')
        b_resume = QPushButton('Resume')

        b_run.clicked.connect(self.worker.start)
        b_pause.clicked.connect(self.env._pause)
        b_resume.clicked.connect(self.env._resume)

        HLayout.addWidget(b_run)
        HLayout.addWidget(b_pause)
        HLayout.addWidget(b_resume)
        HLayout.addWidget(self.leave)


        self.main_tab = QTabWidget()
        self.overview = OverviewWindow(self.main_tab, self.env)
        self.model = ModelWindow(self.main_tab, self.env)
        self.settings = QWidget()
        self.wallet = WalletWindow(self.main_tab, self.env)
        self.logs = QWidget()

        self.main_tab.addTab(self.overview, 'OverView')
        self.main_tab.addTab(self.model, 'Model')
        self.main_tab.addTab(self.wallet, 'Wallet')
        self.main_tab.addTab(self.logs, 'Logs')
        self.main_tab.addTab(self.settings, 'Settings')

        HLayout.setSpacing(20)

        BF.setLayout(HLayout)
        VLayout.addWidget(self.main_tab)
        VLayout.addWidget(BF)

        self.setLayout(VLayout)

    def _end(self):
        #if env.logger.model_conf_file:
            #env.logger._end()
        self.session._stop()
        sys.exit(0)

    def update(self):
        self.overview.ordr = self.env.manage_orders(self.overview.ordr)
        self.overview.Update_Overview(self.env)
        #self.model.update_step(self.env)
        self.wallet.Update_chart(self.env)

    def batch_up(self):
        #self.model.update_batch(env)
        pass

    def episode_up(self):
        self.model.update_episode(self.env)
