#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
局面评估
author: yooongchun@foxmail.com
"""
import typing
from collections import defaultdict as ddict
from itertools import combinations as comb

import config


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
    xxxxx = WIN + 5
    # Live four
    oxxxxo = WIN + 4
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
    c_db_half_died_four = WIN + 3
    c_db_live_three = WIN + 2
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


class Evaluation(object):
    """棋盘评估类，给当前棋盘打分用"""
    def __init__(self, board: typing.List[list], roi: int=8,
                    point: typing.Optional[config.Point]=None,
                    target: config.Chess=config.Chess.BLACK):
        """初始化
        Args:
            board: 棋盘, 二维数组
            roi: 聚焦区域, 当point传入时可指定评估区域,否则就是全局
            point: 最后一个落子点
            target: 评分的目标对象

        """
        # 这三个变量关联了序列的表示符号，不可更改
        self.x = target.value
        self.roi = roi
        self.d = config.Chess.BLACK.value if self.x == config.Chess.WHITE else config.Chess.WHITE.value
        self.o = config.Chess.EMPTY.value
        # 落子点，用来判断位置得分, 需要加入边框层
        self.point = config.Point(point.x+1, point.y+1, point.chess) if point else None
        # 拓展边框
        size = len(board) + 2
        self._board = [[self.d for _ in range(size)] for _ in range(size)]
        for i in range(1, size-1):
            self._board[i][1:-1] = board[i-1]
        # 设置感兴趣区域
        self.crop_roi()

    def crop_roi(self):
        """截取roi区域"""
        if self.point and self.roi:
            # 不能超过原大小
            roi = min(self.roi, len(self._board))
            start_x = max(0, self.point.x - roi + 1)
            end_x = min(len(self._board), self.point.x + roi)
            start_y = max(0, self.point.y - roi + 1)
            end_y = min(len(self._board), self.point.y + roi)
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
            # Point适配
            self.point = config.Point(self.point.x-start_x, self.point.y-start_y, self.point.chess)
            # crop区域
            self._board = [[self._board[x][y] for x in range(start_x, end_x)] for y in range(start_y, end_y)]

    @property
    def position_score(self):
        """位置分,越靠近中心越高"""
        if self.point is None:
            return 0
        size = len(self._board) - 2
        x = self.point.x
        y = self.point.y
        return min([x, y, size-x, size-y])

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
            if self.is_multi_case(matched):
                if score == Score.LEVEL1:
                    return Score.c_db_half_died_four + pscore
                if score == Score.LEVEL2:
                    return Score.c_db_live_three + pscore
                return Score.c_db_half_died_three + pscore
        return pscore

    def search_case(self, case: str, match_all=False):
        """搜索case"""
        # 通过字符串构建查找序列
        arr = [getattr(self, s) for s in case]
        matcher = Matcher(self._board, arr, match_all)
        matched = matcher.match_arr()
        if matched:
            return matched
        # 序列不对称，则需要额外查找逆序
        arr2 = list(reversed(arr))
        if arr != arr2:
            matcher = Matcher(self._board, arr2, match_all)
            return matcher.match_arr()
        return None

    def is_multi_case(self, cases):
        """交叉情况判断"""
        for dire1, dire2 in comb(cases.keys(), 2):
            for arr1 in cases[dire1]:
                for arr2 in cases[dire2]:
                    if len(arr1) + len(arr2) > len(set(arr1) | set(arr2)):
                        return True

    def show_roi(self):
        """display roi region"""
        util.show(self._board)


if __name__ == "__main__":
    import util

    raw_input = [
        [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 2, 1, 1, 1, 2, 0],
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 1],
        [0, 1, 0, 0, 0, 1, 1, 0, 0, 1],
        [0, 0, 0, 1, 1, 0, 0, 1, 0, 0],
        [0, 1, 0, 2, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 2, 1, 0, 0, 0]]

    evaluate = Evaluation(raw_input, roi=5, point=config.Point(1, 6, config.Chess.EMPTY))
    evaluate.show_roi()
    score = evaluate.get_score()
    print("Evaluate score:", score)
