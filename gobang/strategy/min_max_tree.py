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
        
        self.best_move = Point(-1, -1, target)

    def next_turn(self, turn: Chess):
        """下一步走子对象"""
        if turn == self._target:
            return self._army
        return self._target
    
    def set_best_move(self, move):
        """记录最佳move"""
        self.best_move.x = move[0]
        self.best_move.y = move[1]

    def _xxxsearch(self, prev_turn: Chess, depth: int, pt:Optional[Point]=None,
                    alpha: float=-float('inf'), beta: float=float('inf'), path=[]):
        """递归搜索：返回最佳分数
        Args:
            turn: 上一步棋
            depth: 递归深度
            alpha: 下界
            beta: 上界
        """
        # 符号
        flag = 2 * int(self._target == prev_turn) - 1
        # 下一步
        cur_turn = self.next_turn(prev_turn)
        # 终止条件
        # 如果深度为零则返回
        if depth <= 0:
            evaluater = evaluate.Evaluation(self._chessboard, prev_turn, self._roi, pt)
            print(f"depth={depth}, turn={prev_turn}, point={pt}, alpha={alpha}, beta={beta}, path:{path}")
            score = evaluater.check_three()
            return flag * score
        # # 如果游戏结束则立马返回
        # if evaluater.check_win():
        #     return flag * evaluate.Score.WIN
        # 产生新的走法
        moves = self._chessboard.get_empty()
        # 枚举当前所有走法
        for i, j in moves:
            # 标记当前走法到棋盘
            pt = Point(i, j, cur_turn)
            self._chessboard.set_state(pt)
            # 深度优先搜索，返回评分，走的行和走的列
            score = self._search(cur_turn, depth - 1, pt, alpha, beta, path+[(i,j,cur_turn.value)])
            # 棋盘上清除当前走法
            self._chessboard.unset_state(pt)
            # 计算最好分值的走法
            # alpha/beta 剪枝
            if self._target == cur_turn:
                # 当前节点为极大值节点，则需要用当前节点值更新父节点的beta值作为新上界
                if score > alpha:
                    alpha = score
                    self.set_best_move([i,j])
            else:
                # 当前节点为极小值节点，则需要用当前节点值更新父节点的alpha值作为新下界
                if  score < beta:
                    self.set_best_move([i,j])
                    beta = score
            # 当搜索区间出现矛盾的时候，则搜索结束
            if alpha >= beta:
                self.set_best_move([i, j])
                break
        # 返回当前最好的分数: 极大值节点返回下界，极小值节点返回上界
        return alpha if flag else beta

    def _negetive_max(self, prev_turn: Chess, depth: int, pt:Optional[Point]=None,
                    alpha: float=-float('inf'), beta: float=float('inf')):
        """递归搜索：返回最佳分数
        Args:
            turn: 上一步棋
            depth: 递归深度
            alpha: 下界
            beta: 上界
        """
        # 如果深度为零则返回
        evaluater = evaluate.Evaluation(self._chessboard, prev_turn, self._roi, pt)
        if depth <= 0:
            print(f"depth={depth}, turn={prev_turn}, point={pt}, alpha={alpha}, beta={beta}")
            score = evaluater.check_three()
            return score
        # 如果游戏结束则立马返回
        if evaluater.check_win():
            return evaluate.Score.WIN
        # 产生新的走法
        moves = self._chessboard.get_empty()
        # 遍历每一个候选步
        for i, j in moves:
            # 下一步
            cur_turn = self.next_turn(prev_turn)
            # 标记当前走法到棋盘
            pt = Point(i, j, cur_turn)
            self._chessboard.set_state(pt)
            # 深度优先搜索，返回评分，走的行和走的列
            score = self._negetive_max(cur_turn, depth - 1, pt, -beta, -alpha)
            # 棋盘上清除当前走法
            self._chessboard.unset_state(pt)
            # 计算最好分值的走法
            if score > alpha:
                self.set_best_move([i,j])
                # alpha/beta 剪枝
                if alpha >= beta:
                    break
                alpha = abs(score)
        return alpha

    def search(self, max_depth:int=3):
        """最大递归深度"""
        # score = self._search(self._army, steps*2-1)
        score = self._negetive_max(self._army, max_depth)
        return score, self.best_move


if __name__ == "__main__":
    raw_input = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]]
 
    board = chessboard.ChessBoard(raw_input, size=len(raw_input))
    ai = MinMaxSearcher(board, Chess.BLACK)
    score, best_move = ai.search(5)
    print(f"Best move:{best_move}, score:{score}")
