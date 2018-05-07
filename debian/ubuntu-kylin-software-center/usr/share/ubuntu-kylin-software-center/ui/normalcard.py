#!/usr/bin/python
# -*- coding: utf-8 -*-

### BEGIN LICENSE

# Copyright (C) 2013 National University of Defense Technology(NUDT) & Kylin Ltd

# Author:
#     Shine Huang<shenghuang@ubuntukylin.com>
# Maintainer:
#     Shine Huang<shenghuang@ubuntukylin.com>

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui.uknormalcard import Ui_NormalCard
from ui.starwidget import StarWidget
from utils import run
from utils import commontools
from models.enums import (ITEM_LABEL_STYLE,UBUNTUKYLIN_RES_ICON_PATH,AppActions)
from models.enums import Signals, setLongTextToElideFormat, PkgStates, PageStates
from models.globals import Globals

class NormalCard(QWidget):

    def __init__(self, app, messageBox, parent=None):#nowpage, prepage,
        QWidget.__init__(self, parent)
        self.ui_init()

        self.app = app
        # self.workType = nowpage
        # self.preType = prepage
        self.messageBox = messageBox

        self.switchTimer = QTimer(self)
        self.switchTimer.timeout.connect(self.slot_switch_animation_step)

        # add by kobe: delay show animation
        self.showDelay = False
        self.delayTimer = QTimer(self)
        self.delayTimer.timeout.connect(self.slot_show_delay_animation)

        self.ui.btn.setFocusPolicy(Qt.NoFocus)
        self.ui.btnDetail.setFocusPolicy(Qt.NoFocus)

        self.ui.btnDetail.setCursor(Qt.PointingHandCursor)

        self.ui.description.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.description.setReadOnly(True)

        # self.ui.baseWidget.setAutoFillBackground(True)
        # palette = QPalette()
        # palette.setColor(QPalette.Background, QColor(245, 248, 250))
        # self.ui.baseWidget.setPalette(palette)

        self.ui.baseWidget.setAutoFillBackground(True)
        palette = QPalette()
        img = QPixmap("res/ncard-base.png")
        palette.setBrush(QPalette.Window, QBrush(img))
        self.ui.baseWidget.setPalette(palette)

        # self.ui.detailWidget.setAutoFillBackground(True)
        # palette = QPalette()
        # palette.setColor(QPalette.Background, QColor(245, 248, 250))
        # self.ui.detailWidget.setPalette(palette)

        self.ui.detailWidget.setAutoFillBackground(True)
        palette = QPalette()
        img = QPixmap("res/ncard-base.png")
        palette.setBrush(QPalette.Window, QBrush(img))
        self.ui.detailWidget.setPalette(palette)

        palette = QPalette()
        palette.setBrush(QPalette.Base, QBrush(QColor(255,0,0,0)))
        self.ui.description.setPalette(palette)

        # component shadow
        # shadowe = QGraphicsDropShadowEffect(self)
        # shadowe.setOffset(-2, 2)    # direction
        # shadowe.setColor(Qt.gray)
        # shadowe.setBlurRadius(4)
        # self.setGraphicsEffect(shadowe)

        iconpath = commontools.get_icon_path(self.app.name)
        self.ui.icon.setStyleSheet("QLabel{background-image:url('" + iconpath + "')}")
        self.ui.progressBar_icon.setStyleSheet("QLabel{background-image:url('" + iconpath + "')}")

        # self.ui.baseWidget.setStyleSheet("QWidget{border:0px;}")
        self.ui.name.setStyleSheet("QLabel{font-size:13px;font-weight:bold;color:#666666;}")
        self.ui.named.setStyleSheet("QLabel{font-size:13px;font-weight:bold;color:#666666;}")
        self.ui.size.setStyleSheet("QLabel{font-size:13px;color:#888888;}")
        self.ui.isInstalled.setStyleSheet("QLabel{font-size:13px;color:#888888;}")
        self.ui.description.setStyleSheet("QTextEdit{border:0px;font-size:13px;color:#888888;}")

        # letter spacing
        # font = QFont()
        # font.setLetterSpacing(QFont.PercentageSpacing, 90.0)
        # self.ui.name.setFont(font)
        # self.ui.description.setFont(font)
        # if(len(self.app.displayname) > 20):
        #     font2 = QFont()
        #     font2.setLetterSpacing(QFont.PercentageSpacing, 80.0)
        #     self.ui.name.setFont(font2)
        #     self.ui.name.setStyleSheet("QLabel{font-size:13px;font-weight:bold;color:#666666;}")
        # if(len(self.app.displayname) > 24):
        #     font2 = QFont()
        #     font2.setLetterSpacing(QFont.PercentageSpacing, 80.0)
        #     self.ui.name.setFont(font2)
        #     self.ui.name.setStyleSheet("QLabel{font-size:12px;font-weight:bold;color:#666666;}")

        # convert size
        installedsize = self.app.installedSize
        installedsizek = installedsize / 1024
        if(installedsizek < 1024):
            self.ui.size.setText(str(installedsizek) + " KB")
        else:
            self.ui.size.setText(str('%.2f'%(installedsizek/1024.0)) + " MB")

        # add by kobe
        if self.app.displayname_cn != '' and self.app.displayname_cn is not None and self.app.displayname_cn != 'None':
            setLongTextToElideFormat(self.ui.name, self.app.displayname_cn)
            setLongTextToElideFormat(self.ui.named, self.app.displayname_cn)
        else:
            setLongTextToElideFormat(self.ui.name, self.app.displayname)
            setLongTextToElideFormat(self.ui.named, self.app.displayname)

        if self.app.summary is not None and self.app.summary != 'None' and self.app.summary != '':
            self.ui.description.setText(self.app.summary)
        else:
            self.ui.description.setText(self.app.orig_summary)

        self.ui.isInstalled.setText("已安装")
        # rating star
        self.star = StarWidget("small", self.app.ratings_average, self.ui.baseWidget)
        self.star.move(75, 56)

        # btn & border
        # if ( self.app.percent > 0 and self.app.percent < 200 ) or (self.app.status in (PkgStates.INSTALLING, PkgStates.REMOVING, PkgStates.UPGRADING) and self.app.percent == 0):
        if self.app.status in (PkgStates.INSTALLING, PkgStates.REMOVING, PkgStates.UPGRADING):
            self.ui.progressBar.setVisible(True)
            self.ui.progresslabel.setVisible(True)
            self.ui.progressBar_icon.setVisible(True)
            self.ui.progressBar.setValue(self.app.percent)
            self.ui.progresslabel.setText(str('%.0f' % self.app.percent) + '%')

            if self.app.status == PkgStates.INSTALLING:
                self.ui.btn.setEnabled(False)
                if self.app.percent > 0:
                    self.ui.btn.setText("正在安装")
                else:
                    self.ui.btn.setText("等待安装")
                self.star.show()

                self.ui.isInstalled.setVisible(False)
                self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
                                             "QProgressBar:chunk{background-color:#BBF9A3;}")
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-install-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-install-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-install-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-install-border.png');}")
            elif self.app.status == PkgStates.REMOVING:
                self.ui.btn.setEnabled(False)
                if self.app.percent > 0:
                    self.ui.btn.setText("正在卸载")
                else:
                    self.ui.btn.setText("等待卸载")
                if (Globals.NOWPAGE in (PageStates.UPPAGE,PageStates.UNPAGE,PageStates.SEARCHUPPAGE,PageStates.SEARCHUNPAGE)):
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                else:
                    self.star.hide()
                    self.ui.isInstalled.setVisible(True)
                self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
                                                  "QProgressBar:chunk{background-color:#C5CED9;}")
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
            elif self.app.status == PkgStates.UPGRADING:
                self.ui.btn.setEnabled(False)
                if self.app.percent > 0:
                    self.ui.btn.setText("正在升级")
                else:
                    self.ui.btn.setText("等待升级")
                self.star.hide()
                if (Globals.NOWPAGE in (PageStates.UPPAGE,PageStates.UNPAGE,PageStates.SEARCHUPPAGE,PageStates.SEARCHUNPAGE)):
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                else:
                    self.star.hide()
                    self.ui.isInstalled.setVisible(True)
                self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
                                             "QProgressBar:chunk{background-color:#FDD99A;}")
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")

            self.star.hide()

        else:
            if(Globals.NOWPAGE == PageStates.ALLPAGE or Globals.NOWPAGE == PageStates.HOMEPAGE ):
                if(self.app.is_installed):
                    # add by kobe
                    self.star.hide()
                    self.ui.isInstalled.setVisible(True)
                    if(run.get_run_command(self.app.name) == ""):
                        # init app.status
                        self.app.status = PkgStates.NORUN
                        self.ui.btn.setText("已安装")
                        self.ui.btn.setEnabled(False)
                        self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                        self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                    else:
                        # init app.status
                        self.app.status = PkgStates.RUN
                        self.ui.btn.setText("启动")
                        self.ui.btn.setEnabled(True)
                        self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-run-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-run-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-run-btn-3.png');}")
                        self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-run-border.png');}")
                else:
                    # init app.status
                    self.app.status = PkgStates.INSTALL
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                    self.ui.btn.setText("安装")
                    self.ui.btn.setEnabled(True)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-install-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-install-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-install-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-install-border.png');}")

            elif(Globals.NOWPAGE == PageStates.UPPAGE):
                # init app.status
                self.app.status = PkgStates.UPDATE
                self.star.show()
                self.ui.isInstalled.setVisible(False)
                self.ui.btn.setText("升级")
                self.ui.btn.setEnabled(True)
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")

            elif(Globals.NOWPAGE == PageStates.UNPAGE):
                # init app.status
                self.app.status = PkgStates.UNINSTALL
                self.star.show()
                self.ui.isInstalled.setVisible(False)
                self.ui.btn.setText("卸载")
                self.ui.btn.setEnabled(True)
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")

            elif(Globals.NOWPAGE in (PageStates.SEARCHHOMEPAGE,PageStates.SEARCHALLPAGE,PageStates.SEARCHWINPAGE,PageStates.SEARCHUAPAGE,PageStates.SEARCHTRANSPAGE)):#zx11.27
                if(self.app.is_installed):
                    self.star.hide()
                    self.ui.isInstalled.setVisible(True)
                    if(run.get_run_command(self.app.name) == ""):
                        # init app.status
                        self.app.status = PkgStates.NORUN
                        self.ui.btn.setText("已安装")
                        self.ui.btn.setEnabled(False)
                        self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                        self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                    else:
                        # init app.status
                        self.app.status = PkgStates.RUN
                        self.ui.btn.setText("启动")
                        self.ui.btn.setEnabled(True)
                        self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-run-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-run-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-run-btn-3.png');}")
                        self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-run-border.png');}")
                else:
                    # init app.status
                    self.app.status = PkgStates.INSTALL
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                    self.ui.btn.setText("安装")
                    self.ui.btn.setEnabled(True)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-install-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-install-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-install-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-install-border.png');}")
            elif(Globals.NOWPAGE == PageStates.SEARCHUPPAGE): #zx 11.27
                # init app.status
                self.app.status = PkgStates.UPDATE
                self.star.show()
                self.ui.isInstalled.setVisible(False)
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")
                if self.app.is_installed is True and self.app.is_upgradable is True:
                    self.ui.btn.setText("升级")
                    self.ui.btn.setEnabled(True)
                else:
                    self.ui.btn.setText("无法升级")
                    self.ui.btn.setEnabled(False)
            elif(Globals.NOWPAGE == PageStates.SEARCHUNPAGE):
                # init app.status
                self.app.status = PkgStates.UNINSTALL
                # add by kobe, Fixed Bug #1373740
                self.star.show()
                self.ui.isInstalled.setVisible(False)
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                if self.app.is_installed:
                    self.ui.btn.setText("卸载")
                    self.ui.btn.setEnabled(True)
                else:
                    self.ui.btn.setText("无法卸载")
                    self.ui.btn.setEnabled(False)

            # if self.app.percent < 0:
            #     self.star.hide()
            #     self.ui.progressBar.setVisible(True)
            #     self.ui.progresslabel.setVisible(True)
            #     self.ui.progressBar_icon.setVisible(True)
            #     self.ui.progressBar.setValue(0)
            #     self.ui.progresslabel.setText("失败")
            #     self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
            #                                  "QProgressBar:chunk{background-color:#BBF9A3;}")

        self.ui.btn.clicked.connect(self.slot_btn_click)
        self.ui.btnDetail.clicked.connect(self.slot_emit_detail)

    def ui_init(self):
        self.ui = Ui_NormalCard()
        self.ui.setupUi(self)
        self.show()

    def enterEvent(self, event):
        if hasattr(self, "delayTimer"): #if there is app in install upgrade or uninstall in uksc starting there will be error
            self.delayTimer.start(300)
        # self.switchDirection = 'down'
        # self.switch_animation()

    def leaveEvent(self, event):
        if self.delayTimer.isActive():
            self.delayTimer.stop()
        if self.showDelay:
            self.showDelay = False
            self.switchDirection = 'up'
            self.switch_animation()

    def slot_show_delay_animation(self):
        self.delayTimer.stop()
        self.switchDirection = 'down'
        self.switch_animation()
        self.showDelay = True

    def switch_animation(self):
        if(self.switchDirection == 'down'):
            self.py = -88
            self.switchTimer.stop()
            self.switchTimer.start(12)
        else:
            self.py = 0
            self.switchTimer.stop()
            self.switchTimer.start(12)

    def slot_switch_animation_step(self):
        if(self.switchDirection == 'down'):
            if(self.py < 0):
                self.py += 4
                self.ui.detailWidget.move(0, self.py)
                self.ui.baseWidget.move(0, self.py + 88)
            else:
                self.switchTimer.stop()
                self.ui.detailWidget.move(0, 0)
                self.ui.baseWidget.move(0, 0 + 88)
        else:
            if(self.py > -88):
                self.py -= 4
                self.ui.detailWidget.move(0, self.py)
                self.ui.baseWidget.move(0, self.py + 88)
            else:
                self.switchTimer.stop()
                self.ui.detailWidget.move(0, -88)
                self.ui.baseWidget.move(0, 0)

    def slot_btn_click(self):
        if(self.ui.btn.text() == "启动"):
            self.app.run()
        else:
            self.ui.btn.setEnabled(False)
            if(self.ui.btn.text() == "安装"):
                self.app.status = PkgStates.INSTALLING
                self.ui.btn.setText("等待安装")
                self.slot_show_progress("install")
                self.emit(Signals.install_app, self.app)
                self.emit(Signals.get_card_status, self.app.name, PkgStates.INSTALLING)
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-install-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-install-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-install-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-install-border.png');}")

            elif(self.ui.btn.text() == "升级"):
                self.app.status = PkgStates.UPGRADING
                self.ui.btn.setText("等待升级")
                self.slot_show_progress("upgrade")
                self.emit(Signals.upgrade_app, self.app)
                self.emit(Signals.get_card_status, self.app.name, PkgStates.UPGRADING)
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")

            elif(self.ui.btn.text() == "卸载"):
                if self.app.name == "ubuntu-kylin-software-center":
                    self.emit(Signals.uninstall_uksc_or_not, "normalcard")
                else:
                    self.app.status = PkgStates.REMOVING
                    self.ui.btn.setText("等待卸载")
                    self.slot_show_progress("remove")
                    self.emit(Signals.remove_app, self.app)
                    self.emit(Signals.get_card_status, self.app.name, PkgStates.REMOVING)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")

    def uninstall_uksc(self, where):
        if where == "normalcard":
            self.app.status = PkgStates.REMOVING
            self.ui.btn.setText("等待卸载")
            self.emit(Signals.remove_app, self.app)
            self.emit(Signals.get_card_status, self.app.name, PkgStates.REMOVING)
            self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
            self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")

    def cancel_uninstall_uksc(self, where):
        if where == "normalcard":
            self.ui.btn.setEnabled(True)

    # wb
    def slot_show_progress(self,status):
        self.ui.progressBar.setVisible(True)
        self.ui.progresslabel.setVisible(True)
        self.ui.progressBar_icon.setVisible(True)
        self.star.setVisible(False)
        if status == "install":
            self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
                                              "QProgressBar:chunk{background-color:#BBF9A3;}")
        elif status == "upgrade":
            self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
                                              "QProgressBar:chunk{background-color:#FDD99A;}")
        else:
            self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
                                            "QProgressBar:chunk{background-color:#C5CED9;}")
        #self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
        #                                    "QProgressBar:chunk{background-color:#5DC4FE;}")#text-align:right;
        self.ui.progressBar.setRange(0,100)
        self.ui.progresslabel.setText(str(0) + '%')
        self.ui.progressBar.reset()

    def slot_progress_change(self, pkgname, percent, status):
        if self.app.name == pkgname:
            self.ui.progressBar.setVisible(True)
            self.ui.progresslabel.setVisible(True)
            self.ui.progressBar_icon.setVisible(True)
            self.star.setVisible(False)
            if status == AppActions.INSTALL:
                self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
                                             "QProgressBar:chunk{background-color:#BBF9A3;}")
                self.ui.btn.setText("正在安装")
            elif status == AppActions.UPGRADE:
                self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
                                             "QProgressBar:chunk{background-color:#FDD99A;}")
                self.ui.btn.setText("正在升级")
            elif status == AppActions.REMOVE:
                self.ui.progressBar.setStyleSheet("QProgressBar{background-color:#F4F8FB;border:0px;border-radius:0px;color:#1E66A4;}"
                                           "QProgressBar:chunk{background-color:#C5CED9;}")
                self.ui.btn.setText("正在卸载")
            self.ui.progressBar.setValue(percent)
            if percent < float(0.0):
                self.ui.progressBar.setValue(0)
                self.ui.progresslabel.setText("失败")
            else:
                self.ui.progresslabel.setText(str('%.0f' % percent) + '%')

    def slot_progress_finish(self,pkgname):
        if self.app.name == pkgname:
            self.ui.progresslabel.setVisible(False)
            self.ui.progressBar_icon.setVisible(False)
            self.ui.progressBar.setVisible(False)
            #self.star.setVisible(True)
            self.ui.progressBar.reset()

    def slot_progress_cancel(self, pkgname):
        if self.app.name == pkgname:
            self.ui.progresslabel.setVisible(False)
            self.ui.progressBar_icon.setVisible(False)
            self.ui.progressBar.setVisible(False)
            #self.star.setVisible(True)
            self.ui.progressBar.reset()

    # kobe 1106
    def slot_change_btn_status(self, pkgname, status):
        if self.app.name == pkgname:
            self.ui.btn.setEnabled(False)
            if status == PkgStates.INSTALLING:
                self.app.status = PkgStates.INSTALLING
                if self.app.percent > 0:
                    self.ui.btn.setText("正在安装")
                else:
                    self.ui.btn.setText("等待安装")
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-install-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-install-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-install-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-install-border.png');}")
            elif status == PkgStates.REMOVING:
                self.app.status = PkgStates.REMOVING
                if self.app.percent > 0:
                    self.ui.btn.setText("正在卸载")
                else:
                    self.ui.btn.setText("等待卸载")
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")

            elif status == PkgStates.UPGRADING:
                self.app.status = PkgStates.UPGRADING
                if self.app.percent > 0:
                    self.ui.btn.setText("正在升级")
                else:
                    self.ui.btn.setText("等待升级")
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")


    def slot_emit_detail(self):
        self.emit(Signals.show_app_detail, self.app)

    def slot_work_finished(self, pkgname, action):
        if self.app.name == pkgname:
            if action in (AppActions.INSTALL,AppActions.INSTALLDEBFILE):
                if(Globals.NOWPAGE in (PageStates.UNPAGE,PageStates.SEARCHUNPAGE)):
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                    self.app.status = PkgStates.UNINSTALL
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                    #if self.app.is_installed:#why app.is_installed is false
                    self.ui.btn.setText("卸载")
                    self.ui.btn.setEnabled(True)
                elif(Globals.NOWPAGE in (PageStates.UPPAGE,PageStates.SEARCHUPPAGE)):
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                    if(run.get_run_command(self.app.name) == ""):
                        self.app.status = PkgStates.NORUN
                    else:
                        self.app.status = PkgStates.RUN
                    self.ui.btn.setText("无法升级")
                    self.ui.btn.setEnabled(False)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")
                else:
                    self.star.hide()
                    self.ui.isInstalled.setVisible(True)
                    if(run.get_run_command(self.app.name) == ""):
                        self.app.status = PkgStates.NORUN
                        self.ui.btn.setText("已安装")
                        self.ui.btn.setEnabled(False)
                        self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                        self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                    else:
                        self.app.status = PkgStates.RUN
                        self.ui.btn.setText("启动")
                        self.ui.btn.setEnabled(True)
                        self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-run-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-run-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-run-btn-3.png');}")
                        self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-run-border.png');}")
            elif action == AppActions.REMOVE:
                self.app.status = PkgStates.INSTALL
                self.star.show()
                self.ui.isInstalled.setVisible(False)
                self.ui.btn.setText("安装")
                self.ui.btn.setEnabled(True)
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-install-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-install-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-install-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-install-border.png');}")
            elif action == AppActions.UPGRADE:
                if(Globals.NOWPAGE in (PageStates.UPPAGE,PageStates.SEARCHUPPAGE,PageStates.UNPAGE,PageStates.SEARCHUNPAGE)):
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                else:
                    self.star.hide()
                    self.ui.isInstalled.setVisible(True)
                if(run.get_run_command(self.app.name) == ""):
                    self.app.status = PkgStates.NORUN
                    self.ui.btn.setText("已安装")
                    self.ui.btn.setEnabled(False)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                else:
                    self.app.status = PkgStates.RUN
                    self.ui.btn.setText("启动")
                    self.ui.btn.setEnabled(True)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-run-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-run-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-run-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-run-border.png');}")

    def slot_work_cancel(self, pkgname, action):
        if self.app.name == pkgname:
            if action == AppActions.INSTALL:
                self.app.status = PkgStates.INSTALL
                self.star.show()
                self.ui.isInstalled.setVisible(False)
                self.ui.btn.setText("安装")
                self.ui.btn.setEnabled(True)
                self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-install-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-install-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-install-btn-3.png');}")
                self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-install-border.png');}")
            elif action == AppActions.REMOVE:
                if (Globals.NOWPAGE in (PageStates.UPPAGE,PageStates.UNPAGE,PageStates.SEARCHUPPAGE,PageStates.SEARCHUNPAGE)):
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                else:
                    self.star.hide()
                    self.ui.isInstalled.setVisible(True)
                if Globals.NOWPAGE in (PageStates.UPPAGE, PageStates.SEARCHUPPAGE):
                    self.ui.btn.setText("升级")
                    self.app.status = PkgStates.UPDATE
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")
                else:
                    self.ui.btn.setText("卸载")
                    self.app.status = PkgStates.UNINSTALL
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                self.ui.btn.setEnabled(True)
            elif action == AppActions.UPGRADE:
                if (Globals.NOWPAGE in (PageStates.UPPAGE,PageStates.UNPAGE,PageStates.SEARCHUPPAGE,PageStates.SEARCHUNPAGE)):
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                else:
                    self.star.hide()
                    self.ui.isInstalled.setVisible(True)
                if Globals.NOWPAGE in (PageStates.UNPAGE, PageStates.SEARCHUNPAGE):
                    self.app.status = PkgStates.UNINSTALL
                    self.ui.btn.setText("卸载")
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                else:
                    self.app.status = PkgStates.UPDATE
                    self.ui.btn.setText("升级")
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")
                self.ui.btn.setEnabled(True)
            elif action == AppActions.INSTALLDEBFILE:
                if(Globals.NOWPAGE == PageStates.ALLPAGE or Globals.NOWPAGE == PageStates.HOMEPAGE ):
                    if(self.app.is_installed):
                        # add by kobe
                        self.star.hide()
                        self.ui.isInstalled.setVisible(True)
                        if(run.get_run_command(self.app.name) == ""):
                            # init app.status
                            self.app.status = PkgStates.NORUN
                            self.ui.btn.setText("已安装")
                            self.ui.btn.setEnabled(False)
                            self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                            self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                        else:
                            # init app.status
                            self.app.status = PkgStates.RUN
                            self.ui.btn.setText("启动")
                            self.ui.btn.setEnabled(True)
                            self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-run-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-run-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-run-btn-3.png');}")
                            self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-run-border.png');}")
                    else:
                        # init app.status
                        self.app.status = PkgStates.INSTALL
                        self.star.show()
                        self.ui.isInstalled.setVisible(False)
                        self.ui.btn.setText("安装")
                        self.ui.btn.setEnabled(True)
                        self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-install-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-install-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-install-btn-3.png');}")
                        self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-install-border.png');}")

                elif(Globals.NOWPAGE == PageStates.UPPAGE):
                    # init app.status
                    self.app.status = PkgStates.UPDATE
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                    self.ui.btn.setText("升级")
                    self.ui.btn.setEnabled(True)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")

                elif(Globals.NOWPAGE == PageStates.UNPAGE):
                    # init app.status
                    self.app.status = PkgStates.UNINSTALL
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                    self.ui.btn.setText("卸载")
                    self.ui.btn.setEnabled(True)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")

                elif(Globals.NOWPAGE in (PageStates.SEARCHHOMEPAGE,PageStates.SEARCHALLPAGE,PageStates.SEARCHWINPAGE,PageStates.SEARCHUAPAGE,PageStates.SEARCHTRANSPAGE)):#zx11.27
                    if(self.app.is_installed):
                        self.star.hide()
                        self.ui.isInstalled.setVisible(True)
                        if(run.get_run_command(self.app.name) == ""):
                            # init app.status
                            self.app.status = PkgStates.NORUN
                            self.ui.btn.setText("已安装")
                            self.ui.btn.setEnabled(False)
                            self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                            self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                        else:
                            # init app.status
                            self.app.status = PkgStates.RUN
                            self.ui.btn.setText("启动")
                            self.ui.btn.setEnabled(True)
                            self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-run-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-run-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-run-btn-3.png');}")
                            self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-run-border.png');}")
                    else:
                        # init app.status
                        self.app.status = PkgStates.INSTALL
                        self.star.show()
                        self.ui.isInstalled.setVisible(False)
                        self.ui.btn.setText("安装")
                        self.ui.btn.setEnabled(True)
                        self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-install-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-install-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-install-btn-3.png');}")
                        self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-install-border.png');}")
                elif(Globals.NOWPAGE == PageStates.SEARCHUPPAGE): #zx 11.27
                    # init app.status
                    self.app.status = PkgStates.UPDATE
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-up-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-up-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-up-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-up-border.png');}")
                    if self.app.is_installed is True and self.app.is_upgradable is True:
                        self.ui.btn.setText("升级")
                        self.ui.btn.setEnabled(True)
                    else:
                        self.ui.btn.setText("无法升级")
                        self.ui.btn.setEnabled(False)
                elif(Globals.NOWPAGE == PageStates.SEARCHUNPAGE):
                    # init app.status
                    self.app.status = PkgStates.UNINSTALL
                    # add by kobe, Fixed Bug #1373740
                    self.star.show()
                    self.ui.isInstalled.setVisible(False)
                    self.ui.btn.setStyleSheet("QPushButton{color:white;border:0px;background-image:url('res/ncard-un-btn-1.png');}QPushButton:hover{border:0px;background-image:url('res/ncard-un-btn-2.png');}QPushButton:pressed{border:0px;background-image:url('res/ncard-un-btn-3.png');}")
                    self.ui.btnDetail.setStyleSheet("QPushButton{border:0px;background-image:url('res/ncard-un-border.png');}")
                    if self.app.is_installed:
                        self.ui.btn.setText("卸载")
                        self.ui.btn.setEnabled(True)
                    else:
                        self.ui.btn.setText("无法卸载")
                        self.ui.btn.setEnabled(False)

            # if self.app.percent < 0:
            #     self.star.hide()