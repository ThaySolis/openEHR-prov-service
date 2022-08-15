from functools import wraps
import time

class CircularBuffer:
    """
    A very, very simple circular buffer.
    """

    def __init__(self, amount : int):
        self._initial_index = 0
        self._amount = 0
        self._buffer = [0.0] * amount

    def add(self, value : float):
        """
        Adds a value to the circular buffer.
        """

        final_index = (self._initial_index + self._amount) % len(self._buffer)
        self._buffer[final_index] = value
        if self._amount < len(self._buffer):
            self._amount += 1
        else:
            self._initial_index = (self._initial_index + 1) % len(self._buffer)

    def clear(self):
        """
        Clears the circular buffer.
        """

        self._initial_index = 0
        self._amount = 0

    def to_list(self) -> list:
        """
        Converts the contents of the buffer to a list.
        """

        if self._amount == 0:
            return []

        final_index = (self._initial_index + self._amount) % len(self._buffer)
        if final_index > self._initial_index:
            return self._buffer[self._initial_index:final_index]
        else:
            return self._buffer[self._initial_index:]+self._buffer[:final_index]

class TimedGroup:
    """
    A group of functions timed as a group.
    """

    def __init__(self, max_samples : int):
        self._samples = CircularBuffer(max_samples)

    def get_samples(self) -> list:
        return self._samples.to_list()

    def add_sample(self, value : float):
        self._samples.add(value)

    def clear(self):
        self._samples.clear()

    def wrap(self, fn):
        """
        Wraps a function to be measured.
        """

        # inspired by <https://dev.to/kcdchennai/python-decorator-to-measure-execution-time-54hk>
        @wraps(fn)
        def wrapped_function(*args, **kwargs):
            start_time = time.perf_counter()
            result = fn(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time

            self.add_sample(total_time)

            return result
        return wrapped_function

class Timed:
    """
    A class which holds timed measurements.
    """

    def __init__(self, max_samples : int):
        self._groups = {}
        self._max_samples = max_samples

    def measure(self, name : str):
        """
        Creates a decorator that wraps a function to be measured with a given name.
        """

        def wrapper(fn):
            return self.get_group(name).wrap(fn)
        return wrapper

    def clear_all(self):
        """
        Clears all measurements so far.
        """

        for name in self._groups:
            self._groups[name].clear()

    def get_group(self, name : str) -> TimedGroup:
        """
        Gets the timed group with a given name.
        """

        if name not in self._groups:
            self._groups[name] = TimedGroup(self._max_samples)
        return self._groups[name]

class NotTimed:
    """
    A class which provided the same API as the Timed class, but does not collect any timing data.
    """

    def measure(self, name : str):
        def wrapper(fn):
            return fn
        return wrapper

    def clear_all(self):
        pass

    def get_group(self, name : str) -> TimedGroup:
        return None
