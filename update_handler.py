from deepnet import Network
import numpy as np
from helperfunctions.image_processing.retrieving_images import VideoCapture
from deepnet.layers import FullyConnectedLayer, BatchNorm, Dropout, ReLU, SoftMax, ConvolutionLayer, MaxPoolLayer, \
    Flatten
from deepnet.optimizers import Adam
import json
import websocket
import _thread as thread
import time


class WerbeSkip(object):
    def __init__(self):
        self.network = self.init_network()
        # Prosieben: 354
        # SRF: 303
        self.cap = VideoCapture(channel=354, colour=False, rate_limit=1, convert_network=True)

        self.filters = []
        self.result = []
        self.predictions = []

        self.filter_size = 25
        self.chain_size = 5

    def init_network(self):
        net = Network()

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
        net.load("helperfunctions\prosieben\\networks\\teleboy\\teleboy.h5")
        return net

    def producer(self):
        channel = self.get_prediction()
        message = {"command": "update", "room": 'main', "channel": channel, 'token': 'NWcVm69HTM4kQ2giE7JQ20buzQmu7uGcfNxftTC1'}
        return message

    def get_prediction(self):
        img = next(self.cap)

        prediction = self.network.feedforward(img)

        self.predictions.append(prediction[0, 1])
        snippet = self.predictions[self.filter_size:]
        if np.any(np.array(snippet) > 0.9):  # checks if network is sure that it found a logo
            self.filters.append(1)
        else:
            self.filters.append(0)

        last_filter = self.filters[-1]
        if np.all(np.array(self.filters[-self.chain_size:]) == last_filter):  # checks if the last values are the same
            if last_filter == 1:
                if np.mean(self.predictions[self.chain_size:]) > 0.9:
                    self.result.append(last_filter)
                else:
                    self.result.append(self.result[-1])
            else:
                self.result.append(last_filter)
        else:
            self.result.append(self.result[-1])

        self.clean_up()
        return {"Prosieben": {"ad": self.result[-1], "id": 354}}

    def clean_up(self):
        if len(self.predictions) > 2 * self.filter_size and len(self.filters) > 2 * self.chain_size:
            self.filters.pop(0)
            self.result.pop(0)
            self.predictions.pop(0)

    def on_message(self, ws, message):
        error = json.loads(message).get('error', None)
        if error:
            print('GOT ERROR:', error)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")
        time.sleep(10)
        self.run()

    def on_open(self, ws):
        def run(*args):
            while True:
                message = self.producer()
                ws.send(json.dumps(message))

        thread.start_new_thread(run, ())

    def run(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://127.0.0.1:8000/chat/stream/",
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever()


if __name__ == "__main__":
    x = WerbeSkip()
    x.run()

