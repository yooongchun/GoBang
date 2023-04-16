"""
判断某矩阵是否存在子矩阵
"""
import cv2
import numpy as np
import pandas as pd


def is_sub_matrix(mat, kernel):
    """子矩阵是否存在"""
    kernel = kernel.astype(np.float32) / kernel.sum()
    dst = cv2.filter2D(mat.astype(np.float32), -1, kernel)
    print(pd.DataFrame(dst.astype(int)))


if __name__ == "__main__":
    mat = np.zeros((15, 15))
    kernel = np.zeros((2, 4, 4), dtype=np.float16)
    for x, y in [(0,0), (0,1), (0,2), (0,3), (1,3), (2,3),(3,3)]:
        kernel[0, x, y] = 1
        kernel[0, y, x] = 1
        mat[x+5, y+2] = 1
        mat[x+8, y+8] = 1
    
    print(pd.DataFrame(kernel.astype(int)))
    print(pd.DataFrame(mat.astype(int)))

    is_sub_matrix(mat, kernel)
