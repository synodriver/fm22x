# -*- coding: utf-8 -*-
from fm22x.event import Request, Response, SYNC_WORD, calculate_checksum
from typing import Iterable
from enum import Enum, auto


class _State(Enum):
    read_header = auto()
    read_data = auto()


class Connection:
    def __init__(self):
        self.buffer = bytearray()
        self.state = _State.read_header

        self._mid = None
        self._size = None  # tmp packet

    def send(self, req: Request) -> bytes:
        return req.encode()

    def receive(self, data: bytes) -> Iterable[Response]:
        self.buffer.extend(data)
        while True:
            if self.state == _State.read_header:
                if len(self.buffer) < 5:
                    break
                if self.buffer[:2] != SYNC_WORD:
                    raise ValueError("Invalid sync word")
                self._mid = self.buffer[2]
                self._size = int.from_bytes(self.buffer[3:5], "big")
                self.state = _State.read_data
            if self.state == _State.read_data:
                if len(self.buffer) < self._size + 6:
                    break
                data = self.buffer[5 : 5 + self._size]
                checksum = self.buffer[5 + self._size]
                if checksum != calculate_checksum(self.buffer[: 5 + self._size]):
                    raise ValueError("Invalid checksum")
                yield self._generate_response(data)
                del self.buffer[: self._size + 6]
                self.state = _State.read_header

    def _generate_response(self, data: bytes) -> Response:
        return Response.decode(self._mid, data)
