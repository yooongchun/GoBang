#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
局面评估
author: yooongchun@foxmail.com
"""
import typing
from collections import defaultdict as ddict

import config


class Score(object):
    """各类形态的评分"""
    FIVE = 10000 # 连五：必胜
    
    LIVE_FOUR = 10000 # 活四：必胜
    DB_HALF_FOUR = 10000 # 双冲四，必胜
    HALF_FOUR = 1000 # 冲四
    
    DB_LIVE_THREE = 10000 # 双活三：必胜
    LIVE_THREE = 500 # 活三
    DB_DIED_THREE = 500 # 双眠三
    DIED_THREE = 100 # 眠三
    
    DB_LIVE_TWO = 500 # 双活二
    LIVE_TWO = 100 # 活二
    DB_DIED_TWO = 100 # 双眠二
    DIED_TWO = 10 # 眠二


class Direction(object):
    """方向定义"""
    HORI = 0
    VERT = 1
    DIAG = 2
    RDIAG = 3


class Matcher(object):
    """在矩阵中搜索给定的数组"""
    def __init__(self, matrix, arr, match_all=False) -> None:
        self.matrix = matrix
        self.arr = arr
        self.rt_all = match_all
        self.n, self.k = len(matrix), len(arr)
        self.indexes = ddict(list)

    def _hori_match_arr(self):
        """水平方向"""
        for i in range(self.n):
            for j in range(self.n-self.k+1):
                if self.matrix[i][j:j+self.k] != self.arr:
                    continue
                self.indexes[Direction.HORI].append((i, j))
                if not self.rt_all:
                    return

    def _vert_match_arr(self):
        """竖直方向"""
        for j in range(self.n):
            for i in range(self.n-self.k+1):
                sub = [self.matrix[i+m][j] for m in range(self.k)]
                if sub != self.arr:
                    continue
                self.indexes[Direction.VERT].append((i,j))
                if not self.rt_all:
                    return

    def _diag_match_arr(self):
        """对角线"""
        stop_k = self.n - self.k + 1
        for x in range(self.n-self.k, 0, -1): # 右半轴
            for i, j in enumerate(range(x, stop_k)):
                sub = [self.matrix[i+m][j+m] for m in range(self.k)]
                if sub != self.arr:
                    continue
                self.indexes[Direction.DIAG].append((i, j))
                if not self.rt_all:
                    return
        for x in range(stop_k): # 左半轴
            for i, j in zip(range(x, stop_k), range(min(self.n-x, stop_k))):
                sub = [self.matrix[i+m][j+m] for m in range(self.k)]
                if sub != self.arr:
                    continue
                self.indexes[Direction.DIAG].append((i, j))
                if not self.rt_all:
                    return

    def _rdiag_match_arr(self):
        """逆对角线"""
        stop_k = self.n - self.k + 1
        for x in range(self.n-self.k-1, self.n): # 左半轴
            for i, j in zip(range(x), range(x, self.k-2, -1)):
                sub = [self.matrix[i+m][j-m] for m in range(self.k)]
                if sub != self.arr:
                    continue
                self.indexes[Direction.RDIAG].append((i, j))
                if not self.rt_all:
                    return
        for x in range(stop_k): # 右半轴
            for i, j in zip(range(x, stop_k), range(self.n-1, self.k-2, -1)):
                sub = [self.matrix[i+m][j-m] for m in range(self.k)]
                if sub != self.arr:
                    continue
                self.indexes[Direction.RDIAG].append((i, j))
                if not self.rt_all:
                    return

    def match_arr(self):
        """遍历搜索二维数组, 查找数组arr是否存在
        如果存在,返回序列的坐标
        如果rt_all=True, 则需要查找所有满足要求的序列
        """
        self._hori_match_arr()
        if not self.rt_all and len(self.indexes[Direction.HORI]):
            return self.indexes[Direction.HORI][0]
        self._vert_match_arr()
        if not self.rt_all and len(self.indexes[Direction.VERT]):
            return self.indexes[Direction.VERT][0]
        self._diag_match_arr()
        if not self.rt_all and len(self.indexes[Direction.DIAG]):
            return self.indexes[Direction.DIAG][0]
        self._rdiag_match_arr()
        if not self.rt_all and len(self.indexes[Direction.RDIAG]):
            return self.indexes[Direction.RDIAG][0]
        if not self.rt_all or not len(self.indexes):
            return False
        return self.indexes


class Evaluation(object):
    """棋盘评估类，给当前棋盘打分用"""
    def __init__(self, board: typing.List[list], point:typing.Optional[config.Point]=None,
                    target:int=config.State.BLACK):
        """"""
        self.target = target
        self.point = point
        # 拓展边框
        size = len(board) + 2
        self._board = [[config.State.EMPTY for i in range(size)] for j in range(size)]
        for i in range(1, size-1):
            self._board[i][1:-1] = board[i-1]

    @property
    def position_score(self):
        """位置分,越靠近中心越高"""
        if self.point is None:
            return 0
        size = len(self._board) - 2
        x = self.point.x
        y = self.point.y
        return min([x, y, size-x, size-y])

    def evaluate(self):
        """评估局面并给出打分"""
        pscore = self.position_score
        if self.case_XXXXX():
            return Score.FIVE + pscore
        if self.case_OXXXXO():
            return Score.LIVE_FOUR + pscore
        return pscore

    def case_XXXXX(self):
        """连五: 包含四种情况"""
        arr = [self.target] * 5
        matcher = Matcher(self._board, arr, match_all=False)
        return matcher.match_arr()

    def case_OXXXXO(self):
        """活四: 包含四种情况"""
        a = self.target
        e = config.State.EMPTY
        arr = [e, a, a, a, a, e]
        matcher = Matcher(self._board, arr, match_all=False)
        return matcher.match_arr()


if __name__ == "__main__":
    raw_input = [
        [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, -1, 1, 1, 1, -1, 1],
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 1],
        [0, 1, 0, 0, 0, 1, 1, 0, 0, 1],
        [0, 0, 0, 1, 1, 1, 0, 1, 0, 0],
        [0, 1, 0, -1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, -1, 1, 0, 0, 0]]
    print(raw_input)
    evaluate = Evaluation(raw_input)
    res = evaluate.case_XXXXX()
    print("XXXXX", res)
    res = evaluate.case_OXXXXO()
    print("OXXXXO", res)
