# -*- coding: utf-8 -*-
from unittest import TestCase

from fm22x.connection import Connection
from fm22x.event import MidReset


class TestCon(TestCase):
    def setUp(self):
        self.con = Connection()

    def test_feed(self):
        for ev in self.con.receive(
            b"\xef\xaa"
            + int.to_bytes(0x10, 1)
            + int.to_bytes(0, 2)
            + int.to_bytes(0x10, 1)
        ):
            self.assertTrue(isinstance(ev, MidReset))

    def test_feed2(self):
        data = (
            b"\xef\xaa"
            + int.to_bytes(0x10, 1)
            + int.to_bytes(0, 2)
            + int.to_bytes(0x10, 1)
        )
        count = 0
        for ev in self.con.receive(data * 2):
            self.assertTrue(isinstance(ev, MidReset))
            count += 1
        self.assertEqual(count, 2)

    def test_feed_imcomplete(self):
        data = b"\xef\xaa" + int.to_bytes(0x10, 1) + int.to_bytes(0, 2)
        count = 0
        for ev in self.con.receive(data):
            self.assertTrue(isinstance(ev, MidReset))
            count += 1
        self.assertEqual(count, 0)
        count = 0
        for ev in self.con.receive(int.to_bytes(0x10, 1)):
            self.assertTrue(isinstance(ev, MidReset))
            count += 1
        self.assertEqual(count, 1)


if __name__ == "__main__":
    from unittest import main

    main()
