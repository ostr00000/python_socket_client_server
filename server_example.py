import server
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    required = ["functions_example.py", "multiprocess.py"]
    with server.Server("localhost", 55555, required) as s:
        s.start_server()
        data = list(range(100))
        ret = s.send_data_to_compute(data, required[0][:-3], "map_it")
        s.stop_server()
        logger.info("result: {}".format(ret))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
