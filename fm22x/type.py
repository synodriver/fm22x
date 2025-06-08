# -*- coding: utf-8 -*-
from typing import Protocol, Self


class ProtocolFrame(Protocol):
    def encode(self) -> bytes:
        ...

    @classmethod
    def decode(cls, raw: bytes) -> Self:
        ...

    def validate(self) -> bool:
        ...
