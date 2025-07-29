# SPDX-License-Identifier: 0BSD
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

# This test is meant to be run under micropython and exercises the
# ledstrip.LedStrip module. It might work with regular python unittest
# but i have not tried that.

import unittest
import asyncio

from ledstrip import ledstrip
from cmdtemplate import CommandTemplate

class FakeCmd(CommandTemplate):

    pass
    # self._stoprequest defined in super

class TestLedStrip(unittest.TestCase):

    def setUp(self):
        # create some clients
        self.fake1 = FakeCmd()
        self.fake2 = FakeCmd()
        # create an instance of ledstrip
        self.strip = ledstrip.LedStrip(2, 16, 100)
        # verify creating parameters
        self.assertEqual(len(self.strip._buf), 300)
        self.assertFalse(self.strip._lock.locked())
        self.assertFalse(self.fake1._stoprequest)
        self.assertFalse(self.fake2._stoprequest)

    # verify acquiring a lock
    async def async_test_acquire(self):
        # acquire the lock and verify
        await self.strip.acquire(self.fake1)
        self.assertEqual(self.strip._user, self.fake1)
        self.assertTrue(self.strip._lock.locked())
        self.assertFalse(self.fake1._stoprequest)

    def test_acquire(self):
        asyncio.run(self.async_test_acquire())

    # verify releasing a lock
    async def async_test_release(self):
        # acquire the lock, dont need to re-verify
        await self.strip.acquire(self.fake1)
        # release it and verify
        self.strip.release()
        self.assertFalse(self.strip._lock.locked())
        self.assertIsNone(self.strip._user)
        self.assertFalse(self.fake1._stoprequest)

    def test_release(self):
        asyncio.run(self.async_test_release())

    async def async_test_acquire_twice(self):
        # initial acquire as before
        await self.strip.acquire(self.fake1)
        self.assertEqual(self.strip._user, self.fake1)
        self.assertTrue(self.strip._lock.locked())
        self.assertFalse(self.fake1._stoprequest)
        # try another acquire
        # this one should not get the lock
        await self.strip.acquire(self.fake2)
        # fake1 still has the lock
        self.assertTrue(self.fake1._stoprequest)
        self.assertEqual(self.strip._user, self.fake1)
        self.assertTrue(self.strip._lock.locked())
        # releasing now should allow fake2 to gain access
        self.strip.release()
        self.assertTrue(self.strip._lock.locked())
        self.assertEqual(self.strip._user, fake2)
        self.assertFalse(self.fake2._stoprequest)
        # release again should stop fake2 and release the lock
        self.strip.release()
        self.assertFalse(self.strip._lock.locked())
        self.assertIsNone(self.strip._user)
        self.assertTrue(self.fake2._stoprequest)

    def test_acquire_twice(self):
        asyncio.run(self.async_test_acquire_twice())


if __name__ == "__main__":
    unittest.main()
