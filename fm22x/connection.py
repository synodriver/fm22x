# -*- coding: utf-8 -*-
from fm22x.event import Request, Response


class Connection:
    def send(self, req: Request) -> bytes: ...

    def receive(self, data: bytes) -> Response: ...
