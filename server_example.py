import server
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    required_dirs = ["example/"]
    required_files = ["functions_example.py", "multiprocess.py"]
    required_files = [required_dirs[0] + f for f in required_files]
    module_to_start = required_files[0][:-3].replace("/", ".")
    function_to_start = "map_it"

    with server.Server("localhost", 55555, required_dirs, required_files) as s:
        s.start_server()
        data = list(range(100))
        ret = s.send_data_to_compute(data, module_to_start, function_to_start)
        s.stop_server()
        logger.info("result: {}".format(ret))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
