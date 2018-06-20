from deepnet.datasets import load_mnist_cnn
from deepnet.layers import FullyConnectedLayer, Dropout, ReLU, BatchNorm, SoftMax, ConvolutionLayer, MaxPoolLayer, Flatten
from deepnet.optimizers import Adam
from deepnet import Network


train_data, train_labels, test_data, test_labels = load_mnist_cnn()

net = Network()

net.use_gpu = True

net.input((1, 28, 28))

net.add(ConvolutionLayer(n_filter=32, width_filter=3, height_filter=3, stride=1, zero_padding=0))
net.add(BatchNorm())
net.add(ReLU())
net.add(ConvolutionLayer(n_filter=64, width_filter=3, height_filter=3, stride=1, zero_padding=0))
net.add(BatchNorm())
net.add(ReLU())
net.add(MaxPoolLayer(width_filter=2, height_filter=2, stride=1))
net.add(Dropout(0.75))
net.add(Flatten())
net.add(FullyConnectedLayer(128))
net.add(ReLU())
net.add(Dropout(0.5))
net.add(FullyConnectedLayer(10))
net.add(SoftMax())

optimizer = Adam(learning_rate=0.03)
net.regression(optimizer=optimizer, cost="cross_entropy")

net.fit(train_data, train_labels, validation_set=(test_data, test_labels),
        epochs=22, mini_batch_size=512, snapshot_step=2)
net.evaluate(test_data, test_labels)
