# -*- coding: utf-8 -*-
from typing_extensions import Self, Protocol


class ProtocolFrame(Protocol):
    def encode(self) -> bytes: ...

    @classmethod
    def decode(cls, raw: bytes) -> Self: ...

    def validate(self) -> bool: ...
