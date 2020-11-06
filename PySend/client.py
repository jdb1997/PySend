import socket
import logging
import sys
import pathlib
import queue


class Client(object):

    def __init__(self, buffer=1024, debug=False):
        # TODO: Need to configure logger formatting
        self.logger = logging.getLogger(__name__)

        if debug:
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
        else:
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.error = False
        self.buffer = buffer
        self.output_dir = pathlib.Path().cwd()
        self.total_files = 0
        self.total_files_created = 0
        self.total_dirs = 0
        self.total_dirs_created = 0
        self.total_bytes = 0
        self.total_bytes_received = 0
        self.file_queue = queue.Queue()

    def init_client(self, directory):
        if not directory.exists():
            self.logger.warning("Directory doesn't exist! Directory is being created")
            self.output_dir = pathlib.Path.cwd().joinpath(directory)
            self.output_dir.mkdir()
        else:
            self.output_dir = directory

    def recv_all(self, sock):
        data = b""

        while True:
            sock_data = sock.recv(self.buffer)

            if sock_data != b"":
                data += sock_data
            else:
                break

        return data

    def recv_file(self, filename, sock):
        recv_data = 0

        with open(self.output_dir.joinpath(filename), "wb") as f:
            while True:
                sock_data = sock.recv(self.buffer)

                if sock_data != b"":
                    f.write(sock_data)
                    recv_data += len(sock_data)
                else:
                    break

        return recv_data

    def connect(self, address):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.connect(address)

            server_sock.send("CATALOG".encode("ascii"))
            # Shutdown is called to tell the server we're done sending
            # Otherwise TCP deadlock occurs
            server_sock.shutdown(socket.SHUT_WR)

            catalog = self.recv_all(server_sock).decode("ascii")
            self.total_bytes_received += len(catalog)
            self.logger.debug("Catalog received")
            self.parse_catalog(catalog)

            while not self.file_queue.empty():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as file_sock:

                    file_info = self.file_queue.get()
                    path_type, expected_bytes, filename = file_info.split(":")
                    filename = pathlib.Path(filename)

                    if self.output_dir.joinpath(filename).exists():
                        self.logger.warning("EXISTS: " + filename.as_posix())
                        continue
                    elif not self.output_dir.joinpath(filename).exists():
                        file_sock.connect(address)

                        if self.error:
                            file_sock.send("ERROR".encode("ascii"))
                            self.logger.critical("Exiting!")
                            quit()

                        file_sock.send(file_info.encode("ascii"))
                        file_sock.shutdown(socket.SHUT_WR)

                        bytes_received = self.recv_file(filename, file_sock)
                        self.total_bytes_received += bytes_received

                        if bytes_received != int(expected_bytes):
                            self.logger.critical("Didn't receive all bytes: " + filename)
                            self.error = True

                        self.total_files_created += 1

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as exit_sock:
                exit_sock.connect(address)
                exit_sock.send("SUCCESSFULL".encode("ascii"))

            self.logger.info("~~Report~~")
            self.logger.info("Files created: " + str(self.total_files_created))
            self.logger.info("Dirs created: " + str(self.total_dirs_created))
            self.logger.info("Bytes received: " + str(self.total_bytes_received))

    def parse_catalog(self, catalog):
        for item in catalog.split(","):
            if item.startswith("FILE:"):
                self.file_queue.put(item)
                self.total_files += 1
            if item.startswith("DIR:"):
                path = self.output_dir.joinpath(pathlib.Path(item.split(":")[1]))
                self.make_directory(path)

        self.logger.debug("~~Catalog contains~~")
        self.logger.debug("Total files: " + str(self.total_files))
        self.logger.debug("Total directories: " + str(self.total_dirs))

    def make_directory(self, directory):
        # Makes sure a directory doesn't exists before it creates it
        if directory.exists():
            self.logger.warning("EXISTS: " + directory.as_posix())
        else:
            directory.mkdir()
            self.total_dirs_created += 1
