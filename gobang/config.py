#! /usr/bin/env python3
#! -*- coding: utf-8 -*-

"""
配置文件
author:yooongchun@foxmail.com
"""
import enum
import pathlib
from collections import namedtuple


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
    SIZE = 10
    
    # UI界面
    UI_HEIGHT = 540
    UI_WIDTH = 540
    UI_MARGIN = 22
    UI_GRID = (UI_WIDTH - 2 * UI_MARGIN) / (SIZE - 1)
    UI_PIECE = 34


# 棋子表示
Chess = enum.IntEnum("Chess", {"EMPTY": 0, "BLACK": 1, "WHITE": 2})

# 点对象
Point = namedtuple("Point", ["x", "y", "chess"])
