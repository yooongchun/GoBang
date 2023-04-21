#! /usr/bin/env python3
#! -*- coding: utf-8 -*-
"""
Utils
"""

def trans(c):
    """转换表示"""
    if c == 0:
        return "-"
    if c == 1:
        return "x"
    return "o"


def show(matrix):
    """display matrix readable"""
    print("  " + "  ".join(str(i) for i in range(len(matrix))))
    for i in range(len(matrix)):
        row_str = '  '.join(trans(v) for j, v in enumerate(matrix[i]))
        print(f"{i} " + row_str)
