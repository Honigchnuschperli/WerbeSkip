import platform
import ctypes
import numpy
import time


class IOHandler(object):
    """The IOHandler"""
    def __init__(self, network):
        self.DICTIONARY = {
            "epoch": self._s_epoch,
            "progress": self._s_progress,
            "train_loss": self._s_tl,
            "train_accuracy": self._s_ta,
            "validate_loss": self._s_vl,
            "validate_accuracy": self._s_va,
            "time": self._s_time,
        }
        self.start_time = time.time()
        self.network = network
        self.activate_ansi()
        self._metric_last_update = 0

    def _s_epoch(self) -> str:
        return "epoch {} of {}".format(self.network.current_epoch + 1, self.network.total_epoch)

    def _s_progress(self) -> str:
        return "progress: {:.3f}".format(self.network.progress)

    def _s_tl(self) -> str:
        return "train loss: {:.5f}".format(numpy.mean(self.network.train_loss[-100:]))

    def _s_ta(self) -> str:
        return "train accuracy: {:.5f}".format(numpy.mean(self.network.train_accuracy[-100:]))

    def _s_vl(self) -> str:
        return "validate loss: {:.5f}".format(numpy.mean(self.network.validate_loss[-100:]))

    def _s_va(self) -> str:
        return "validate accuracy: {:.5f}".format(numpy.mean(self.network.validate_accuracy[-100:]))

    def _s_time(self) -> str:
        return "time {:.3f}".format(time.time() - self.start_time)

    @staticmethod
    def activate_ansi():
        if platform.system() == "Windows" and platform.release() == "10":
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    def print_metrics(self, metrics: tuple or list, snapshot_step: int):
        if snapshot_step < time.time() - self._metric_last_update:
            self._print_metrics(metrics=metrics)
            self._metric_last_update = time.time()

    def _print_metrics(self, metrics: tuple or list) -> None:
        """
        prints all metric which are in the list.
        If "all" is in the first position it will
        print every metric.
        :param metrics: list with metrics as string
        """
        if metrics[0] == "all":
            metrics = self.DICTIONARY.keys()

        result = ""
        for index, metric in enumerate(metrics):
            result += self.DICTIONARY[metric]()
            if index + 1 < len(metrics):
                if len(result.split("\n")[-1]) > 60:
                    result += "\n"
                else:
                    result += " | "
        print("\033[F\033[F" + result)
