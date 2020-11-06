import socket
import logging
import sys
# import pathlib


class Server(object):

    def __init__(self, address, debug=False):
        # TODO: Need to configure logger formatting
        self.logger = logging.getLogger(__name__)

        if debug:
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
        else:
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.server_runtime = True
        self.buffer = 1024
        self.address = address
        self.total_files = 0
        self.total_files_sent = 0
        self.total_dirs = 0
        self.total_bytes = 0
        self.total_bytes_sent = 0
        # Catalog contains all the directories and files paths and the size of the file
        # Example "DIR:example/EXAMPLE/ExAmPlE,FILE:1234:example/example.png"
        # The idea is that the client Splits the string with "," and then can Loop through and make the dirs
        # and then request the files!
        self.catalog = ""

    def init_serv(self, directory):
        self.logger.info("Directory: " + directory.as_posix())

        if not directory.exists():
            self.logger.critical("Directory/File does not exist, Program is exiting")
            quit()

        self.make_catalog(directory)

        self.total_bytes += len(self.catalog)

    def start_serv(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.bind(self.address)
            self.logger.info("Server listening on: " + self.address[0] + ":" + str(self.address[1]))

            self.logger.info("Total directories: " + str(self.total_dirs))
            self.logger.info("Total files: " + str(self.total_files))
            self.logger.info("Total bytes: " + str(self.total_bytes))

            server_sock.listen(1)

            while self.server_runtime:
                client_sock, client_address = server_sock.accept()
                client_adr_str = client_address[0] + ":" + str(client_address[1])
                self.logger.debug("Connection at: " + client_adr_str)

                with client_sock:
                    # On client connect the server checks what it request
                    # i.e. CATALOG, FILE, SUCCESFULL
                    client_response = self.recv_all(client_sock).decode("ascii")

                    if client_response == "CATALOG":
                        self.logger.info(client_adr_str + " requested a catalog")
                        client_sock.sendall(self.catalog.encode("ascii"))
                        self.logger.info("Catalog sent: " + client_adr_str)
                        self.total_bytes_sent += len(self.catalog)
                    elif client_response.startswith("FILE:"):
                        if client_response in self.catalog:
                            # Takes the request sent by client
                            # i.e. FILE:22:example/example.txt
                            # send_file returns total bytes sent
                            path_type, file_size, filename = client_response.split(":")
                            self.logger.info("Sending: " + filename)
                            bytes_sent = self.send_file(filename, client_sock)
                            self.logger.debug("Bytes sent: " + str(bytes_sent))
                            self.total_bytes_sent += bytes_sent
                            self.total_files_sent += 1

                            if bytes_sent != int(file_size):
                                # Warns server that it didn't send all the bytes of a file
                                self.logger.warning("Didn't send all bytes")
                                self.logger.warning("File: " + filename)
                                self.logger.warning("Size: " + str(file_size))
                        else:
                            # Tells server that the file requested was not in the catalog
                            # Also so the client cant request random files if they know the path LOL
                            self.logger.warning("Client requested a file that is not in the catalog!")
                            self.logger.warning("File requested: " + client_response)
                    elif client_response == "SUCCESSFULL":
                        # Client sends "SUCCESSFULL" when it has grabbed all the files in the catalog
                        self.server_runtime = False
                    elif client_response == "ERROR":
                        # Tells the server the client encountered an error
                        self.logger.critical("The client has encountered an error!")
                        self.logger.critical("Exiting!")
                        quit()

            self.logger.info("Total files sent: " + str(self.total_files_sent))
            self.logger.info("Total bytes sent: " + str(self.total_bytes_sent))

    def send_file(self, filename, sock):
        bytes_sent = 0

        with open(filename, "rb") as f:
            while True:
                # Used so the program doesn't load the whole file at once. i.e. if you have 10Gb file
                # socket.send() returns bytes sent I figured send_file should do the same!
                data = f.read(self.buffer)

                if data != b"":
                    sock.send(data)
                    bytes_sent += len(data)
                else:
                    break

        return bytes_sent

    def recv_all(self, sock):
        data = b""

        while True:
            recv = sock.recv(self.buffer)

            if recv != b"":
                data += recv
            else:
                break

        return data

    def make_catalog(self, directory):
        # Used to populate catalog, it is called recursively(Pretty neat!)
        if directory.is_dir():
            self.catalog += "DIR:" + directory.as_posix() + ","
            self.total_dirs += 1
            self.logger.debug("DIR:" + directory.as_posix())

            for child in directory.iterdir():
                self.make_catalog(child)
        elif directory.is_file():
            posix_path = directory.as_posix()
            file_size = str(directory.stat().st_size)
            self.total_bytes += directory.stat().st_size

            self.catalog += "FILE:" + file_size + ":" + posix_path + ","
            self.total_files += 1
            self.logger.debug("FILE:" + file_size + ":" + posix_path)
        else:
            self.logger.critical("Input is neither a file or directory, Program is exiting")
            quit()
