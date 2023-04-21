#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
命令行模拟
author: yooongchun@foxmail.com
"""
import time
import argparse

import chessboard
import evaluate
from strategy import min_max_tree
from config import Chess, Point


def simulate(size: int, max_depth:int=3, ai_first:bool=False):
    """模拟"""
    board = chessboard.ChessBoard(size=size)
    ai = Chess.BLACK if ai_first else Chess.WHITE
    human = Chess.WHITE if ai_first else Chess.BLACK
    turn = ai_first
    while True:
        if evaluate.Evaluation(board, ai).check_win():
            print("AI win!")
            break
        if evaluate.Evaluation(board, human).check_win():
            print("You win!")
            break
        if not board.has_empty():
            print("No empty position to go!")
            break
        if turn: # AI play
            mmt = min_max_tree.MinMaxSearcher(board, Chess.BLACK)
            print("AI is thinking...")
            start = time.time()
            best_score, best_move = mmt.search(max_depth)
            end = time.time()
            print(f"AI score:{best_score}, move:{best_move}, depth:{max_depth}, time:{end-start:0.2f}s")
            if best_move:
                board.set(best_move)
                board.show()
                turn = False
            else:
                print("No best move!")
                break
        else: # human play    
            xy = input("Your turn: ")
            xy = xy.strip()
            if len(xy) == 2:
                x, y = xy[0], xy[1]
            elif ' ' in xy:
                x, y = xy.split(" ")
            elif "," in xy:
                x, y = xy.split(",")
            else:
                raise ValueError("Unsupported value!")
            pt = Point(int(x), int(y), human)
            board.set(pt)
            board.show()
            turn = True


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--size", type=int, default=5, help="board size")
    parser.add_argument("-d", "--depth", type=int, default=3, help="AI search max depth")
    parser.add_argument("--ai-first", action="store_true", default=False, help="AI first")
    args = parser.parse_args()
    return args


def main():
    """主函数入口"""
    args = parse_args()
    simulate(args.size, args.depth, args.ai_first)


if __name__ == "__main__":
    main()
