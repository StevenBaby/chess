import os
import glob
import itertools
import pickle

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import torch
import torch.nn as nn
import torch.cuda
import torch.nn.functional as F
import torch.utils.data

from tqdm import tqdm

from . import (
    find_board,
    make_pieces,
    make_piece,
    BOARD,
    INDEX,
)

import capture

from logger import logger


if torch.cuda.is_available():
    device = torch.device("cuda")
    type = torch.cuda.FloatTensor
else:
    device = torch.device("cpu")
    type = torch.FloatTensor
torch.set_default_tensor_type(type)


DIRNAME = os.path.dirname(__file__)
MODELPATH = os.path.join(DIRNAME, 'model.pkl')
QQBOARD = os.path.join(DIRNAME, 'images/qqboard*.png')
model = None


class Dataset(torch.utils.data.Dataset):

    def __init__(self, image=None, board=None) -> None:
        super().__init__()
        self.labels = []
        self.images = []

        logger.info("load board datasets...")

        files = glob.glob(QQBOARD)
        for filename in files:
            qqboard = np.asarray(Image.open(filename).convert("RGB"))
            gray = qqboard[:, :, 0]

            circles = cv2.HoughCircles(
                gray, cv2.HOUGH_GRADIENT, 1,
                minDist=30,
                param1=10,
                param2=30,
                minRadius=25,
                maxRadius=30)

            if circles is None:
                continue

            circles = np.uint16(np.around(circles))
            r = round(circles[0][:, 2].mean())

            pieces = []

            for i in circles[0]:
                loc = (i[0] // 80, i[1] // 80)

                for offx, offy in itertools.product(range(-10, 10), range(-10, 10)):
                    x = round(i[0]) - r + offx
                    y = round(i[1]) - r + offy
                    piece = qqboard[y:y + r * 2, x: x + r * 2]
                    piece = make_piece(piece)
                    piece = torch.from_numpy(piece).float().permute(2, 0, 1)
                    self.images.append(piece)
                    idx = INDEX[BOARD[loc]]
                    self.labels.append(idx[0] + idx[1] * 7)

        self.labels = torch.LongTensor(self.labels)
        logger.info("load board datasets finished....")

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        return self.images[index], self.labels[index]


class Classifier(nn.Module):

    def forward(self, x):
        return self.model(x)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.model = nn.Sequential(
            nn.Conv2d(3, 64, 4, 2, 1),
            nn.LazyBatchNorm2d(),
            nn.LeakyReLU(0.2),

            nn.Conv2d(64, 32, 4, 2, 1),
            nn.LazyBatchNorm2d(),
            nn.LeakyReLU(0.2),

            nn.Flatten(),

            nn.LazyLinear(64),
            nn.LazyBatchNorm1d(),
            nn.LeakyReLU(0.2),

            nn.LazyLinear(len(INDEX)),
            nn.Sigmoid(),
        )

    def predict(self, x: torch.Tensor):
        x = x.to(device)
        y = self.forward(x)
        y = torch.argmax(y, dim=x.dim() - 3)

        name = (y % 7).unsqueeze_(0)
        color = (y // 7).unsqueeze_(0)

        idxs = torch.cat((name, color)).permute(1, 0)
        idxs = [tuple(var) for var in idxs.detach().cpu().numpy()]
        return idxs


def train(epoch=120):
    dataset = Dataset()

    trainset, valset = torch.utils.data.random_split(
        dataset, [int(len(dataset) * 0.7), int(len(dataset) * 0.3)],
        generator=torch.Generator(device=device)
    )

    trainloader = torch.utils.data.DataLoader(
        dataset=trainset,
        batch_size=256,
        shuffle=True,
        generator=torch.Generator(device=device),
    )

    valoader = torch.utils.data.DataLoader(
        dataset=trainset,
        batch_size=256,
        shuffle=True,
        generator=torch.Generator(device=device),
    )

    model = Classifier()
    model.to(device)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.0005,
    )
    criterion = nn.BCELoss()

    bar = tqdm(range(epoch))
    loss = 0
    acc = 0
    for _ in bar:
        model.train()
        for x, t in trainloader:
            x = x.to(device)
            t = F.one_hot(t, len(INDEX)).float().to(device)
            y = model.forward(x)

            loss = criterion(y, t)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            loss = loss.item()
            bar.set_postfix(loss=loss, acc=acc)

        model.eval()
        total = 0.0
        right = 0.0
        for x, t in valoader:

            x = x.to(device)
            t = F.one_hot(t, len(INDEX)).float().to(device)
            y = model.forward(x)
            right += torch.sum(torch.argmax(y, dim=1) == torch.argmax(t, dim=1))
            total += t.shape[0]

            acc = float(right / total)
            bar.set_postfix(loss=loss, acc=acc)

    return model


def save_model(model):
    dirname = os.path.dirname(MODELPATH)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(MODELPATH, 'wb') as file:
        file.write(pickle.dumps(model))


def load_model() -> nn.Module:
    logger.info("load model...")
    if not os.path.exists(MODELPATH):
        model = train()
        save_model(model)
    else:
        with open(MODELPATH, 'rb') as file:
            model = pickle.loads(file.read())
        model.eval()
    logger.info("load model finish...")
    return model


def get_model():
    global model
    if model is None:
        model = load_model()
    return model


def get_board():
    img = capture.capture("天天象棋")
    if not img:
        return None

    img = np.asarray(img).copy()
    img = find_board(img)
    if img is None:
        return None

    pieces, locs = make_pieces(img)

    x = []
    for piece in pieces:
        piece = torch.from_numpy(piece).float().permute(2, 0, 1).unsqueeze_(0)
        x.append(piece)

    x = torch.cat(x)

    model = get_model()
    idxs = model.predict(x)
    board = {}
    for i, idx in enumerate(idxs):
        board[locs[i]] = idx

    return board
