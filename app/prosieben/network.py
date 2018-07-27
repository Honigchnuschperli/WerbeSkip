from deepnet import Network
import cv2
import numpy as np
from app.image_processing.image_loader import load_ads_cnn
from app.image_processing.generator import TrainGenerator
from app.image_processing.retrieving_images import VideoCapture
from deepnet.layers import FullyConnectedLayer, BatchNorm, Dropout, ReLU, SoftMax, ConvolutionLayer, MaxPoolLayer, Flatten
from deepnet.optimizers import Adam, SGD
import time
import deepdish as dd

if __name__ == "__main__":

    gen = TrainGenerator(epochs=1, mini_batch_size=64, padding_w=151.5, padding_h=84.5, colour=False, channel="teleboy")
    net = Network()

    net.use_gpu = True

    net.input((1, 180, 320))

    net.add(ConvolutionLayer(n_filter=16, width_filter=12, height_filter=8, stride=4, zero_padding=0, padding_value=1))
    net.add(BatchNorm())
    net.add(ReLU())
    net.add(ConvolutionLayer(n_filter=64, width_filter=6, height_filter=4, stride=1, zero_padding=2, padding_value=1))
    net.add(BatchNorm())
    net.add(ReLU())
    net.add(MaxPoolLayer(width_filter=3, height_filter=3, stride=2))
    net.add(ConvolutionLayer(n_filter=128, width_filter=4, height_filter=4, stride=1))
    net.add(BatchNorm())
    net.add(ReLU())
    net.add(ConvolutionLayer(n_filter=128, width_filter=3, height_filter=3, stride=2))
    net.add(BatchNorm())
    net.add(ReLU())
    net.add(ConvolutionLayer(n_filter=256, width_filter=3, height_filter=3, stride=1))
    net.add(BatchNorm())
    net.add(Dropout(0.75))
    net.add(Flatten())
    net.add(FullyConnectedLayer(512))
    net.add(BatchNorm())
    net.add(ReLU())
    net.add(Dropout(0.5))
    net.add(FullyConnectedLayer(2))
    net.add(SoftMax())

    optimizer = Adam(learning_rate=0.001)
    net.regression(optimizer=optimizer, cost="cross_entropy")
    net.load("C:\Jetbrains\PyCharm\WerbeSkip\\app\prosieben\\networks\\teleboy\\teleboy.h5")
    x = 0
    l = []
    cap = VideoCapture(channel=354, colour=False, rate_limit=1)
    last_time = time.time()
    for img in cap:
        cv2.imshow("img", img)
        cv2.waitKey(1)
        img = np.expand_dims(img.transpose(2, 0, 1), axis=0) / 255
        hh = net.feedforward(img)
        o = float(hh[0, 1])
        x = 0
        print(time.time()-last_time)
        last_time = time.time()
