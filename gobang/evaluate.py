#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
局面评估
author: yooongchun@foxmail.com
"""
import enum
import typing
from collections import defaultdict as ddict
from itertools import combinations as comb

import util
import chessboard
from  config import Point, Chess


class Score(object):
    """各类形态的评分"""
    # score level
    WIN = 10000
    LEVEL1 = 1000
    LEVEL2 = 500
    LEVEL3 = 100
    LEVEL4 = 50
    LEVEL5 = 10
    LEVEL6 = 1

    # 单一形态可以直接在矩阵中搜索
    # Connected five
    xxxxx = WIN + 100
    # Live four
    oxxxxo = WIN + 50
    # Half-died four
    oxxxxd = LEVEL1
    xoxxx = LEVEL1
    xxoxx = LEVEL1
    # Live three
    oxxxo = LEVEL2
    oxoxxo = LEVEL2
    # Half-died three
    dxxxoo = LEVEL3
    dxxoxo = LEVEL3
    dxoxxo = LEVEL3
    xxoox = LEVEL3
    xoxox = LEVEL3
    doxxxod = LEVEL3
    # Live two
    ooxxoo = LEVEL4
    oxoxo = LEVEL4
    xoox = LEVEL4
    # Half-died two
    dxooxo = LEVEL5
    dxxooo = LEVEL5
    dxoxoo = LEVEL5
    xooox = LEVEL5

    # 组合形态需要进一步判断
    c_db_half_died_four = WIN + 10
    c_db_live_three = WIN + 1
    c_db_half_died_three = LEVEL2


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
                sub = self.matrix[i][j:j+self.k]
                if sub != self.arr:
                    continue
                index = tuple((i, j+m) for m in range(self.k))
                self.indexes[Direction.HORI].append(index)
                if not self.rt_all:
                    return

    def _vert_match_arr(self):
        """竖直方向"""
        for j in range(self.n):
            for i in range(self.n-self.k+1):
                sub = [self.matrix[i+m][j] for m in range(self.k)]
                if sub != self.arr:
                    continue
                index = tuple((i+m, j) for m in range(self.k))    
                self.indexes[Direction.VERT].append(index)
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
                index = tuple((i+m, j+m) for m in range(self.k))
                self.indexes[Direction.DIAG].append(index)
                if not self.rt_all:
                    return
        for x in range(stop_k): # 左半轴
            for i, j in zip(range(x, stop_k), range(min(self.n-x, stop_k))):
                sub = [self.matrix[i+m][j+m] for m in range(self.k)]
                if sub != self.arr:
                    continue
                index = tuple((i+m, j+m) for m in range(self.k))
                self.indexes[Direction.DIAG].append(index)
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
                index = tuple((i+m, j-m) for m in range(self.k))
                self.indexes[Direction.RDIAG].append(index)
                if not self.rt_all:
                    return
        for x in range(stop_k): # 右半轴
            for i, j in zip(range(x, stop_k), range(self.n-1, self.k-2, -1)):
                sub = [self.matrix[i+m][j-m] for m in range(self.k)]
                if sub != self.arr:
                    continue
                index = tuple((i+m, j-m) for m in range(self.k))
                self.indexes[Direction.RDIAG].append(index)
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


class MaxEvaluation(object):
    """棋盘评估类, 只对一个类型打分"""
    def __init__(self, board: chessboard.ChessBoard, target: enum.IntEnum,
                        roi: int=8, point: typing.Optional[Point]=None):
        """初始化
        Args:
            board: 棋盘, 二维数组
            roi: 聚焦区域, 当point传入时可指定评估区域,否则就是全局
            point: 最后一个落子点
            target: 评分的目标对象

        """
        self._chessboard = board
        # roi区域
        self._roi = roi
        # 落子点，用来判断位置得分
        self._point = point
        # 这三个变量关联了序列的表示符号，不可更改
        self.x = target.value
        self.d = Chess.BLACK.value if self.x == Chess.WHITE else Chess.WHITE.value
        self.o = Chess.EMPTY.value
        # 添加边框
        self._add_border()

    @property
    def position_score(self):
        """位置分,越靠近中心越高"""
        if self._point is None:
            return 0
        size = self._chessboard.size
        x = self._point.x
        y = self._point.y
        return min([x, y, size-x, size-y])

    def _add_border(self):
        """添加边框"""
        size = self._chessboard.size + 2
        new_board = [[self.d for _ in range(size)] for _ in range(size)]
        board = self._chessboard.get_board()
        for i in range(1, size-1):
            new_board[i][1:-1] = board[i-1]
        self._chessboard = chessboard.ChessBoard(new_board, size)
        if self._point:
            self._point = Point(self._point.x+1, self._point.y+1, self._point.chess)

    def get_score(self):
        """评估局面并给出打分"""
        # 位置分，越靠近中心，得分越高
        pscore = self.position_score
        # 按照分数对case进行排序，便于查找的时候从高到低查找
        cases = filter(lambda x: x[0] in 'oxd', dir(Score))
        cases = sorted(cases, key=lambda x: getattr(Score, x), reverse=True)
        for case in cases:
            score = getattr(Score, case)
            # Only these cases need consider double case
            match_all = score in [Score.LEVEL1, Score.LEVEL2, Score.LEVEL3]
            matched = self.search_case(case, match_all)
            if not matched:
                continue
            if not match_all:
                return score + pscore
            # match all
            if self._is_multi_case(matched):
                if score == Score.LEVEL1:
                    return Score.c_db_half_died_four + pscore
                if score == Score.LEVEL2:
                    return Score.c_db_live_three + pscore
                return Score.c_db_half_died_three + pscore
            return score + pscore
        return pscore

    def search_case(self, case: str, match_all=False):
        """搜索case"""
        # 通过字符串构建查找序列
        roi_board = self._chessboard.get_board(self._point, self._roi)
        arr = [getattr(self, s) for s in case]
        matcher = Matcher(roi_board, arr, match_all)
        matched = matcher.match_arr()
        if matched:
            return matched
        # 序列不对称，则需要额外查找逆序
        arr2 = list(reversed(arr))
        if arr != arr2:
            matcher = Matcher(roi_board, arr2, match_all)
            return matcher.match_arr()
        return None

    def _is_multi_case(self, cases):
        """交叉情况判断"""
        for dire1, dire2 in comb(cases.keys(), 2):
            for arr1 in cases[dire1]:
                for arr2 in cases[dire2]:
                    if len(arr1) + len(arr2) > len(set(arr1) | set(arr2)):
                        return True


class Evaluation(object):
    """对盘面打分,即是自己的最大分-对手的最大分"""
    
    def __init__(self, board: chessboard.ChessBoard, target: enum.IntEnum,
                        roi: int=8, point: typing.Optional[Point]=None):
        """初始化
        Args:
            board: 棋盘, 二维数组
            roi: 聚焦区域, 当point传入时可指定评估区域,否则就是全局
            point: 最后一个落子点
            target: 评分的目标对象

        """
        self._chessboard = board
        # roi区域
        self._roi = roi
        # 落子点，用来判断位置得分
        self._point = point
        self._target = target
        self._army = Chess.BLACK if target == Chess.WHITE else Chess.WHITE

    def get_score(self, min_max=False):
        """计算得分"""
        eva1 = MaxEvaluation(self._chessboard, self._target, self._roi, self._point)
        eva2 = MaxEvaluation(self._chessboard, self._army, self._roi, self._point)
        max_score = eva1.get_score()
        min_score = eva2.get_score()
        if not min_max:
            return max_score - min_score
        return max_score, min_score

    def check_win(self):
        """是否已经获胜"""
        eva = MaxEvaluation(self._chessboard, self._target, self._roi, self._point)
        return eva.search_case('xxxxx')

    def show_roi(self):
        """display roi region"""
        roi = self._chessboard.get_board(self._point, self._roi)
        util.show(roi)


if __name__ == "__main__":
    raw_input = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 2, 0, 0, 0],
        [0, 1, 1, 2, 0, 0],
        [0, 1, 2, 2, 2, 0],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 2, 0, 0, 0]]
    board = chessboard.ChessBoard(raw_input, size=len(raw_input))
    evaluate = Evaluation(board, Chess.BLACK, roi=5, point=Point(2, 2))
    score = evaluate.get_score()
    evaluate.show_roi()
    print("Evaluate score:", score)
