# -*- coding: utf-8 -*-
import functools
import operator
from dataclasses import dataclass
from enum import IntEnum


class Command(IntEnum):
    RESET = 0x10
    GET_STATUS = 0x11
    VERIFY = 0x12
    ENROLL = 0x13
    ENROLL_SINGLE = 0x1D
    DELETE_USER = 0x20
    DELETE_ALL = 0x21
    GET_USER_INFO = 0x22
    FACE_RESET = 0x23
    MID_GET_ALL_USERID = 0x24
    MID_ENROLL_ITG = 0x26
    GET_VERSION = 0x30
    INIT_ENCRYPTIO = 0x50
    MID_SET_RELEASE_ENC_KEY = 0x52
    MID_SET_DEBUG_ENC_KEY = 0x53
    MID_GET_SN = 0x93
    READ_USB_UVC_PARAMETERS = 0xB0
    SET_USB_UVC_PARAMETERS = 0xB1
    MID_UPGRADE_FW = 0xF6
    MID_ENROLL_WITH_PHOTO = 0xF7
    DEMO_MODE = 0xFE


class MsgId(IntEnum):
    MID_RESET = 0x10  # todo


class FaceDir(IntEnum):
    UP = 0x10
    DOWN = 0x08
    LEFT = 0x04
    RIGHT = 0x02
    MIDDLE = 0x01  # 录入正向的人脸
    UNDEFINE = 0x00  # 未定义，默认为正向


def calculate_checksum(data: bytes) -> int:
    return functools.reduce(operator.xor, data[2:])


SYNC_WORD = b"\xef\xaa"


@dataclass
class Event:
    @classmethod
    def decode(cls, raw: bytes) -> "Event":
        if raw[:2] != SYNC_WORD:
            raise ValueError("Invalid sync word")
        pass


class Request:
    def encode(self) -> bytes:
        data = (
            SYNC_WORD
            + self.command.to_bytes(1, "big")
            + self.size.to_bytes(2, "big")
            + self.data
        )
        checksum = calculate_checksum(data)
        return data + checksum.to_bytes(1, "big")

    @property
    def size(self):
        return len(self.data)


class ResponseMeta(type):
    register_types = {}

    def __new__(cls, name, bases, attrs, **kwargs):
        tp = super().__new__(cls, name, bases, attrs, **kwargs)
        if name != "Response":
            cls.register_types[tp.msg_id] = tp
        return tp


class Response(metaclass=ResponseMeta):
    @classmethod
    def decode(cls, mid: int, data: bytes) -> "Response":
        return cls.register_types[mid].from_bytes(data)


class MidReset(Response):
    msg_id = MsgId.MID_RESET
    size = 0
    data = b""

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls()


class Reset(Request):
    command = Command.RESET
    size = 0
    data = b""


class GetStatus(Request):
    command = Command.GET_STATUS
    size = 0
    data = b""


class Verify(Request):
    command = Command.VERIFY

    def __init__(self, pd_rightaway: bool, timeout: int):
        """

        :param pd_rightaway: 解锁成功后是否立刻断电(yes:1  no:0
        :param timeout: 解锁超时时间（单位s）
        """
        self.pd_rightaway = pd_rightaway
        self.timeout = timeout
        self.data = int(pd_rightaway).to_bytes(1, "big") + timeout.to_bytes(1, "big")


class Enroll(Request):
    command = Command.ENROLL

    def __init__(self, admin: bool, user_name: str, face_dir: FaceDir, timeout: int):
        """

        :param admin: 是否设置为管理员(yes:1 no:0)
        :param user_name: 录入用户姓名
        :param face_dir: 用户需要录入的方向 具体参数下表“人脸方向定义”所示
        :param timeout: 录入超时时间（单位s）
        """
        self.admin = admin
        if len(user_name) > 32:
            raise ValueError("User name too long")
        self.user_name = user_name
        self.face_dir = face_dir
        self.timeout = timeout
        self.data = (
            int(admin).to_bytes(1, "big")
            + user_name.encode("utf-8")
            + face_dir.to_bytes(1, "big")
            + timeout.to_bytes(1, "big")
        )


class EnrollSingle(Request):
    command = Command.ENROLL_SINGLE

    def __init__(self, admin: bool, user_name: str, face_dir: FaceDir, timeout: int):
        """

        :param admin: 是否设置为管理员(yes:1 no:0)
        :param user_name: 录入用户姓名
        :param face_dir: 不使用
        :param timeout: 录入超时时间（单位s）
        """
        self.admin = admin
        if len(user_name) > 32:
            raise ValueError("User name too long")
        self.user_name = user_name
        self.face_dir = face_dir
        self.timeout = timeout
        self.data = (
            int(admin).to_bytes(1, "big")
            + user_name.encode("utf-8")
            + face_dir.to_bytes(1, "big")
            + timeout.to_bytes(1, "big")
        )


class DeleteUser(Request):
    command = Command.DELETE_USER

    def __init__(self, user_id: int):
        """

        :param user_id: 用户ID
        """
        self.user_id = user_id
        self.data = user_id.to_bytes(2, "big")


class DeleteAll(Request):
    command = Command.DELETE_ALL
    size = 0
    data = b""


class GetUserInfo(Request):
    command = Command.GET_USER_INFO

    def __init__(self, user_id: int):
        """

        :param user_id: 用户ID
        """
        self.user_id = user_id
        self.data = user_id.to_bytes(2, "big")


class FaceReset(Request):
    """
    清除录入状态
    """

    command = Command.FACE_RESET
    size = 0
    data = b""


class MidGetAllUserid(Request):
    """
    获取所有已注册用户 数量和ID
    """

    command = Command.MID_GET_ALL_USERID
    size = 0
    data = b""


class MidEnrollITG(Request):
    command = Command.MID_ENROLL_ITG

    def __init__(
        self,
        admin: bool,
        user_name: str,
        face_dir: FaceDir,
        enroll_type: bool,
        enable_duplicate: bool,
        timeout: int,
    ):
        """

        :param admin: 是否设置为管理员(yes:1 no:0)
        :param user_name: 录入用户姓名
        :param face_dir: 不使用
        :param enroll_type: 注册类型：交互录入或单帧录入
        :param enable_duplicate: 0
        :param timeout: 录入超时时间（单位s）
        """
        self.admin = admin
        if len(user_name) > 32:
            raise ValueError("User name too long")
        self.user_name = user_name
        self.face_dir = face_dir
        self.enroll_type = enroll_type
        self.enable_duplicate = enable_duplicate
        self.timeout = timeout
        self.data = (
            int(admin).to_bytes(1, "big")
            + user_name.encode("utf-8")
            + face_dir.to_bytes(1, "big")
            + int(enroll_type).to_bytes(1, "big")
            + int(enable_duplicate).to_bytes(1, "big")
            + timeout.to_bytes(1, "big")
            + b"\0\0\0"
        )


class GetVersion(Request):
    command = Command.GET_VERSION
    size = 0
    data = b""


class InitEncryptIO(Request):
    command = Command.INIT_ENCRYPTIO

    def __init__(self, seed: int):
        """

        :param seed: 随机种子
        """
        self.data = seed.to_bytes(4, "big")


class MidSetReleaseEncKey(Request):
    command = Command.MID_SET_RELEASE_ENC_KEY

    def __init__(self, enc_key_number: bytes):
        """

        :param enc_key_number: 加密序列
        """
        self.data = enc_key_number
