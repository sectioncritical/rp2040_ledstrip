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

# Unit tests for the cmdif.py command interface.
#
# To run:
#     python -m unittest -v test_cmdif.py
#
# I recommend using a venv although this test and cmdif do not require
# any installed packages.

import unittest

import cmdif

saved_param_list = None
saved_config_list = None
call_count = 0

def test_cmd(param_list, config_list):
    global saved_param_list
    global saved_config_list
    global call_count
    saved_param_list = param_list
    saved_config_list = config_list
    call_count += 1


class TestAddCmd(unittest.TestCase):

    def setUp(self):
        global saved_param_list
        global saved_config_list
        global call_count
        saved_param_list = None
        saved_config_list = None
        call_count = 0
        self.ci = cmdif.CmdInterface()
        self.assertTrue(self.ci)

    def test_initial(self):
        self.assertEqual(1, len(self.ci._cmds))
        self.assertTrue("help" in self.ci._cmds)

    def test_add(self):
        cfg = [1, 2, 3]
        self.ci.add_cmd("test", test_cmd, "help for test command", cfg)
        self.assertEqual(2, len(self.ci._cmds))
        self.assertTrue("test" in self.ci._cmds)
        cmdentry = self.ci._cmds["test"]
        self.assertEqual("help for test command", cmdentry[1])
        self.assertEqual(test_cmd, cmdentry[0])
        self.assertEqual(cfg, cmdentry[2])

    def test_exec(self):
        cfg = [4,5,6]
        self.ci.add_cmd("test", test_cmd, "help for test command", cfg)
        self.assertEqual(0, call_count)
        prm = ["test", "foo", 1]
        self.ci.exec(prm)
        self.assertEqual(1, call_count)
        self.assertIsNotNone(saved_param_list)
        self.assertIsNotNone(saved_config_list)
        self.assertEqual(prm, saved_param_list)
        self.assertEqual([4, 5, 6], saved_config_list)
