# -*- coding: utf-8 -*-
from fm22x.note import Note
from fm22x.request import Request, SYNC_WORD, calculate_checksum
from fm22x.response import Response
from typing import Iterable
from enum import Enum, auto


class _State(Enum):
    read_header = auto()
    read_data = auto()


class Connection:
    def __init__(self):
        self.buffer = bytearray()
        self.state = _State.read_header

        self._size = None  # tmp packet
        self._msg_id = None  # tmp packet

    def send(self, req: Request) -> bytes:
        return req.encode()

    def receive(self, data: bytes) -> Iterable[Response | Note]:
        self.buffer.extend(data)
        while True:
            if self.state == _State.read_header:
                if len(self.buffer) < 5:
                    break
                if self.buffer[:2] != SYNC_WORD:
                    raise ValueError("Invalid sync word")
                msg_id = self.buffer[2]
                if msg_id not in (0x00, 0x01):  # reply note
                    raise ValueError("Invalid msg id")
                self._msg_id = msg_id
                self._size = int.from_bytes(self.buffer[3:5], "big")
                self.state = _State.read_data
            if self.state == _State.read_data:
                if len(self.buffer) < self._size + 6:
                    break
                data = self.buffer[5 : 5 + self._size]
                checksum = self.buffer[5 + self._size]
                if checksum != calculate_checksum(self.buffer[: 5 + self._size]):
                    raise ValueError("Invalid checksum")
                if self._msg_id == 0x00:
                    yield self._generate_response(data)
                else:
                    yield self._generate_note(data)
                del self.buffer[: self._size + 6]
                self.state = _State.read_header

    def _generate_response(self, data: bytes) -> Response:
        d = Response.decode(data)
        if d.mid == 19:
            pass
        return d

    def _generate_note(self, data: bytes) -> Note:
        return Note.decode(data)
