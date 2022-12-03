from __future__ import annotations

import argparse
import http.server
import os
import socket
import typing

import qrcode


def get_ip_addr() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))
    return s.getsockname()[0]


def get_free_port(range_: tuple[int, int]) -> int:
    for port in range(*range_):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            in_use = s.connect_ex(("localhost", port)) == 0
            if not in_use:
                return port
    raise OSError(f"Failed to find free port in range {range_}.")


def print_qr(data: str) -> None:
    qr = qrcode.QRCode()
    qr.add_data(data)
    qr.print_ascii()


def start_server(directory: str, host: str, port: int) -> None:
    httpd = http.server.HTTPServer(
        (host, port),
        lambda *args: http.server.SimpleHTTPRequestHandler(  # type: ignore
            *args, directory=directory
        ),
    )
    httpd.serve_forever()


def main(argv: typing.Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sharez", description="Share directory in your local network"
    )
    parser.add_argument(
        "directory",
        action="store",
    )
    parser.add_argument(
        "--host",
        default=None,
        action="store",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        action="store",
    )
    args = parser.parse_args(argv)

    if not os.path.exists(args.directory):
        raise FileNotFoundError(args.directory)

    ip = args.host or get_ip_addr()
    port = int(args.port) or get_free_port((7500, 7800))
    url = f"http://{ip}:{port}"
    print_qr(url)
    print(f"Sharing {args.directory!r} at {url}")
    try:
        start_server(args.directory, host=ip, port=port)
    except KeyboardInterrupt:
        print("\rShutting down...")
    return 0
