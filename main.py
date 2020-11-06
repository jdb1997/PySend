#! /usr/bin/env python
# A program created to send file(s)
# and/or directories using TCP/IP
# Author: James Bryant
import argparse
import pathlib
from PySend import client, server


def serv(address, directory, debug):
    file_serv = server.Server(address, debug)
    file_serv.init_serv(directory)
    file_serv.start_serv()


def recv(address, directory, debug):
    file_client = client.Client(debug)
    file_client.init_client(directory)
    file_client.connect(address)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Program used to send file(s) and/or directories of a TCP/IP socket")

    parser.add_argument(
        "--addr", help="Address of server, or address of the client. default: 127.0.0.1",
        default="127.0.0.1")
    parser.add_argument(
        "--port", help="Port of server, or client. default: 5000", type=int, default=5000)
    parser.add_argument(
        "--serv", help="Using this argument causes the program to act as a server, " +
                       "without the argument the program acts as a client", action="store_true")
    parser.add_argument(
        "--dir", help="Directory of what to be sent, defaults to CWD", default=pathlib.Path())
    parser.add_argument(
        "--debug", help="To debug, or not to debug!", action="store_true")

    args = parser.parse_args()

    # Converts string to Path obj if a directory is given
    if not isinstance(args.dir, pathlib.Path):
        args.dir = pathlib.Path(args.dir)

    if args.serv:
        serv((args.addr, args.port), args.dir, args.debug)
    elif not args.serv:
        recv((args.addr, args.port), args.dir, args.debug)
