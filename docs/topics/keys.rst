Custom primary keys
-------------------

When generating a token for a user, django-sesame stores the primary key of
that user in the token. In order to keep tokens short, django-sesame creates
compact binary representations of primary keys, according to their type.

If you're using integer or UUID primary keys, you're fine. If you're using
another type of primary key, for example a string created by a unique ID
generation algorithm, the default representation may be suboptimal.

For example, let's say primary keys are strings containing 24 hexadecimal
characters. The default packer represents them with 25 bytes. You can reduce
them to 12 bytes with this custom packer:

.. code-block:: python

    from sesame.packers import BasePacker

    class Packer(BasePacker):

        @staticmethod
        def pack_pk(user_pk):
            assert len(user_pk) == 24
            return bytes.fromhex(user_pk)

        @staticmethod
        def unpack_pk(data):
            return data[:12].hex(), data[12:]

Then, set the :data:`SESAME_PACKER` setting to the dotted Python path to your
custom packer class.

For details, see :class:`~sesame.packers.BasePacker` and look at built-in
packers defined in the ``sesame.packers`` module.
