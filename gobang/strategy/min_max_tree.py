#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
搜索算法的实现
author: yooongchun@foxmail.com
"""
from typing import Optional

import chessboard
import evaluate
from config import Chess, Point

class MinMaxSearcher(object):
    """博弈树搜索"""
    def __init__(self, board: chessboard.ChessBoard, target: Chess, roi: int=8):
        """初始化
        Args:
            board: 棋盘
            role: 角色, 黑棋或白棋
            roi: 搜索范围
        """
        self._target = target
        self._army = Chess.BLACK if target == Chess.WHITE else Chess.WHITE
        self._roi = roi
        self._chessboard = board
        # 储存中间结果
        self._max_depth = -1

    def _negetive_max(self, turn: bool, depth: int, pt:Optional[Point]=None,
                    alpha: float=-float('inf'), beta: float=float('inf'), path=[]):
        """递归搜索：返回最佳分数
        Args:
            turn: 上一步棋
            depth: 递归深度
            alpha: 上界
            beta: 下界
        """
        evaluater = evaluate.Evaluation(self._chessboard, self._target, self._roi, pt)
        # 如果深度为零则返回
        if depth <= 0:
            score = evaluater.get_score()
            return score, pt
        # 如果结束则立马返回
        if evaluater.check_win():
            print(f"win path: {path}")
            return evaluate.Score.WIN, pt
        # 产生新的走法
        moves = self._chessboard.get_empty(neighbor_layer=2, shuffle=True)
        # 遍历每一个候选步
        best_move = None
        for i, j in moves:
            # 标记当前走法
            pt = Point(i, j, self._target if turn else self._army)
            self._chessboard.set(pt)
            score, _ = self._negetive_max(not turn, depth - 1, pt, alpha, beta, path + [(i,j)])
            # 清除当前走法
            self._chessboard.unset()
            best_move = pt
            # 计算最好分值的走法
            if turn and score > alpha : # 当前为Max节点
                alpha = score
                # alpha + beta剪枝点
                if score >= beta:
                    break
            elif not turn and score < beta: # 当前节点为MIN节点
                beta = score
                # alpha + beta剪枝点
                if score <= alpha:
                    break
        if turn:
            return alpha, best_move
        return beta, best_move

    def search(self, max_depth:int=3):
        """最大递归深度"""
        self._max_depth = max_depth
        score, move = self._negetive_max(True, max_depth)
        return score, move
