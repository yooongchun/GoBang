# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import typing

import config

class ChessBoard(object):
    """定义棋盘类及关联的操作"""
    def __init__(self, board:typing.Optional[typing.List[list]]=None, size:int=config.Config.SIZE):
        """初始化
        Args:
            board: 用board初始化
            size: 初始化board的大小
        """
        self.size = size
        if board is None:
            self._board = [[config.Chess.EMPTY.value for _ in range(size)] for _ in range(size)]
        else:
            assert len(board) == size, "board's shape and config.SIZE is conflict with each other!"
            self._board = board

    def get_board(self, point:typing.Optional[config.Point]=None, roi:int=8):
        """获取棋盘
        Args:
            point: 兴趣点中心, 当和roi一起传递时会截取关注区域
            roi: 以point为中心, roi为距离的感兴趣区域
        """
        if point is None or not roi:
            return self._board
        return self._crop_roi(point, roi)

    def get_empty(self):
        """空位置"""
        moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self._board[i][j] == config.Chess.EMPTY:
                    moves.append((i,j))
        return moves

    def _crop_roi(self, point:config.Point, roi):
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
        cropped_board = [[self._board[x][y] for x in range(start_x, end_x)] for y in range(start_y, end_y)]
        return cropped_board

    def set_state(self, pt:config.Point):
        """落子"""
        if self._board[pt.x][pt.y] != config.Chess.EMPTY:
            raise ValueError(f"{pt} position not empty!")
        if pt.x < 0 or pt.x >= self.size or pt.y < 0 or pt.y >= self.size:
            raise ValueError(f"{pt} out of boundary!")
        self._board[pt.x][pt.y] = pt.chess.value
        return True

    def unset_state(self, pt:config.Point):
        """清除"""
        assert 0 <= pt.x < self.size, "Invalid point.x"
        assert 0 <= pt.y < self.size, "Invalid point.y"

        self._board[pt.x][pt.y] = config.Chess.EMPTY.value
        return True

    def get_state(self, pt:config.Point):
        """获取指定点坐标的状态"""
        assert 0 <= pt.x < self.size, "Invalid pt.x"
        assert 0 <= pt.y < self.size, "Invalid pt.y"

        return self._board[pt.x][pt.y]

    def reset(self):
        """重置棋盘"""
        self._board = [[config.Chess.EMPTY.value for _ in range(self.size)] for _ in range(self.size)]
        return self._board


if __name__ == "__main__":
    import util

    board = ChessBoard(size=15)
    board.set_state((config.Point(7,7,config.Chess.BLACK)))
    board.set_state((config.Point(6,8,config.Chess.BLACK)))
    board.set_state((config.Point(5,9,config.Chess.BLACK)))
    board.set_state((config.Point(4,10,config.Chess.BLACK)))
    board.set_state((config.Point(3,11,config.Chess.BLACK)))
    board.set_state((config.Point(2,12,config.Chess.BLACK)))

    util.show(board.get_board())
