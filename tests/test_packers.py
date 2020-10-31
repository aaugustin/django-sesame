import uuid

from django.test import TestCase, override_settings

from sesame import packers
from sesame.packers import (
    BasePacker,
    BytesPacker,
    LongLongPacker,
    LongPacker,
    ShortPacker,
    StrPacker,
    UnsignedLongLongPacker,
    UnsignedLongPacker,
    UnsignedShortPacker,
    UUIDPacker,
)

from .signals import reset_sesame_settings  # noqa


class Packer(BasePacker):
    """
    Verbatim copy of the example in the README.

    """

    @staticmethod
    def pack_pk(user_pk):
        assert len(user_pk) == 24
        return bytes.fromhex(user_pk)

    @staticmethod
    def unpack_pk(data):
        return data[:12].hex(), data[12:]


class RepeatPacker(LongPacker):
    """
    Packer that can raise an exception in unpack_pk.

    """

    @classmethod
    def pack_pk(cls, user_pk):
        data = super().pack_pk(user_pk)
        assert data[:2] == b"\x00\x00"
        return data[2:4] + data[2:]

    @classmethod
    def unpack_pk(cls, data):
        assert data[:2] == data[2:4]
        data = b"\x00\x00" + data[2:]
        return super().unpack_pk(data)


class TestPackers(TestCase):

    random_uuid = uuid.uuid4()
    cases = [
        (ShortPacker, -32768, b"\x80\x00"),
        (ShortPacker, 0, b"\x00\x00"),
        (ShortPacker, 1, b"\x00\x01"),
        (ShortPacker, 32767, b"\x7f\xff"),
        (UnsignedShortPacker, 0, b"\x00\x00"),
        (UnsignedShortPacker, 1, b"\x00\x01"),
        (UnsignedShortPacker, 65535, b"\xff\xff"),
        (LongPacker, -2147483648, b"\x80\x00\x00\x00"),
        (LongPacker, 0, b"\x00\x00\x00\x00"),
        (LongPacker, 1, b"\x00\x00\x00\x01"),
        (LongPacker, 2147483647, b"\x7f\xff\xff\xff"),
        (UnsignedLongPacker, 0, b"\x00\x00\x00\x00"),
        (UnsignedLongPacker, 1, b"\x00\x00\x00\x01"),
        (UnsignedLongPacker, 4294967295, b"\xff\xff\xff\xff"),
        (LongLongPacker, -9223372036854775808, b"\x80" + 7 * b"\x00"),
        (LongLongPacker, 0, 8 * b"\x00"),
        (LongLongPacker, 1, 7 * b"\x00" + b"\x01"),
        (LongLongPacker, 9223372036854775807, b"\x7f" + 7 * b"\xff"),
        (UnsignedLongLongPacker, 0, 8 * b"\x00"),
        (UnsignedLongLongPacker, 1, 7 * b"\x00" + b"\x01"),
        (UnsignedLongLongPacker, 18446744073709551615, 8 * b"\xff"),
        (UUIDPacker, random_uuid, random_uuid.bytes),
        (BytesPacker, b"", b"\x00"),
        (BytesPacker, random_uuid.bytes, b"\x10" + random_uuid.bytes),
        (BytesPacker, 255 * b"\xff", 256 * b"\xff"),
        (StrPacker, "", b"\x00"),
        (StrPacker, "marie-noëlle", b"\x0dmarie-no\xc3\xablle"),
        (StrPacker, 51 * "👍 ", b"\xff" + 51 * b"\xf0\x9f\x91\x8d "),
        (
            Packer,
            "abcdef012345abcdef567890",
            b"\xab\xcd\xef\x01\x23\x45\xab\xcd\xef\x56\x78\x90",
        ),
        (RepeatPacker, 2, b"\x00\x02\x00\x02"),
    ]

    def test_pack_pk(self):
        for Packer, user_pk, data in self.cases:
            with self.subTest(Packer=Packer, user_pk=user_pk):
                self.assertEqual(Packer().pack_pk(user_pk), data)

    def test_unpack_pk(self):
        rest = b"random stuff"
        for Packer, user_pk, data in self.cases:
            with self.subTest(Packer=Packer, user_pk=user_pk):
                self.assertEqual(Packer().unpack_pk(data + rest), (user_pk, rest))

    error_cases = [
        (BytesPacker, 256 * b"\xff"),
        (StrPacker, 64 * "👍"),
    ]

    def test_pack_pk_error(self):
        for Packer, user_pk in self.error_cases:
            with self.subTest(Packer=Packer, user_pk=user_pk):
                with self.assertRaises(ValueError):
                    Packer().pack_pk(user_pk)

    def test_get_packer_with_auto_primary_key(self):
        self.assertEqual(type(packers.packer), LongPacker)

    @override_settings(AUTH_USER_MODEL="tests.UUIDUser")
    def test_get_packer_with_uuid_primary_key(self):
        self.assertEqual(type(packers.packer), UUIDPacker)

    def test_get_packer_with_unsupported_primary_key(self):
        with self.assertRaises(NotImplementedError) as exc:
            with override_settings(AUTH_USER_MODEL="tests.BooleanUser"):
                pass  # pragma: no cover
        self.assertEqual(
            str(exc.exception),
            "BooleanField primary keys aren't supported",
        )

    @override_settings(
        AUTH_USER_MODEL="tests.StrUser",
        SESAME_PACKER="tests.test_packers.Packer",
    )
    def test_get_packer_with_custom_packer(self):
        self.assertEqual(type(packers.packer), Packer)
