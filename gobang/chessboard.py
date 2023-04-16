# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import numpy as np
import pandas as pd

import config


class Point(object):
    """定义点对象"""
    def __init__(self, x: int, y: int, val: int=config.State.EMPTY):
        self.x = x
        self.y = y
        self.state = val
    
    def __repr__(self) -> str:
        return f"Point({self.x},{self.y}):config.State({self.state})"

    def __str__(self) -> str:
        return self.__repr__()


class ChessBoard(object):
    """定义棋盘类，绘制棋盘的形状，切换先后手，判断输赢等"""
    def __init__(self, size=config.Config.SIZE, win_num=config.Config.WIN_NUM):
        self.size = size
        self.win_num = win_num # 赢棋的最少连子个数
        assert size < config.State.WHITE, "the size is too large!"
        self._board = [[config.State.EMPTY for _ in range(size)] for _ in range(size)]

    def board(self):
        """棋盘"""
        return self._board

    def set_state(self, point:Point):
        """落子"""
        if self._board[point.x][point.y] != config.State.EMPTY:
            return False
        if point.x < 0 or point.x >= self.size or point.y < 0 or point.y >= self.size:
            return False
        self._board[point.x][point.y] = point.state
        return True

    def clear_state(self, point:Point):
        """落子"""
        assert 0 <= point.x < self.size, "Invalid point.x"
        assert 0 <= point.y < self.size, "Invalid point.y"
        assert point.state in [config.State.BLACK, config.State.WHITE, config.State.EMPTY], "Invalid point.state"
        
        self._board[point.x][point.y] = config.State.EMPTY
        return True

    def get_state(self, point:Point):
        """获取指定点坐标的状态"""
        assert 0 <= point.x < self.size, "Invalid point.x"
        assert 0 <= point.y < self.size, "Invalid point.y"

        return self._board[point.x][point.y]

    def line_win(self, line):
        """判断给定直线上是否有满足赢棋"""
        line = np.cumsum(line)
        lmax = line.max()
        # 白棋赢
        if lmax // config.State.WHITE >= self.win_num:
            return config.State.WHITE
        # 黑棋赢
        elif (lmax%config.State.WHITE) // config.State.BLACK >= self.win_num:
            return config.State.BLACK
        # 平局: 当前局面已经无子可下
        if np.min(self._board) != config.State.EMPTY:
            return config.State.EMPTY
        # 无人赢
        return False

    def _hwin(self, point:Point):
        """水平方向是否有赢棋"""
        # 取出point位置前后4个点范围内的4条线
        xstart = max(point.x-self.win_num+1, 0)
        xend = min(self.size, point.x+self.win_num)
        hline = [self.get_state(Point(x, point.y)) for x in range(xstart, xend)]
        return self.line_win(hline)
    
    def _vwin(self, point:Point):
        """竖直方向是否有赢棋"""
        # 取出point位置前后4个点范围内的4条线
        ystart = max(point.y-self.win_num+1, 0)
        yend = min(self.size, point.y+self.win_num)
        vline = [self.get_state(Point(point.x, y)) for y in range(ystart, yend)]
        return self.line_win(vline)

    def _swin(self, point:Point):
        """正斜线方向是否有赢棋"""
        xstart = point.x
        ystart = point.y
        step = self.win_num - 1
        while xstart > 0 and ystart > 0 and step > 0:
            xstart -= 1
            ystart -= 1
            step -= 1
        xend = point.x
        yend = point.y
        step = self.win_num
        while xend < self.size and yend < self.size and step > 0:
            xend += 1
            yend += 1
            step -= 1
        sline = [self.get_state(Point(x, y)) for x, y in zip(range(xstart, xend), range(ystart, yend))]
        return self.line_win(sline)
    
    def _rwin(self, point:Point):
        """反斜线方向是否有赢棋"""
        xstart = point.x
        yend = point.y
        step = self.win_num
        while xstart > 0 and yend < self.size and step > 0:
            xstart -= 1
            yend += 1
            step -= 1
        xend = point.x
        ystart = point.y
        step = self.win_num
        while xend < self.size and ystart > 0 and step > 0:
            xend += 1
            ystart -= 1
            step -= 1
        rline = [self.get_state(Point(x, y)) for x, y in zip(range(xstart, xend+1), range(yend, ystart-1, -1))]
        return self.line_win(rline)
    
    def check_win(self, point:Point):
        """当把x,y位置落子之后, 局面是否有赢家,num表示至少需要num个子连珠"""
        if not self.set_state(point):
            return False
        # 水平方向是否有赢棋
        state = self._hwin(point)
        if state != False:
            self.clear_state(point)
            return state
        # 竖直方式是否有赢棋
        state = self._vwin(point)
        if state != False:
            self.clear_state(point)
            return state
        # 正斜线方向是否有赢棋
        state = self._swin(point)
        if state != False:
            self.clear_state(point)
            return state
        # 反斜线方向是否有赢棋
        state = self._rwin(point)
        if state != False:
            self.clear_state(point)
            return state
        self.clear_state(point)
        return False
    
    def reset(self):
        """重置棋盘"""
        self._board = [[config.State.EMPTY for _ in range(self.size)] for _ in range(self.size)]
        return self._board

    def show_board(self):
        """打印棋盘信息"""
        print(pd.DataFrame(self._board))


if __name__ == "__main__":
    b = ChessBoard(size=15)
    b.set_state((Point(7,7,config.State.BLACK)))
    b.set_state((Point(6,8,config.State.WHITE)))
    b.set_state((Point(5,9,config.State.BLACK)))
    b.set_state((Point(4,10,config.State.BLACK)))
    b.set_state((Point(3,11,config.State.BLACK)))
    b.set_state((Point(2,12,config.State.BLACK)))
    
    
    if b.check_win(Point(8,6,config.State.BLACK)) == config.State.WHITE:
        print("WHITE win!")
    elif b.check_win(Point(8,6,config.State.BLACK)) == config.State.BLACK:
        print("BLACK win!")
    elif b.check_win(Point(8,6,config.State.BLACK)) == config.State.EMPTY:
        print("Fair play!")
    else:
        print("Nobody win!")

    b.show_board()
