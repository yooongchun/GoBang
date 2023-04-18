#! /usr/bin/env python3
#! -*- coding: utf-8 -*-
"""
Utils
"""

def show(matrix):
    """display matrix readable"""
    for i in range(len(matrix)):
        row_str = ' '.join(str(v) for v in matrix[i])
        print(row_str)
