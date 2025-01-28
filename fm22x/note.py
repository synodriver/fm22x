# -*- coding: utf-8 -*-
from typing import Self
from enum import IntEnum


class NID(IntEnum):
    READY = 0
    FACE_STATE = 1  # 算法执行成功，并且返回人脸信息_note_data_face
    UNKNOWNERROR = 2  # 未知错误
    OTA_DONE = 3
    EYE_STATE = 4


class FaceState(IntEnum):
    NORMAL = 0
    NOFACE = 1
    TOOUP = 2
    TOODOWN = 3
    TOOLEFT = 4
    TOORIGHT = 5
    FAR = 6
    CLOSE = 7
    EYEBROW_OCCLUSION = 8
    EYE_OCCLUSION = 9
    FACE_OCCLUSION = 10
    DIRECTION_ERROR = 11
    EYE_CLOSE_STATUS_OPEN_EYE = 12
    EYE_CLOSE_STATUS = 13
    UNKNOW_STATUS = 14


class NoteMeta(type):
    register_types = {}

    def __new__(cls, name, bases, attrs, **kwargs):
        tp = super().__new__(cls, name, bases, attrs, **kwargs)
        if name != "Note":
            cls.register_types[tp.nid] = tp
        return tp


class Note(metaclass=NoteMeta):
    def __init__(self, nid: NID, data: bytes):
        self.nid = NID(nid)
        self.data = data

    @classmethod
    def decode(cls, data: bytes) -> Self:
        nid = data[0]
        if nid not in cls.register_types:
            raise ValueError("Invalid nid")
        return cls.register_types[nid](nid, data[1:])


class NidReady(Note):
    nid = NID.READY


class NidFaceState(Note):
    nid = NID.FACE_STATE

    @property
    def state(self) -> FaceState:
        return FaceState(int.from_bytes(self.data[:2], "big"))

    @property
    def left(self):
        return int.from_bytes(self.data[2:4], "big")

    @property
    def top(self):
        return int.from_bytes(self.data[4:6], "big")

    @property
    def right(self):
        return int.from_bytes(self.data[6:8], "big")

    @property
    def bottom(self):
        return int.from_bytes(self.data[8:10], "big")

    @property
    def yaw(self):
        return int.from_bytes(self.data[10:12], "big")

    @property
    def pitch(self):
        return int.from_bytes(self.data[12:14], "big")

    @property
    def roll(self):
        return int.from_bytes(self.data[14:16], "big")


class NidUnknownError(Note):
    nid = NID.UNKNOWNERROR


class NidOTADone(Note):
    nid = NID.OTA_DONE


class NidEyeState(Note):
    nid = NID.EYE_STATE
