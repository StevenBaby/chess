import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image

from logger import logger

BOARD = {
    (0, 0): '車', (0, 3): '卒', (0, 6): '兵', (0, 9): '俥',
    (1, 0): '馬', (1, 2): '砲', (1, 7): '炮', (1, 9): '傌',
    (2, 0): '象', (2, 3): '卒', (2, 6): '兵', (2, 9): '相',
    (3, 0): '士', (3, 9): '仕', (4, 0): '將', (4, 3): '卒',
    (4, 6): '兵', (4, 9): '帥', (5, 0): '士', (5, 9): '仕',
    (6, 0): '象', (6, 3): '卒', (6, 6): '兵', (6, 9): '相',
    (7, 0): '馬', (7, 2): '砲', (7, 7): '炮', (7, 9): '傌',
    (8, 0): '車', (8, 3): '卒', (8, 6): '兵', (8, 9): '俥'
}

INDEX = {
    '帥': (0, 0), '仕': (1, 0), '相': (2, 0), '傌': (3, 0), '俥': (4, 0), '炮': (5, 0), '兵': (6, 0),
    '將': (0, 1), '士': (1, 1), '象': (2, 1), '馬': (3, 1), '車': (4, 1), '砲': (5, 1), '卒': (6, 1),
}

NAME = {
    i: v
    for v, i in INDEX.items()
}


def find_board(img: np.array) -> np.ndarray:
    ratio = img.shape[0] / img.shape[1]
    width = 1920
    img = cv2.resize(img, (width, int(ratio * width)))

    gray = img[:, :, 0]
    blur = cv2.GaussianBlur(gray, (7, 7), 0.5)
    edges = cv2.Canny(blur, 50, 100)
    # return edges

    contours, hierarchy = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rects = []
    for cnt in contours:
        rect = cv2.boundingRect(cnt)
        (x, y, w, h) = rect
        if w < 100 or h < 100:
            continue

        ratio = w / h
        if ratio > 0.91 or ratio < 0.89:
            continue

        # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        rects.append(rect)

    if not rects:
        return None

    (x, y, w, h) = rects[0]
    croped = img[y:y + h, x: x + w]

    out = croped
    out = cv2.resize(out, (720, 800))
    return out


def make_piece(piece):
    img = cv2.resize(piece, (32, 32))
    img = img[2:23, 2:30]
    img = cv2.resize(piece, (32, 32))
    img = img / 255.0
    return img


def make_pieces(img):
    gray = img[:, :, 0]

    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, 1,
        minDist=30,
        param1=10,
        param2=30,
        minRadius=25,
        maxRadius=30)

    if circles is None:
        return None

    circles = np.uint16(np.around(circles))
    r = round(circles[0][:, 2].mean())

    pieces = []
    locs = []
    for i in circles[0]:

        x = round(i[0]) - r
        y = round(i[1]) - r

        # cv2.circle(img, (i[0], i[1]), r, (0, 255, 0), 1)

        loc = (i[0] // 80, i[1] // 80)

        piece = img[y:y + r * 2, x: x + r * 2]
        piece = make_piece(piece)
        pieces.append(piece)
        locs.append(loc)

    return pieces, locs


def plot_board(locs, idxs, pieces=None):
    colors = {
        0: 'red',
        1: 'white',
    }

    import matplotlib as mpl
    mpl.rcParams["font.sans-serif"] = ["Dengxian"]   # 设置显示中文字体
    mpl.rcParams["axes.unicode_minus"] = False   # 设置正常显示符号

    import itertools
    figure = plt.figure(figsize=(5, 5.5))
    figure.tight_layout()

    ax = figure.subplots()
    ax.axis('off')

    for y in range(10):
        ax.plot([0, 8], [y, y], color='k')

    for x in (0, 8):
        ax.plot([x, x], [0, 9], color='k')

    for x in range(1, 8):
        ax.plot([x, x], [0, 4], color='k')
        ax.plot([x, x], [5, 9], color='k')

    ax.plot([3, 5], [0, 2], color='k')
    ax.plot([3, 5], [2, 0], color='k')

    ax.plot([3, 5], [7, 9], color='k')
    ax.plot([3, 5], [9, 7], color='k')

    for i, loc in enumerate(locs):
        # ax.Circle
        x = loc[0]
        y = 9 - loc[1]

        ax.scatter([x], [y], s=[600], color='black', alpha=1)
        ax.text(x - 0.3, y - 0.17,
                str(NAME[idxs[i]]),
                size=18,
                color=colors[idxs[i][1]])


def plot_pieces(locs, pieces):

    figure = plt.figure(figsize=(5, 5.5))
    figure.tight_layout()

    axes = figure.subplots(10, 9)

    for row in axes:
        for ax in row:
            ax.axis("off")

    for i, loc in enumerate(locs):
        x = loc[0]
        y = loc[1]
        axes[y, x].imshow(pieces[i])
