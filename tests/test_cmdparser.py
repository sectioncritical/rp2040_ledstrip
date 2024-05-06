#
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

# Unit tests for the cmdparser.py command parser.
#
# To run:
#     python -m unittest -v test_cmdparser.py
#
# I recommend using a venv although this test and cmdparser do not require
# any installed packages.

import unittest

import cmdparser

# most of the logic is test by the other test cases
# this one is just to validate the public facing wrapper method
class TestProcessInput(unittest.TestCase):

    def setUp(self):
        self.cp = cmdparser.CmdParser()
        self.assertTrue(self.cp)

    def test_nominal(self):
        b = "$foo,bar\n"
        result = self.cp.process_input(b)
        self.assertIsInstance(result, list)
        self.assertEqual(2, len(result))
        self.assertEqual("foo", result[0])
        self.assertEqual("bar", result[1])

    def test_pieces(self):
        b = "$fo"
        result = self.cp.process_input(b)
        self.assertIsNone(result)
        b = "o,ba"
        result = self.cp.process_input(b)
        self.assertIsNone(result)
        b = "r\n"
        result = self.cp.process_input(b)
        self.assertIsInstance(result, list)
        self.assertEqual(2, len(result))
        self.assertEqual("foo", result[0])
        self.assertEqual("bar", result[1])

class TestCmdParserGood(unittest.TestCase):

    def setUp(self):
        self.cp = cmdparser.CmdParser()
        self.assertTrue(self.cp)

    def test_2args(self):
        b = "$arg1,arg2\n"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(2, len(result))
        self.assertEqual("arg1", result[0])
        self.assertEqual("arg2", result[1])

    def test_1arg(self):
        b = "$foobar\n"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        self.assertEqual("foobar", result[0])

    def test_3args(self):
        b = "$foo,bar,baz\n"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(3, len(result))
        self.assertEqual("foo", result[0])
        self.assertEqual("bar", result[1])
        self.assertEqual("baz", result[2])

    # a command line with no actual arguments does not return an empty list
    # it returns a list with one item which is an empty string
    def test_0arg(self):
        b = "$\n"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        self.assertEqual("", result[0])

    # change to design made it case sensitive so dont do this test any more
    ##def test_lower_case(self):
    ##    b = "$FOO,bar\n"
    ##    result = self.cp.parse_cmd(b)
    ##    self.assertIsInstance(result, list)
    ##    self.assertEqual(2, len(result))
    ##    self.assertEqual("foo", result[0])
    ##    self.assertEqual("bar", result[1])

class TestCmdParserBad(unittest.TestCase):

    def setUp(self):
        self.cp = cmdparser.CmdParser()
        self.assertTrue(self.cp)

    def test_bad_leading(self):
        b = "foo,bar\n"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(0, len(result))

    def test_bad_trailing(self):
        b = "$foo,bar"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(0, len(result))

    def test_garbage(self):
        b = "ishdk57e9ksjh(*&)(&*alskjs"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(0, len(result))

    def test_bad_delimiter(self):
        b = "$foo.bar\n"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        self.assertEqual("foo.bar", result[0])

    # verify empty parm before comma is okay
    def test_empty_first_parm(self):
        b = "$,bar\n"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(2, len(result))
        self.assertEqual("", result[0])
        self.assertEqual("bar", result[1])

    # verify empty parm after comma is okay
    def test_empty_second_parm(self):
        b = "$foo,\n"
        result = self.cp.parse_cmd(b)
        self.assertIsInstance(result, list)
        self.assertEqual(2, len(result))
        self.assertEqual("foo", result[0])
        self.assertEqual("", result[1])


class TestAssembleCmd(unittest.TestCase):

    def setUp(self):
        self.cp = cmdparser.CmdParser()
        self.assertTrue(self.cp)
        self.assertIsNone(self.cp._buf)

    def test_complete_nominal(self):
        b = "$foo,bar\n"
        result = self.cp.assemble_cmd(b)
        self.assertEqual("$foo,bar\n", result)

    # check that it can handle bytearray as well as bytes
    # this test not strictly needed now since change to strings from bytes
    # but keep anyway - doesnt hurt
    def test_complete_nominal_bytearray(self):
        b = "$foo,bar\n"
        result = self.cp.assemble_cmd(b)
        self.assertEqual("$foo,bar\n", result)

    def test_ignore_trailing(self):
        b = "$foo,bar\n$baz,qux"
        result = self.cp.assemble_cmd(b)
        # verify the input was framed properly
        self.assertEqual("$foo,bar\n", result)
        # verify that more input is processed correctly without the
        # stray bytes from the previous input
        b = "$foo,bar\n"
        result = self.cp.assemble_cmd(b)
        self.assertEqual("$foo,bar\n", result)

    def test_ignore_leading(self):
        b = "qwerty$foo,bar\n"
        result = self.cp.assemble_cmd(b)
        # verify leading bytes are ignored
        # and valid input was framed properly
        self.assertEqual("$foo,bar\n", result)

    # check that an empty input does not cause a problem
    # however, we do not test input of None or non-bytes type because
    # the function does not check for that
    # I assume that the caller will not pass invalid types
    def test_empty_input(self):
        b = ""
        result = self.cp.assemble_cmd(b)
        self.assertIsNone(result)

    # verify correct result when command is passed in more than one piece
    def test_two_pieces(self):
        b = "$foo,"
        result = self.cp.assemble_cmd(b)
        self.assertIsNone(result)
        b = "bar\n"
        result = self.cp.assemble_cmd(b)
        self.assertEqual("$foo,bar\n", result)

    # check that it can be terminated with \r instead of \n
    def test_cr_instead_of_newline(self):
        b = "$foo,bar\r"
        result = self.cp.assemble_cmd(b)
        self.assertEqual("$foo,bar\n", result)

    # verify CRLF terminator does not cause a problem
    def test_crlf(self):
        b = "$foo,bar\r\n"
        result = self.cp.assemble_cmd(b)
        # verify the input was framed properly
        self.assertEqual("$foo,bar\n", result)
        # verify that more input is processed correctly without the
        # stray bytes from the previous input
        b = "$baz,qux\n"
        result = self.cp.assemble_cmd(b)
        self.assertEqual("$baz,qux\n", result)

    # verify LFCR terminator does not cause a problem
    def test_lfcr(self):
        b = "$foo,bar\n\r"
        result = self.cp.assemble_cmd(b)
        # verify the input was framed properly
        self.assertEqual("$foo,bar\n", result)
        # verify that more input is processed correctly without the
        # stray bytes from the previous input
        b = "$baz,qux\n"
        result = self.cp.assemble_cmd(b)
        self.assertEqual("$baz,qux\n", result)

    # detailed check of internals to make sure method works the way we
    # think it does
    # _buf is the only internal state of cp
    def test_internals(self):
        # internal buf should be None
        self.assertIsNone(self.cp._buf)
        # passing in anything prior to $ buf should remain None
        b = "plugh"
        result = self.cp.assemble_cmd(b)
        self.assertIsNone(result)
        self.assertIsNone(self.cp._buf)
        b = "plover"
        result = self.cp.assemble_cmd(b)
        self.assertIsNone(result)
        self.assertIsNone(self.cp._buf)
        # passing in CR or LF does nothing
        b = "\r"
        result = self.cp.assemble_cmd(b)
        self.assertIsNone(result)
        self.assertIsNone(self.cp._buf)
        b = "\n"
        result = self.cp.assemble_cmd(b)
        self.assertIsNone(result)
        self.assertIsNone(self.cp._buf)
        # starting with $ inits the buffer
        b = "$"
        result = self.cp.assemble_cmd(b)
        self.assertIsNone(result)
        self.assertEqual("$", self.cp._buf)
        # adding stuff adds to the buffer
        b = "foo,b"
        result = self.cp.assemble_cmd(b)
        self.assertIsNone(result)
        self.assertEqual("$foo,b", self.cp._buf)
        # add a little more
        b = "ar"
        result = self.cp.assemble_cmd(b)
        self.assertIsNone(result)
        self.assertEqual("$foo,bar", self.cp._buf)
        # adding that last \n returns result and resets buffer
        b = "\n"
        result = self.cp.assemble_cmd(b)
        self.assertEqual("$foo,bar\n", result)
        self.assertIsNone(self.cp._buf)


if __name__ == "__main__":
    unittest.main()
