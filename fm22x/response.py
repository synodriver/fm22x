# -*- coding: utf-8 -*-
from enum import IntEnum
from typing import Self, Literal


class MID(IntEnum):
    MID_RESET = 0x10
    MID_GETSTATUS = 0x11
    MID_VERIFY = 0x12
    MID_ENROLL = 0x13
    MID_ENROLL_SINGLE = 0x1D
    MID_DELUSER = 0x20
    MID_DELALL = 0x21
    MID_GETUSERINFO = 0x22
    MID_FACERESET = 0x23
    MID_GET_ALL_USERID = 0x24
    MID_ENROLL_ITG = 0x26
    MID_GET_VERSION = 0x30
    MID_INIT_ENCRYPTION = 0x50
    MID_SET_RELEASE_ENC_KEY = 0x52
    MID_SET_DEBUG_ENC_KEY = 0x53
    MID_GET_SN = 0x93
    READ_USB_UVC_PARAMETERS = 0xB0
    SET_USB_UVC_PARAMETERS = 0xB1
    MID_UPGRADE_FW = 0xF6
    MID_ENROLL_WITH_PHOTO = 0xF7
    MID_DEMOMODE = 0xFE


class ResponseMeta(type):
    register_types = {}

    def __new__(cls, name, bases, attrs, **kwargs):
        tp = super().__new__(cls, name, bases, attrs, **kwargs)
        if name != "Response":
            cls.register_types[tp.mid] = tp
        return tp


class MsgResultCode(IntEnum):
    SUCCESS = 0
    MR_REJECTED = 1  # module rejected this command
    ABORTED = 2  # algo aborted
    FAILED4_CAMERA = 4  # camera open failed
    FAILED4_UNKNOWNREASON = 5  # UNKNOWN_ERROR
    FAILED4_INVALIDPARAM = 6  # invalid param
    FAILED4_NOMEMORY = 7  # no enough memory
    FAILED4_UNKNOWNUSER = 8  # exceed limitation
    FAILED4_MAXUSER = 9  # exceed maximum user number
    FAILED4_FACEENROLLED = 10  # this face has been enrolled
    FAILED4_LIVENESSCHECK = 12  # liveness check failed
    FAILED4_TIMEOUT = 13  # exceed the time limit
    FAILED4_AUTHORIZATION = 14  # authorization failed
    FAILED4_READ_FILE = 19  # read file failed
    FAILED4_WRITE_FILE = 20  # write file failed
    FAILED4_NO_ENCRYPT = 21  # encrypt must be set
    FAILED4_NO_RGBIMAGE = 23  # rgb image is not read
    FAILED4_JPGPHOTO_LARGE = 24
    FAILED4_JPGPHOTO_SMALL = 25


class Response(metaclass=ResponseMeta):
    def __init__(self, mid: int, result: MsgResultCode, data: bytes):
        self.mid = mid
        self.result = result
        self.data = data

    @classmethod
    def decode(cls, data: bytes) -> Self:
        mid = data[0]
        if mid not in cls.register_types:
            raise ValueError("Invalid mid")
        result = data[1]
        data = data[2:]
        return cls.register_types[mid](mid, result, data)


class MidReset(Response):
    mid = MID.MID_RESET


class Status(IntEnum):
    IDLE = 0
    BUSY = 1
    ERROR = 2
    INVALID = 3


class MidGetStatus(Response):
    mid = MID.MID_GETSTATUS

    @property
    def status(self) -> Status:
        return Status(self.data[0])


class MidVerify(Response):
    mid = MID.MID_VERIFY

    @property
    def user_id(self):
        if self.result == MsgResultCode.SUCCESS:
            return int.from_bytes(self.data[:2], "big")

    @property
    def user_name(self):
        if self.result == MsgResultCode.SUCCESS:
            return self.data[2:-2].decode("utf-8")

    @property
    def admin(self):
        """
        is admin
        :return:
        """
        if self.result == MsgResultCode.SUCCESS:
            return bool(self.data[-2])

    @property
    def unlock_status(self):
        if self.result == MsgResultCode.SUCCESS:
            return self.data[-1]


class MidEnroll(Response):
    mid = MID.MID_ENROLL

    @property
    def user_id(self):
        if self.result == MsgResultCode.SUCCESS:
            return int.from_bytes(self.data[:2], "big")

    @property
    def face_direction(self):
        """
        各个方向人脸的录入状态
        :return:
        """
        if self.result == MsgResultCode.SUCCESS:
            return self.data[2]


class MidEnrollSingle(Response):
    mid = MID.MID_ENROLL_SINGLE

    @property
    def user_id(self):
        if self.result == MsgResultCode.SUCCESS:
            return int.from_bytes(self.data[:2], "big")

    @property
    def face_direction(self):
        """
        01（表示正脸录入）
        :return:
        """
        if self.result == MsgResultCode.SUCCESS:
            return self.data[2]


class MidDelUser(Response):
    mid = MID.MID_DELUSER


class MidDelAll(Response):
    mid = MID.MID_DELALL


class MidGetUserInfo(Response):
    mid = MID.MID_GETUSERINFO

    @property
    def user_id(self):
        if self.result == MsgResultCode.SUCCESS:
            return int.from_bytes(self.data[:2], "big")

    @property
    def user_name(self):
        if self.result == MsgResultCode.SUCCESS:
            return self.data[2:-1].decode("utf-8")

    @property
    def admin(self):
        """
        is admin
        :return:
        """
        if self.result == MsgResultCode.SUCCESS:
            return bool(self.data[-1])


class MidFaceReset(Response):
    mid = MID.MID_FACERESET


class MidGetAllUserID(Response):
    mid = MID.MID_GET_ALL_USERID

    @property
    def user_counts(self):
        """
        已注册用户数量
        :return:
        """
        if self.result == MsgResultCode.SUCCESS:
            return self.data[0]

    @property
    def user_id(self) -> list:
        """
        所有已注册用户ID，使用连续两个字节存储一个ID，先存高八位
        :return:
        """
        if self.result == MsgResultCode.SUCCESS:
            return [
                int.from_bytes(self.data[i : i + 2], "big")
                for i in range(1, len(self.data), 2)
            ]


class MidEnrollITG(Response):
    mid = MID.MID_ENROLL_ITG

    @property
    def user_id(self):
        if self.result == MsgResultCode.SUCCESS:
            return int.from_bytes(self.data[:2], "big")


class MidGetVersion(Response):
    mid = MID.MID_GET_VERSION

    @property
    def version(self):
        if self.result == MsgResultCode.SUCCESS:
            return self.data.decode("utf-8")


class MidInitEncryption(Response):
    mid = MID.MID_INIT_ENCRYPTION

    @property
    def device_id(self):
        return self.data


class MidSetReleaseEncKey(Response):
    mid = MID.MID_SET_RELEASE_ENC_KEY


class MidSetDebugEncKey(Response):
    mid = MID.MID_SET_DEBUG_ENC_KEY


class MidGetSN(Response):
    mid = MID.MID_GET_SN

    @property
    def device_sn(self):
        """
        设备唯一序列号信息，前8字节有效
        :return:
        """
        return self.data[:8].decode("utf-8")


class ReadUSBUvcParameters(Response):
    mid = MID.READ_USB_UVC_PARAMETERS

    @property
    def usb_type(self) -> Literal["1.1", "2.0"]:
        if self.data[0] == 0x11:
            return "1.1"
        elif self.data[0] == 0x20:
            return "2.0"

    @property
    def rotate(self) -> bool:
        """

        :return: True则旋转180度
        """
        if self.data[1] & 0x01:
            return True
        return False

    @property
    def flip(self):
        """

        :return: True则镜像翻转
        """
        if self.data[1] & 0x02:
            return True
        return False

    @property
    def quality(self) -> int:
        """
        图像质量 10-99
        :return:
        """
        return self.data[2]


class SetUSBUvcParameters(Response):
    """
    Usb 传图参数设置结果
    """

    mid = MID.SET_USB_UVC_PARAMETERS


class MidUpgradeFW(Response):
    mid = MID.MID_UPGRADE_FW

    @property
    def progress(self):
        """
        升级进度百分比
        :return:
        """
        return self.data[0]


class MidEnrollWithPhoto(Response):
    mid = MID.MID_ENROLL_WITH_PHOTO

    @property
    def seq(self):
        """
        包序号
        :return:
        """
        return int.from_bytes(self.data[:2], "big")


class MidDemoMode(Response):
    mid = MID.MID_DEMOMODE
