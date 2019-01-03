from __future__ import unicode_literals

import logging
import struct
import uuid

logger = logging.getLogger('sesame')


class IntPkPacker(object):
    """
    Tool to pack user id stock Django user model, that uses int as pk.

    """
    PACKED_SIZE = 4

    def pack(self, user_pk):
        return struct.pack(str('!i'), user_pk)

    def parse(self, packed_pk):
        return struct.unpack(str('!i'), packed_pk)[0]


class UuidPkPacker(object):
    """
    Tool to pack user id from custom user model, that uses UUID as pk.

    """
    PACKED_SIZE = 16

    def pack(self, user_pk):
        return user_pk.bytes

    def parse(self, packed_pk):
        return uuid.UUID(bytes=packed_pk)
