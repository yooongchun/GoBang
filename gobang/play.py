#! /usr/bin/env python3
# -*- coding:utf-8 -*-


import sys

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui
from PyQt5.QtMultimedia import QSound
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox

import ai
import config
import chessboard
import evaluate


class AI(QtCore.QThread):
    """定义线程类执行AI的算法"""

    finishSignal = QtCore.pyqtSignal(config.Point)

    def __init__(self, chessboard: chessboard.ChessBoard, role: config.Chess, parent=None):
        super(AI, self).__init__(parent)
        self.role = role
        self.chessboard = chessboard

    def run(self):
        """独立线程执行"""
        self.ai = ai.Searcher(self.chessboard, self.role, 8)
        (x, y), score = self.ai.search(True, 2)
        print(f"AI searched best move: ({x}, {y}), best score: {score}")
        self.finishSignal.emit(config.Point(x, y, self.role))


class GoBang(QWidget):
    """棋盘类"""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """初始化棋盘"""

        self.chessboard = chessboard.ChessBoard()  # 棋盘类
        palette1 = QPalette()  # 设置棋盘背景
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap(config.Config.CHESSBOARD_BG)))
        self.setPalette(palette1)
        self.setCursor(Qt.PointingHandCursor)  # 鼠标变成手指形状

        self.setFixedSize(QtCore.QSize(config.Config.UI_WIDTH, config.Config.UI_HEIGHT))
        self.setWindowTitle(f"{config.Config.APP_NAME}-{config.Config.APP_VERSION}")  # 窗口名称
        self.setWindowIcon(QIcon(config.Config.CHESS_BLACK))  # 窗口图标

        self.sound_piece = QSound(config.Config.SOUND_MOVE)  # 加载落子音效
        self.sound_win = QSound(config.Config.SOUND_WIN)  # 加载胜利音效
        self.sound_defeated = QSound(config.Config.SOUND_DEFEATED)  # 加载失败音效
        
        self.black = QPixmap(config.Config.CHESS_BLACK)
        self.white = QPixmap(config.Config.CHESS_WHITE)

        self.step = 0  # 步数
        self.ui_point = config.Point(0, 0, 0)

        # AI已下棋，主要是为了加锁，当值是False的时候说明AI正在思考，这时候玩家鼠标点击失效，要忽略掉 mousePressEvent
        self.ai_down = True
        self.setMouseTracking(True)
        self.show()

    def paintEvent(self, event):  # 画出指示箭头
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()

    def mousePressEvent(self, e):
        """人类玩家下棋"""
        if e.button() == Qt.LeftButton: # 按下鼠标左键
            if not self.ai_down: # AI 还未下棋
                print("Not your turn!")
                return
            ui_point = config.Point(e.x(), e.y(), config.Chess.BLACK)  # 鼠标坐标
            point = self.coordinate_transform_pixel2map(ui_point)  # 对应棋盘坐标
            if not point:  # 棋子落在棋盘外
                print("Out of chessboard!")
                return
            if self.chessboard.get_state(point) != config.Chess.EMPTY:  # 棋子没有落在空白处
                print("Position not empty!")
                return
            print("Human play!", point)
            self.chessboard.set_state(point)
            self.draw(point)
            print("AI is thinging...")
            self.ai_down = False
            self.ai = AI(self.chessboard, config.Chess.WHITE)  # 新建线程对象，传入棋盘参数
            self.ai.finishSignal.connect(self.AI_move)  # 结束线程，传出参数
            self.ai.start()  # run

    def AI_move(self, point: config.Point):
        """轮到AI下棋"""
        self.chessboard.set_state(point)
        self.ai_down = True

        self.draw(point)
        self.update()

    def draw(self, point: config.Point):
        """绘制落子位置的棋子图"""
        self.ui_point = self.coordinate_transform_map2pixel(point)
        
        label = QLabel(self)
        if point.chess == config.Chess.BLACK:
            label.setPixmap(self.black)  # 放置黑色棋子
        else:
            label.setPixmap(self.white)  # 放置白色棋子
        label.setVisible(True)  # 图片可视
        label.setScaledContents(True)  # 图片大小根据标签大小可变
        label.setGeometry(self.ui_point.x, self.ui_point.y, config.Config.UI_PIECE, config.Config.UI_PIECE)  # 画出棋子
        self.sound_piece.play()  # 落子音效
        self.step += 1  # 步数+1

        if evaluate.Evaluation(self.chessboard, point.chess).check_win():  # 判断输赢
            winner = point.chess
            self.gameover(winner)

    def drawLines(self, qp):
        """指示AI当前下的棋子"""
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(self.ui_point.x - 5, self.ui_point.y - 5, self.ui_point.x + 3, self.ui_point.y + 3)
        qp.drawLine(self.ui_point.x + 3, self.ui_point.y, self.ui_point.x + 3, self.ui_point.y + 3)
        qp.drawLine(self.ui_point.x, self.ui_point.y + 3, self.ui_point.x + 3, self.ui_point.y + 3)

    def coordinate_transform_map2pixel(self, point: config.Point):
        """从 chessMap 里的逻辑坐标到 UI 上的绘制坐标的转换"""
        ui_x = config.Config.UI_MARGIN + point.y * config.Config.UI_GRID - config.Config.UI_PIECE / 2
        ui_y = config.Config.UI_MARGIN + point.x * config.Config.UI_GRID - config.Config.UI_PIECE / 2     
        return config.Point(int(ui_x), int(ui_y), point.chess)

    def coordinate_transform_pixel2map(self, ui_point: config.Point):
        """从 UI 上的绘制坐标到 chessMap 里的逻辑坐标的转换"""
        x = int(round((ui_point.y - config.Config.UI_MARGIN) / config.Config.UI_GRID))
        y = int(round((ui_point.x - config.Config.UI_MARGIN) / config.Config.UI_GRID))
        # 有MAGIN, 排除边缘位置导致坐标越界
        if x < 0 or x >= config.Config.SIZE or y < 0 or y >= config.Config.SIZE:
            return None
        else:
            return config.Point(x, y, ui_point.chess)

    def gameover(self, winner):
        if winner == config.Chess.BLACK:
            self.sound_win.play()
            reply = QMessageBox.question(self, 'You Win!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            self.sound_defeated.play()
            reply = QMessageBox.question(self, 'You Lost!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:  # 复位
            self.step = 0
            self.chessboard.reset()
            self.update()
        else:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GoBang()
    sys.exit(app.exec_())
