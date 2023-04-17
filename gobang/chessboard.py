# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import typing

import torch
import torch.nn.functional as F

import config


class ChessBoard(object):
    """定义棋盘类，绘制棋盘的形状，切换先后手，判断输赢等"""
    def __init__(self, board:typing.Optional[torch.Tensor]=None, size=config.Config.SIZE):
        self.size = size
        if board is None:
            self._board = config.State.EMPTY * torch.ones((size, size), dtype=torch.float32)
        else:
            assert board.shape[0] == size, "board's shape and config.SIZE is conflict with each other!"
            self._board = board

    def board(self):
        """棋盘"""
        return self._board

    def set_state(self, point:config.Point):
        """落子"""
        if self._board[point.x][point.y] != config.State.EMPTY:
            return False
        if point.x < 0 or point.x >= self.size or point.y < 0 or point.y >= self.size:
            return False
        self._board[point.x][point.y] = point.state
        return True

    def unset_state(self, point:config.Point):
        """清除"""
        assert 0 <= point.x < self.size, "Invalid point.x"
        assert 0 <= point.y < self.size, "Invalid point.y"
        assert point.state in [config.State.BLACK, config.State.WHITE, config.State.EMPTY], "Invalid point.state"
        
        self._board[point.x][point.y] = config.State.EMPTY
        return True

    def get_state(self, point:config.Point):
        """获取指定点坐标的状态"""
        assert 0 <= point.x < self.size, "Invalid point.x"
        assert 0 <= point.y < self.size, "Invalid point.y"

        return self._board[point.x][point.y]

    def check_win(self, point:config.Point):
        """当把x,y位置落子之后, 局面是否有赢家"""
        if not self.set_state(point):
            return False
        row_kernel = torch.tensor([[[[1, 1, 1, 1, 1]]]], dtype=torch.float32)
        col_kernel = torch.tensor([[[[1], [1], [1], [1], [1]]]], dtype=torch.float32)
        diag_kernel = torch.diag(torch.tensor([1, 1, 1, 1, 1], dtype=torch.float32)).unsqueeze(0).unsqueeze(0)
        rdiag_kernel = torch.flip(diag_kernel, dims=[-1])
        raw_input = self._board.unsqueeze(0).unsqueeze(0)
        for kernel in [row_kernel, col_kernel, diag_kernel, rdiag_kernel]:
            row = F.conv2d(raw_input, kernel)
            row[row != 5] = 0
            if row.sum():
                return True
        return False
    
    def reset(self):
        """重置棋盘"""
        self._board = config.State.EMPTY * torch.ones((self.size, self.size), dtype=torch.float32)
        return self._board


if __name__ == "__main__":
    b = ChessBoard(size=15)
    b.set_state((config.Point(7,7,config.State.BLACK)))
    b.set_state((config.Point(6,8,config.State.BLACK)))
    b.set_state((config.Point(5,9,config.State.BLACK)))
    b.set_state((config.Point(4,10,config.State.BLACK)))
    b.set_state((config.Point(3,11,config.State.BLACK)))
    b.set_state((config.Point(2,12,config.State.BLACK)))
    
    if b.check_win(config.Point(8,6,config.State.BLACK)):
        print("BLACK win!")
    else:
        print("Nobody win!")

    print(b.board())
