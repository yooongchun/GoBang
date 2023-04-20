#!/usr/bin/env python
# -*- coding:utf-8 -*-


class MinMaxSearcher(object):
    """博弈树搜索"""
    def _negetive_max(self, take:int, turn: bool, depth: int, alpha: float=-float('inf'), beta: float=float('inf'), path=']'):
        """递归搜索：返回最佳分数"""
        # 如果深度为零则返回
        if depth <= 0 or take == 0:
            score = int(take == 0) * 100
            print(f"path:{path}, turn: {turn}, score:{score}, alpha:{alpha}, beta:{beta}")
            return score, path
        # 产生新的走法
        best_path = []
        for i in range(1, 3):
            if take - i < 0:
                continue
            new_path = path + (f"-->[{i}]" if turn else f"-->({i})")
            score, sub_path = self._negetive_max(take-i, turn, depth-1, -beta, -alpha, new_path)
            # 计算最好分值的走法
            if score > alpha:
                best_path = sub_path
                alpha = score
                # alpha + beta剪枝点
                if score >= beta:
                    break
        return alpha, best_path

    def search(self, max_depth:int=3):
        """最大递归深度"""
        score = self._negetive_max(5, True, max_depth)
        return score


if __name__ == "__main__":
    ai = MinMaxSearcher()
    score, path = ai.search(3)
    print("Final score", score, path) 