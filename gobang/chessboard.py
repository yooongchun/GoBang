# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import typing

import config
import evaluate


class ChessBoard(object):
    """定义棋盘类，绘制棋盘的形状，切换先后手，判断输赢等"""
    def __init__(self, board:typing.Optional[typing.List[list]]=None, size:int=config.Config.SIZE):
        self.size = size
        if board is None:
            self._board = [[config.Chess.EMPTY.value for _ in range(size)] for _ in range(size)]
        else:
            assert len(board) == size, "board's shape and config.SIZE is conflict with each other!"
            self._board = board

    def board(self):
        """棋盘"""
        return self._board

    def set_state(self, pt:config.Point):
        """落子"""
        if self._board[pt.x][pt.y] != config.Chess.EMPTY:
            return False
        if pt.x < 0 or pt.x >= self.size or pt.y < 0 or pt.y >= self.size:
            return False
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

    def check_win(self, pt:config.Point):
        """当把x,y位置落子之后, 局面是否有赢家"""
        if not self.set_state(pt):
            return False
        v = pt.chess.value
        arr = [v, v, v, v, v]
        matcher = evaluate.Matcher(self._board, arr)
        return matcher.match_arr()

    def reset(self):
        """重置棋盘"""
        self._board = [[config.Chess.EMPTY.value for _ in range(self.size)] for _ in range(self.size)]
        return self._board


if __name__ == "__main__":
    import util

    b = ChessBoard(size=15)
    b.set_state((config.Point(7,7,config.Chess.BLACK)))
    b.set_state((config.Point(6,8,config.Chess.BLACK)))
    b.set_state((config.Point(5,9,config.Chess.BLACK)))
    b.set_state((config.Point(4,10,config.Chess.BLACK)))
    b.set_state((config.Point(3,11,config.Chess.BLACK)))
    b.set_state((config.Point(2,12,config.Chess.BLACK)))
    
    point = config.Point(8,6,config.Chess.BLACK)
    if b.check_win(point):
        print("BLACK win!")
    else:
        print("Nobody win!")

    util.show(b.board())
