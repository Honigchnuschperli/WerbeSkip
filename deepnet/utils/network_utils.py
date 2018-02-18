import numpy as np


def shuffle(x, y):
    """
    Shuffles data in unison with helping from indexing
    :param x: ndarray
    :param y: ndarray
    :return x, y: ndarray
    """
    indexes = np.random.permutation(x.shape[1])
    return x[..., indexes], y[..., indexes]


def make_mini_batches(x, y, size):
    """
    Shuffles data and makes mini batches
    :param x: ndarray
    :param y: ndarray
    :param size: unsigned int
    :return mini_batches: list with ndarray's
    """
    x, y = shuffle(x, y)
    mini_batches = []
    for i in range(0, x.shape[1], size):
        mini_batches.append((x[:, i:size + i], y[:, i:size + i]))
    return mini_batches