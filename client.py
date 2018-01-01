from connection import *
import os
import sys
import shutil
from typing import Optional, IO, List, Tuple
import argparse
import multiprocessing
import logging

directory = "./downloaded/"
THREADS = 8
DECLARED_WORK = 44

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + directory[1:])

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="example: '100.50.200.5'", type=str)
    parser.add_argument("port", type=int, help="number of port to connect")
    parser.add_argument("-t", "--threads", type=int,
                        help="number of threads to start",
                        default=multiprocessing.cpu_count())
    global args
    args = parser.parse_args()
    THREADS = args.threads


template = """
from {dir}.{m_name} import {f_name}
_ret = {f_name}
"""


class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.map_function = None
        self.my_dir = os.path.dirname(os.path.abspath(__file__))

    def _download_file(self):
        if os.path.exists(directory):
            shutil.rmtree(directory[:-1])
        os.makedirs(directory)

        files_num = receive(self.sock)

        for i in range(files_num):
            filename = receive(self.sock)
            data = receive(self.sock)
            with open(directory + filename, 'w') \
                    as new_file:  # type: Optional[IO[str]]
                print(data, file=new_file, end='')

    def start_client(self):
        response = receive(self.sock)
        logger.debug("needed modules {}".format(response))

        if not self._has_all_files(response):
            send(MessageType.download, self.sock)
            logger.debug("downloading modules")
            self._download_file()
            logger.debug("modules downloaded")

        send(MessageType.get_work, self.sock)
        send(DECLARED_WORK, self.sock)

        while True:
            logger.debug("waiting for orders")
            order = receive(self.sock)

            if order == MessageType.end:
                logger.debug("message from server: end")
                self.sock.close()
                break

            elif order == MessageType.compute:
                server_args = receive(self.sock)
                function_args, server_id = list(zip(*server_args))

                module_name, function_name = receive(self.sock)
                logger.debug("received module: '{}', function: '{}'"
                             .format(module_name, function_name))
                self._prepare_function(module_name, function_name)

                # send("fuck you", self.sock)
                # logger.debug("revolt!")
                # continue

                function_result = self.map_function[2](function_args)

                client_result = list(zip(server_id, function_result))
                send(client_result, self.sock)

            else:
                logger.warning("unexpected message from server")
                break

    @staticmethod
    def _has_all_files(files: List[Tuple[str, int]]):

        for name, size in files:
            name = directory + name
            if not os.path.exists(name):
                # logger.debug("file doesn't exist '{}'".format(name))
                return False
            if os.stat(name).st_size != size:
                # logger.debug("file '{}' has wrong size,"
                #              " should be {}, but is {}"
                #              .format(name, os.stat(name).st_size, size))
                return False
        return True

    def _prepare_function(self, module_name, function_name):
        if ((not self.map_function
             or self.map_function[0] != module_name
             or self.map_function[1] != function_name)):

            to_compile = template.format(m_name=module_name,
                                         f_name=function_name,
                                         dir=directory[2:-1])

            comp = compile(to_compile, '<string>', 'exec')
            loc = {}
            exec(comp, {}, loc)
            self.map_function = (module_name, function_name, loc['_ret'])


if __name__ == "__main__":
    c = Client(args.host, args.port)
    c.start_client()
