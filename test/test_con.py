# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
from unittest import TestCase

from fm22x.connection import Connection
from fm22x.response import MidReset, MidEnroll


class TestCon(TestCase):
    def setUp(self):
        self.con = Connection()

    def test_feed(self):
        for ev in self.con.receive(
            b"\xef\xaa"  # sync word
            + int.to_bytes(0x00, 1, "big")  # msg id
            + int.to_bytes(2, 2, "big")  # size
            + (0x10).to_bytes(1, "big")  # mid
            + (0).to_bytes(1, "big")  # result
            + int.to_bytes(18, 1, "big")  # checksum
        ):
            self.assertTrue(isinstance(ev, MidReset))

    def test_feed2(self):
        data = (
            b"\xef\xaa"  # sync word
            + int.to_bytes(0x00, 1, "big")  # msg id
            + int.to_bytes(2, 2, "big")  # size
            + (0x10).to_bytes(1, "big")  # mid
            + (0).to_bytes(1, "big")  # result
            + int.to_bytes(18, 1, "big")  # checksum
        )
        count = 0
        for ev in self.con.receive(data * 2):
            self.assertTrue(isinstance(ev, MidReset))
            count += 1
        self.assertEqual(count, 2)

    def test_feed_imcomplete(self):
        data = (
            b"\xef\xaa"  # sync word
            + int.to_bytes(0x00, 1, "big")  # msg id
            + int.to_bytes(2, 2, "big")  # size
            + (0x10).to_bytes(1, "big")  # mid
            + (0).to_bytes(1, "big")  # result
        )
        count = 0
        for ev in self.con.receive(data):
            self.assertTrue(isinstance(ev, MidReset))
            count += 1
        self.assertEqual(count, 0)
        count = 0
        for ev in self.con.receive(int.to_bytes(18, 1, "big")):  # checksum
            self.assertTrue(isinstance(ev, MidReset))
            count += 1
        self.assertEqual(count, 1)

    def test_wrong_syncword(self):
        data = (
            b"\xef\xab"
            + int.to_bytes(0x00, 1)
            + int.to_bytes(0, 2)
            + int.to_bytes(0x01, 1)
        )
        with self.assertRaises(ValueError):
            for ev in self.con.receive(data):
                pass

    def test_wrong_msg_id(self):
        data = (
            b"\xef\xab"
            + int.to_bytes(0x01, 1)
            + int.to_bytes(0, 2)
            + int.to_bytes(0x01, 1)
        )
        with self.assertRaises(ValueError):
            for ev in self.con.receive(data):
                pass

    def test_wrong_checksum(self):
        data = (
            b"\xef\xaa"
            + int.to_bytes(0x00, 1)
            + int.to_bytes(0, 2)
            + int.to_bytes(0x01, 1)
        )
        with self.assertRaises(ValueError):
            for ev in self.con.receive(data):
                pass

    def test_feed_note(self):
        data = [0xEF, 0xAA, 0x01, 0x00, 0x01, 0x00, 0x00]
        data = bytes(data)
        for ev in self.con.receive(data):
            print(ev)

    def test_receive_real(self):
        with open('../log.bin', 'rb') as f:
            data = f.read()
        for ev in self.con.receive(data):
            print(ev, ev.__dict__)

    def test_receive(self):
        # with open("../read.bin", "rb") as f:
        #     data = f.read()
        data = bytes.fromhex("EF AA 00 00 02 1D 0A 15")
        for ev in self.con.receive(data):
            print(ev, ev.__dict__)
            if isinstance(ev, MidEnroll):
                pass




if __name__ == "__main__":
    from unittest import main

    main()
