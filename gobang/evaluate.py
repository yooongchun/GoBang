#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
局面评估
author: yooongchun@foxmail.com
"""

import cv2
import numpy as np

import config


class Kernel(object):
    """各种特殊的模式,用来评分
    注意：卷积中需要特殊表示空白位置，所以需要在卷积运算前统一将空白值传入, 不能为0
    注意：位置判断的特殊性，需要在传入原矩阵时在外层加一层边缘，用来避免边框阻塞情况
    注意：由于卷积的特殊性，对于双活这类的情况，完全可以通过卷积符合的个数来判断
    """
    def __init__(self, role: int, army: int, empty_val=3) -> None:
        self.role = role
        self.army = army
        self.empty_val = empty_val

    @property
    def Five(self):
        """连五,包含四种情况：横竖斜反"""
        kernels = np.zeros((5, 5, 4), dtype=np.float32)
        for i in range(5):
            # 横向
            kernels[0, i, 0] = self.role
            # 纵向
            kernels[i, 0, 1] = self.role
            # 斜向
            kernels[i, i, 2] = self.role
            # 逆向
            kernels[4-i, i, 3] = self.role
        return kernels / kernels.sum(axis=0).sum(axis=0)

    @property
    def LiveFour(self):
        """活四,两个端点皆可落子,xxxx型,包含四种情况"""
        kernels = np.zeros((6, 6, 4), dtype=np.float32)
        # 横向的两个端点必须是空的
        kernels[0, 0, 0] = kernels[0, 5, 0] = self.empty_val
        # 纵向的两个端点必须是空的
        kernels[0, 0, 1] = kernels[5, 0, 1] = self.empty_val
        # 斜向的两个端点必须是空的
        kernels[0, 0, 2] = kernels[5, 5, 2] = self.empty_val
        # 横向的两个端点必须是空的
        kernels[5, 0, 3] = kernels[0, 5, 3] = self.empty_val
        for i in range(1, 5):
            # 横向
            kernels[0, i, 0] = self.role
            # 纵向
            kernels[i, 0, 1] = self.role
            # 斜向
            kernels[i, i, 2] = self.role
            # 逆向
            kernels[4-i, i, 3] = self.role
        return kernels / kernels.sum(axis=0).sum(axis=0)

    @property
    def HalfFour_OXXXX(self):
        """冲四,一共20种
        第一类: OXXXX型, 包含8种情况, 不过需要注意, 这种条件下要求原矩阵边框加一圈对手子来表示边框阻塞, 不然会存在遗漏的情况
        """
        kernels = np.zeros((6, 6, 8), dtype=np.float32)
        # # 横向有一个端口必须是空的且另一个端口不为空
        kernels[0, 0, 0] = self.empty_val
        kernels[0, 0, 5] = self.army
        kernels[4, 0, 0] = self.army
        kernels[4, 0, 5] = self.empty_val
        # 纵向有一个端口必须是空的且另一个端口不为空
        kernels[1, 0, 0] = self.empty_val
        kernels[1, 5, 0] = self.army
        kernels[5, 0, 0] = self.army
        kernels[5, 5, 0] = self.empty_val
        # 斜向有一个端口必须是空的且另一个端口不为空
        kernels[2, 0, 0] = self.empty_val
        kernels[2, 5, 5] = self.army
        kernels[6, 0, 0] = self.army
        kernels[6, 5, 5] = self.empty_val
        # 逆向有一个端口必须是空的且另一个端口不为空
        kernels[3, 5, 0] = self.empty_val
        kernels[3, 0, 5] = self.army
        kernels[7, 5, 0] = self.army
        kernels[7, 0, 5] = self.empty_val
        for i in range(1,5):
            # 横向
            kernels[0, 0, i] = self.role
            kernels[4, 0, i] = self.role
            # 纵向
            kernels[1, i, 0] = self.role
            kernels[5, i, 0] = self.role
            # 斜向
            kernels[2, i, i] = self.role
            kernels[6, i, i] = self.role
            # 逆向
            kernels[3, 4-i, i] = self.role
            kernels[7, 4-i, i] = self.role
        return kernels / kernels.sum(axis=0).sum(axis=0)
    @property
    def HalfFour_XOXXX(self):
        """冲四,一共20种, 第二类: XOXXX型"""
        kernels = np.zeros((8, 5, 5))
        # 横向
        kernels[0, 0, 1] = self.empty_val
        kernels[4, 0, 3] = self.empty_val
        # 纵向
        kernels[1, 1, 0] = self.empty_val
        kernels[5, 3, 0] = self.empty_val
        # 斜向
        kernels[2, 1, 1] = self.empty_val
        kernels[6, 3, 3] = self.empty_val
        # 逆向
        kernels[3, 3, 1] = self.empty_val
        kernels[7, 1, 3] = self.empty_val
        for i in range(5):
            if i != 1:
                kernels[0, 0, i] = self.role
                kernels[1, i, 0] = self.role
                kernels[2, i, i] = self.role
                kernels[3, 4-i, i] = self.role
            if i != 3:
                kernels[4, 0, i] = self.role
                kernels[5, i, 0] = self.role
                kernels[6, i, i] = self.role
                kernels[7, 4-i, i] = self.role
        return kernels      

    @property
    def HalfFour_XXOXX(self):
        """冲四,一共20种, 第三类: XXOXX型
        """
        kernels = np.zeros((4, 5, 5))
        # 横向
        kernels[0, 0, 2] = self.empty_val
        # 纵向
        kernels[1, 2, 0] = self.empty_val
        # 斜向
        kernels[2, 2, 2] = self.empty_val
        # 逆向
        kernels[3, 2, 2] = self.empty_val
        for i in range(5):
            if i != 2:    
                kernels[0, 0, i] = self.role
                kernels[1, i, 0] = self.role
                kernels[2, i, i] = self.role
                kernels[3, 4-i, i] = self.role
        return kernels      

    @property
    def LiveThree(self):
        """活三"""
        pass

    @classmethod
    def DoubleTwo(cls):
        """冲二"""
        pass

    @classmethod
    def DoubleThree(cls):
        """冲三"""
        pass

    @classmethod
    def LiveTwo(cls):
        """活二"""
        pass


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


class Evaluation(object):
    """棋盘评估类，给当前棋盘打分用
    注意：卷积中需要特殊表示空白位置，所以需要在卷积运算前统一将空白值传入, 这里设置为3
    注意：位置判断的特殊性，需要在传入原矩阵时在外层加一层边缘，用来避免边框阻塞情况
    注意：由于卷积的特殊性，对于双活这类的情况，完全可以通过卷积符合的个数来判断
    """
    EMPTY_VAL = 3

    def __init__(self, board: list, target: int):
        self.target = target # 评估的对象，白棋或黑棋
        self.army = config.State.WHITE if self.target == config.State.BLACK else config.State.BLACK
        # 边缘增加一层并赋值为对手的值
        self._board = np.zeros(len(board)+2)
        self._board[0, :] = self.army
        self._board[-1, :] = self.army
        self._board[:, 0] = self.army
        self._board[:, -1] = self.army
        # 空值转换
        xy = np.where(self._board == config.State.EMPTY)
        self._board[xy] = self.EMPTY_VAL

        # 卷积核，用来判断各种棋型
        self.kernel = Kernel(target, self.army, self.EMPTY_VAL)

    def evaluate(self):
        """评估局面并给出打分"""
        pt = self.case_win()

        return 0

    def case_win(self):
        """必胜棋型, 包括：连五、活四、双冲四、双活三"""
        kernels = np.concatenate([self.kernel.Five, 
                        self.kernel.LiveFour, 
                        self.kernel.HalfFour_OXXXX, 
                        self.kernel.HalfFour_XOXXX,
                        self.kernel.HalfFour_XXOXX], axis=2)
        for i in range(kernels.shape[2]):
            kernel = self.kernel.Five[i]
            res = cv2.filter2D(self._board, -1, kernel)
            count = res.sum()
            if count:
                xys = np.where(res > 0)
                return xys[0]
        return False


if __name__ == "__main__":
    kernel = Kernel(config.State.BLACK, config.State.WHITE)
    print(kernel.Five[0].shape)