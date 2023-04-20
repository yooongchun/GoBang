#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
搜索算法的实现
author: yooongchun@foxmail.com
"""
from typing import Optional

import sys
sys.path.append("/Users/zhayongchun/Desktop/GoBang/gobang")

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

    def _negetive_max(self, turn: Chess, depth: int, pt:Optional[Point]=None,
                    alpha: float=-float('inf'), beta: float=float('inf')):
        """递归搜索：返回最佳分数
        Args:
            turn: 上一步棋
            depth: 递归深度
            alpha: 下界
            beta: 上界
        """
        evaluater = evaluate.Evaluation(self._chessboard, turn, self._roi, pt)
        # 如果深度为零则返回
        if depth <= 0:
            score = evaluater.get_score()
            return score, pt
        # # 如果游戏结束则立马返回
        if evaluater.check_win():
            return evaluate.Score.WIN, pt
        # 产生新的走法
        moves = self._chessboard.get_empty()
        # 遍历每一个候选步
        best_move = None
        for i, j in moves:
            # 标记当前走法到棋盘
            pt = Point(i, j, turn)
            self._chessboard.set(pt)
            # 深度优先搜索，返回评分，走的行和走的列
            score, _ = self._negetive_max(turn, depth - 1, pt, -beta, -alpha)
            # 棋盘上清除当前走法
            self._chessboard.unset()
            # 计算最好分值的走法
            if score > alpha:
                alpha = score
                best_move = Point(i,j,turn)
                # alpha + beta剪枝点
                if score >= beta:
                    break
        return alpha, best_move

    def search(self, max_depth:int=3):
        """最大递归深度"""
        self._max_depth = max_depth
        score, move = self._negetive_max(self._target, max_depth)
        return score, move


if __name__ == "__main__":
    raw_input = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]]
    board = chessboard.ChessBoard(raw_input, size=len(raw_input))
    while True:
        board.show()
        if evaluate.Evaluation(board, Chess.BLACK).check_win():
            print("AI win!")
            break
        if evaluate.Evaluation(board, Chess.WHITE).check_win():
            print("You win!")
            break
        if not board.get_empty():
            print("No empty position to go!")
            break
        xy = input("Your turn: ")
        x, y = xy[0], xy[1]
        pt = Point(int(x),int(y),Chess.WHITE)
        board.set(pt)
        ai = MinMaxSearcher(board, Chess.BLACK)
        score, best_move = ai.search(3)
        print(f"AI score:{score}, move:{best_move}")
        if best_move:
            board.set(best_move)
        else:
            print("No best move!")
            break
