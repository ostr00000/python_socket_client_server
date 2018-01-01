import typing
import multiprocess

arg_num = 7


def square_plus(x):
    return x ** 2 + arg_num


def map_it(data: typing.List):
    return multiprocess.parallel_map(square_plus, data)
