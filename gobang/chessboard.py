# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import random
from typing import Optional, List

import util
from config import Chess, Point, Config


class ChessBoard(object):
    """定义棋盘类及关联的操作"""
    def __init__(self, board:Optional[List[list]]=None, size:int=Config.SIZE):
        """初始化
        Args:
            board: 用board初始化
            size: 初始化board的大小
        """
        self.size = size
        if board is None:
            self._board = [[Chess.EMPTY.value for _ in range(size)] for _ in range(size)]
        else:
            assert len(board) == size, "board's shape and config.SIZE is conflict with each other!"
            self._board = board
        self._history = []

    def get_board(self, point:Optional[Point]=None, roi:int=8):
        """获取棋盘
        Args:
            point: 兴趣点中心, 当和roi一起传递时会截取关注区域
            roi: 以point为中心, roi为距离的感兴趣区域
        """
        if point is None or not roi:
            return self._board
        return self._crop_roi(point, roi)

    def is_empty(self, pt: Point):
        """是否为空"""
        if pt.x < 0 or pt.x >= self.size or pt.y < 0 or pt.y >= self.size:
            raise ValueError(f"{pt} out of boundary!")
        return self._board[pt.x][pt.y] == Chess.EMPTY

    def has_empty(self):
        """是否有空位置"""
        return len(self._history) < self.size ** 2

    def get_empty(self, neighbor_layer:Optional[int]=2, shuffle=True):
        """空位置
        Args:
            neighbor_layer: 当传入此参数时表示空位置必须存在邻居
            shuffle: 随时随机打乱
        """
        if len(self._history) == 0:
            return [(self.size // 2, self.size // 2)]
        moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self._board[i][j] == Chess.EMPTY:
                    if neighbor_layer and self._has_neighbors(i, j, neighbor_layer):
                        moves.append((i,j))
                    elif not neighbor_layer:
                        moves.append((i,j))
        if shuffle:
            random.shuffle(moves)
        return moves

    def _has_neighbors(self, x:int, y:int, layer:int=2):
        """是否有邻居"""
        for i in range(max(0, x-layer), min(self.size, x+layer+1)):
            for j in range(max(0, y-layer), min(self.size, y+layer+1)):
                if i == x and j == y:
                    continue
                if self._board[i][j] != Chess.EMPTY:
                    return True
        return False

    def _crop_roi(self, point:Point, roi:int):
        """截取ROI区域
        Args:
            point: 兴趣点中心, 当和roi一起传递时会截取关注区域
            roi: 以point为中心, roi为距离的感兴趣区域
        """
        roi = min(roi, len(self._board))
        start_x = max(0, point.x - roi + 1)
        end_x = min(len(self._board), point.x + roi)
        start_y = max(0, point.y - roi + 1)
        end_y = min(len(self._board), point.y + roi)
        # crop之后需要将区域补齐为正方形
        left = True
        while end_y - start_y > end_x - start_x:
            if left:
                if start_x > 0:
                    start_x -= 1
                left = False
            else:
                if end_x < len(self._board):
                    end_x += 1
                left = True
        left = True
        while end_x - start_x > end_y - start_y:
            if left:
                if start_y > 0:
                    start_y -= 1
                left = False
            else:
                if end_y < len(self._board):
                    end_y += 1
                left = True
        # crop区域
        cropped_board = [[self._board[j][i] for i in range(start_x, end_x)] for j in range(start_y, end_y)]
        return cropped_board

    def set(self, pt:Point):
        """落子"""
        if self._board[pt.x][pt.y] != Chess.EMPTY:
            raise ValueError(f"{pt} position not empty!")
        if pt.x < 0 or pt.x >= self.size or pt.y < 0 or pt.y >= self.size:
            raise ValueError(f"{pt} out of boundary!")
        self._board[pt.x][pt.y] = pt.chess.value
        self._history.append(pt)
        return True

    def unset(self):
        """回退一步"""
        if not self._history:
            return False
        last = self._history.pop()
        self._board[last.x][last.y] = Chess.EMPTY.value
        return last

    def get(self, pt:Point):
        """获取指定点坐标的状态"""
        assert 0 <= pt.x < self.size, "Invalid pt.x"
        assert 0 <= pt.y < self.size, "Invalid pt.y"

        return self._board[pt.x][pt.y]

    def reset(self):
        """重置棋盘"""
        self._board = [[Chess.EMPTY.value for _ in range(self.size)] for _ in range(self.size)]
        return self._board

    def show(self):
        """display matrix readable"""
        util.show(self._board)
    

if __name__ == "__main__":
    board = ChessBoard(size=15)
    board.set((Point(7,7,Chess.BLACK)))
    board.set((Point(6,8,Chess.BLACK)))
    board.set((Point(5,9,Chess.BLACK)))
    board.set((Point(4,10,Chess.BLACK)))
    board.set((Point(3,11,Chess.BLACK)))
    board.set((Point(2,12,Chess.BLACK)))
    board.show()