#! /usr/bin/env python3
# -*- coding:utf-8 -*-
"""
UI界面
"""
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QWidget

import ai
import chessboard
import evaluate
from config import Chess, Config, Point


class AI(QtCore.QThread):
    """定义线程类执行AI的算法"""

    finishSignal = QtCore.pyqtSignal(Point)

    def __init__(self, chessboard: chessboard.ChessBoard, role: Chess, parent=None):
        super(AI, self).__init__(parent)
        self.role = role
        self.chessboard = chessboard

    def run(self):
        """独立线程执行"""
        self.ai = ai.Searcher(self.chessboard, self.role, 8)
        (x, y), score = self.ai.search(True, 2)
        print(f"AI searched best move: ({x}, {y}), best score: {score}")
        self.finishSignal.emit(Point(x, y, self.role))


class GoBang(QWidget):
    """UI类"""

    def __init__(self):
        super().__init__()
        self.HSIZE = int(Config.UI_BG_SIZE * 1.2)
        self.WSIZE = int(Config.UI_BG_SIZE * 1.5)
        self.GRID_SIZE = Config.UI_BG_SIZE / (Config.SIZE - 1)
        self.MARGIN = 30

        self.step = 0  # 步数
        self.ui_point = Point(0, 0)
        # AI已下棋，主要是为了加锁，当值是False的时候说明AI正在思考
        self.ai_down = True

        # 初始化UI
        self.initUI()

    def initUI(self):
        """初始化棋盘"""
        self.chessboard = chessboard.ChessBoard()  # 棋盘类
        self.setCursor(Qt.PointingHandCursor)  # 鼠标变成手指形状
        self.setFixedSize(QtCore.QSize(self.WSIZE, self.HSIZE))
        self.setWindowTitle(f"{Config.APP_NAME}-{Config.APP_VERSION}")  # 窗口名称
        self.setWindowIcon(QIcon(Config.CHESS_BLACK))  # 窗口图标

        self.sound_piece = QSound(Config.SOUND_MOVE)  # 加载落子音效
        self.sound_win = QSound(Config.SOUND_WIN)  # 加载胜利音效
        self.sound_defeated = QSound(Config.SOUND_DEFEATED)  # 加载失败音效

        self.black = QPixmap(Config.CHESS_BLACK)
        self.white = QPixmap(Config.CHESS_WHITE)

        self.setMouseTracking(True)
        self.show()

    def paintEvent(self, event):  # 画出指示箭头
        qp = QPainter()
        qp.begin(self)
        self.drawBoardGrid(qp)
        if self.step:
            self.drawCircle(qp)
        qp.end()

    def mousePressEvent(self, e):
        """人类玩家下棋"""
        if e.button() == Qt.LeftButton: # 按下鼠标左键
            if not self.ai_down: # AI 还未下棋
                print("Not your turn!")
                return
            ui_point = Point(e.x(), e.y(), Chess.BLACK)  # 鼠标坐标
            point = self.coord_pixel2map(ui_point)  # 对应棋盘坐标
            if not point:  # 棋子落在棋盘外
                print("Out of chessboard!")
                return
            if not self.chessboard.is_empty(point): # 棋子没有落在空白处
                print(f"Position {point} not empty!")
                return
            self.chessboard.set_state(point)
            self.draw(point)
            print("AI is thinking...")
            self.ai_down = False
            self.ai = AI(self.chessboard, Chess.WHITE)  # 新建线程对象，传入棋盘参数
            self.ai.finishSignal.connect(self.AI_move)  # 结束线程，传出参数
            self.ai.start()  # run

    def AI_move(self, point: Point):
        """轮到AI下棋"""
        if not self.chessboard.is_empty(point): # 棋子没有落在空白处
            raise ValueError(f"Position {point} is not empty!")
        self.chessboard.set_state(point)
        self.ai_down = True

        self.draw(point)

    def draw(self, point: Point):
        """绘制落子位置的棋子图"""
        self.ui_point = self.coord_map2pixel(point)
        label = QLabel(self)
        if point.chess == Chess.BLACK:
            label.setPixmap(self.black)  # 放置黑色棋子
        else:
            label.setPixmap(self.white)  # 放置白色棋子
        label.setVisible(True)  # 图片可视
        label.setScaledContents(True)  # 图片大小根据标签大小可变
        size = Config.UI_CHESS_SIZE
        x = self.ui_point.x - size // 2
        y = self.ui_point.y - size // 2
        label.setGeometry(x, y, size, size)  # 画出棋子
        self.sound_piece.play()  # 落子音效
        self.step += 1  # 步数+1
        if evaluate.Evaluation(self.chessboard, point.chess).check_win():  # 判断输赢
            winner = point.chess
            self.gameover(winner)
        self.update()

    def drawBoardGrid(self, qp: QPainter):
        """绘制棋盘"""
        # 背景颜色
        brush = QBrush(QColor(238, 185, 89, 80))
        qp.setBrush(brush)
        qp.drawRect(0, 0, Config.UI_BG_SIZE + 2 * self.MARGIN, Config.UI_BG_SIZE + 2 * self.MARGIN)
        
        def set_pen(width:int, color:QColor=QColor(0, 0, 200, 70)):
            """切换画笔"""
            pen = QPen(color, width)
            qp.setPen(pen)
        # 网格线
        cnt = 0
        w1, w2 = 1, 2
        set_pen(w1)
        xy = self.MARGIN
        while xy <= Config.UI_BG_SIZE + self.MARGIN:
            cnt += 1
            x1 = int(xy)
            y1 = int(self.MARGIN)
            y2 = int(self.MARGIN + Config.UI_BG_SIZE)            
            qp.drawLine(x1, y1, x1, y2)  # 竖线
            qp.drawLine(y1, x1, y2, x1)  # 横线
            if cnt == Config.SIZE // 2 + 1:
                # 中心线加粗
                set_pen(w2)
                qp.drawLine(x1, y1, x1, y2)  # 竖线
                qp.drawLine(y1, x1, y2, x1)  # 横线
                # 恢复画笔
                set_pen(w1)
            xy += self.GRID_SIZE
        # 中心点
        brush = QBrush(QColor(0, 0, 200, 90))
        qp.setBrush(brush)
        xy = self.MARGIN + round(Config.UI_BG_SIZE / 2)
        x = self.MARGIN + round(self.GRID_SIZE * 3)
        y = self.MARGIN + round(Config.UI_BG_SIZE - self.GRID_SIZE * 3)
        w = 5
        qp.drawRect(xy-w, xy-w, 2*w, 2*w)
        qp.drawRect(x-w, y-w, 2*w, 2*w)
        qp.drawRect(y-w, x-w, 2*w, 2*w)
        qp.drawRect(x-w, x-w, 2*w, 2*w)
        qp.drawRect(y-w, y-w, 2*w, 2*w)

    def drawCircle(self, qp: QPainter):
        """指示当前位置的棋子"""
        pen = QPen(QColor(200, 0, 0, 80), 2)
        qp.setPen(pen)
        size = Config.UI_CHESS_SIZE
        x = self.ui_point.x - size // 2
        y = self.ui_point.y - size // 2
        qp.drawRect(x, y, size, size)

    def coord_map2pixel(self, point: Point):
        """从 chessMap 里的逻辑坐标到 UI 上的绘制坐标的转换"""
        ui_x = point.y * self.GRID_SIZE + self.MARGIN
        ui_y = point.x * self.GRID_SIZE + self.MARGIN
        return Point(int(ui_x), int(ui_y), point.chess)

    def coord_pixel2map(self, ui_point: Point):
        """从 UI 上的绘制坐标到 chessMap 里的逻辑坐标的转换"""
        """从 chessMap 里的逻辑坐标到 UI 上的绘制坐标的转换"""
        x = int(round((ui_point.y - self.MARGIN) / self.GRID_SIZE))
        y = int(round((ui_point.x - self.MARGIN) / self.GRID_SIZE))
        # 排除边缘位置导致坐标越界
        if x < 0 or x >= Config.SIZE or y < 0 or y >= Config.SIZE:
            return None
        else:
            return Point(x, y, ui_point.chess)

    def gameover(self, winner):
        if winner == Chess.BLACK:
            self.sound_win.play()
            reply = QMessageBox.question(self, 'You Win!', 'Congratulations, you win! Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            self.sound_defeated.play()
            reply = QMessageBox.question(self, 'You Lost!', 'Sorry, you lost! Continue?',
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
