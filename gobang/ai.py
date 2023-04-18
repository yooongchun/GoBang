#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
搜索算法的实现
author: yooongchun@foxmail.com
"""
import config
import evaluate
import chessboard


class Searcher(object):
    """博弈树搜索"""
    def __init__(self, board: chessboard.ChessBoard, 
                    role: config.Chess=config.Chess.WHITE,
                    roi: int=8):
        """初始化
        Args:
            board: 棋盘
            role: 角色, 黑棋或白棋
            roi: 搜索范围
        """
        self._role = role
        self._army = config.Chess.BLACK if role == config.Chess.WHITE else config.Chess.WHITE
        self._roi = roi
        self._chessboard = board
        self._max_depth = 3
        self._best_move = (0, 0)

    def _search(self, turn: bool, depth: int, alpha: float, beta: float):
        """递归搜索：返回最佳分数
        Args:
            turn: 该谁走子
            depth: 递归深度
            alpha: alpha因子
            beta: beta因子
        """
        # 产生新的走法
        moves = self._chessboard.get_empty()
        best_move = None
        # 枚举当前所有走法
        for i, j in moves:
            # 标记当前走法到棋盘
            if turn:
                pt = config.Point(i, j, self._role)
            else:
                pt = config.Point(i, j, self._army)
            print(f"depth {depth}, move:{pt}")
            self._chessboard.set_state(pt)
            # 深度为零则评估棋盘并返回
            evaluater = evaluate.Evaluation(self._chessboard, self._roi, pt, pt.chess)
            if depth <= 0:
                self._chessboard.unset_state(pt)
                score = evaluater.get_score()
                return score
            # 如果游戏结束则立马返回
            if evaluater.check_win():
                self._chessboard.unset_state(pt)
                return evaluate.Score.WIN
            # 深度优先搜索，返回评分，走的行和走的列
            score = - self._search(not turn, depth - 1, -beta, -alpha)
            # 棋盘上清除当前走法
            self._chessboard.unset_state(pt)

            # 计算最好分值的走法
            # alpha/beta 剪枝
            if abs(score) > alpha:
                alpha = abs(score)
                best_move = (i, j)
                if alpha >= beta:
                    break
        # 如果是第一层则记录最好的走法
        if depth == self._max_depth and best_move:
            self._best_move = best_move
        # 返回当前最好的分数，和该分数的对应走法
        return alpha

    def search(self, turn: bool, depth:int=3):
        import random
        
        # score = self._search(turn, depth, -0x7fffffff, 0x7fffffff)
        moves = self._chessboard.get_empty()
        move = random.choice(moves)
        point = config.Point(move[0], move[1], self._role)
        self._chessboard.set_state(point)
        score = evaluate.Evaluation(self._chessboard, point=point).get_score()
        self._chessboard.unset_state(point)
        return move, score


if __name__ == "__main__":
    raw_input = [
        [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 2, 2, 2, 0, 2, 0],
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 1],
        [0, 1, 0, 0, 0, 1, 1, 0, 0, 1],
        [0, 0, 0, 1, 1, 0, 0, 1, 0, 0],
        [0, 1, 0, 2, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 2, 1, 0, 0, 0]]

    board = chessboard.ChessBoard(raw_input, size=len(raw_input))
    ai = Searcher(board, config.Chess.WHITE)
    best_move, score = ai.search(True)
    print(f"Best move:{best_move}, score:{score}")
