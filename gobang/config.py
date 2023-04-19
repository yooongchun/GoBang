#! /usr/bin/env python3
#! -*- coding: utf-8 -*-

"""
配置文件
author:yooongchun@foxmail.com
"""
import enum
import pathlib


class Config(object):
    PROJ_DIR = pathlib.Path(__file__).parent
    APP_NAME = "GoBang"
    APP_VERSION = "v1.0.0"
    # 棋盘和棋子图片 
    CHESSBOARD_BG = str(pathlib.Path(PROJ_DIR, "assets/img/chessboard.jpg"))
    CHESS_BLACK = str(pathlib.Path(PROJ_DIR, "assets/img/black.png"))
    CHESS_WHITE = str(pathlib.Path(PROJ_DIR, "assets/img/white.png"))

    # 背景音效
    SOUND_DEFEATED = str(pathlib.Path(PROJ_DIR, "assets/sound/defeated.wav"))
    SOUND_WIN = str(pathlib.Path(PROJ_DIR, "assets/sound/win.wav"))
    SOUND_MOVE = str(pathlib.Path(PROJ_DIR, "assets/sound/move.wav"))

    # 棋盘
    SIZE = 15
    
    # UI界面
    UI_CHESS_SIZE = 36
    UI_BG_SIZE = 540


# 棋子表示
class Chess(enum.IntEnum):
    """棋子表示"""
    EMPTY = 0
    BLACK = 1
    WHITE = 2


# 点对象
class Point(object):
    """定义点对象"""
    def __init__(self, x: int, y: int, val: enum.IntEnum=Chess.EMPTY):
        self.x = x
        self.y = y
        self.chess = val

    def __repr__(self) -> str:
        return f"Point({self.x},{self.y}):{self.chess.name}"
