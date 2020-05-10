import struct
import uuid


class BasePacker:
    """
    Abstract base class for packers.

    """

    def pack_pk(self, user_pk):
        """
        Create a short representation of the primary key of a user.

        Return bytes.

        """

    def unpack_pk(self, data):
        """
        Extract the primary key of a user from a signed token.

        Return the primary key and the remaining bytes.

        """


class IntPacker:
    @staticmethod
    def pack_pk(user_pk):
        return struct.pack(str("!i"), user_pk)

    @staticmethod
    def unpack_pk(data):
        return struct.unpack(str("!i"), data[:4])[0], data[4:]


class UUIDPacker:
    @staticmethod
    def pack_pk(user_pk):
        return user_pk.bytes

    @staticmethod
    def unpack_pk(data):
        return uuid.UUID(bytes=data[:16]), data[16:]


PACKERS = {"AutoField": IntPacker, "IntegerField": IntPacker, "UUIDField": UUIDPacker}
