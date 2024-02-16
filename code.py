#!/usr/bin/env python3
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

import board
import usb_cdc
#from busio import UART

import cmdparser

from adafruit_neopxl8 import NeoPxl8
from adafruit_led_animation.color import RED, GREEN, BLUE, WHITE, BLACK
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.blink import Blink

start_gpio = board.NEOPIXEL0
num_strands = 1
pix_per_strand = 3*144
total_pix = num_strands * pix_per_strand
brightness=1
#stride = 144


pxl8 = NeoPxl8(start_gpio, total_pix, num_strands=num_strands,
               brightness=brightness, auto_write=False)

#uart = UART(tx=board.TX, rx=board.RX, baudrate=115200, timeout=0)

# from input string, write to serial comm channel appending CRLF
def ser_write(printstr):
    # uart.write((printstr+"\r\n").encode("utf-8"))
    usb_cdc.data.write(bytes(printstr, "ascii"))

# write a line to serial console with CRLF termination
def ser_writeln(printstr):
    ser_write(printstr)
    ser_write("\r\n")

# return characters from serial comm channel or None
def ser_read():
    available = usb_cdc.data.in_waiting
    if available:
        input = usb_cdc.data.read(available)
        return input.decode("ascii")
    return None

# animation to turn everything off
def anim_off(cmdargs):
    for idx in range(total_pix):
        pxl8[idx] = BLACK
    pxl8.show()
    return None

def anim_idle(cmdargs):
    if len(cmdargs) == 2:
        # TODO come up with uniform way to handle errors like this
        try:
            level = int(cmdargs[1])
        except ValueError:
            level = 0
        if level == 0:
            solid = Solid(pxl8, color=(0, 0, 8))
            return solid
        elif level == 1:
            pulse = Pulse(pxl8, speed=0.01, color=(0,8,15), period=5)
            return pulse
        elif level == 2:
            pulse = Pulse(pxl8, speed=0.01, color=(8,0,15), period=3)
            return pulse
        elif level == 3:
            pulse = Pulse(pxl8, speed=0.01, color=(8,8,15), period=1)
            return pulse
    return None

def anim_rpm(cmdargs):
    try:
        level = int(cmdargs[1])
    except ValueError:
        level = 0
    if level == 0:
        speed = 1
    else:
        speed = 1 / level
    chase = Chase(pxl8, speed=speed, color=(8,0,0), size=10, spacing=20)
    return chase

def anim_brake(cmdargs):
    if len(cmdargs) == 2:
        try:
            level = int(cmdargs[1])
        except ValueError:
            level = 0
        if level == 0:
            solid = Solid(pxl8, color=(15, 0, 0))
            return solid
        elif level == 1:
            blink = Blink(pxl8, speed=0.1, color=(15, 0, 0))
            return blink
    return None

def anim_reverse(cmdargs):
    if len(cmdargs) == 2:
        try:
            level = int(cmdargs[1])
        except ValueError:
            level = 0
        if level == 0:
            solid = Solid(pxl8, color=(15, 15, 15))
            return solid
        elif level == 1:
            blink = Blink(pxl8, speed=0.5, color=(15, 15, 15))
            return blink
    return None

def anim_turn(cmdargs):
    return anim_off(cmdargs)

def cmd_help(cmdargs):
    ser_writeln("\nCommands")
    ser_writeln("--------")
    for key, val in cmd_dict.items():
        ser_writeln(f"{key:<8}: {val[1]}")
    ser_writeln("")
    return None

cmd_dict = {
    "help": (cmd_help, "show list of commands"),
    "off": (anim_off, "stop animations"),
    "idle": (anim_idle, "idle mode (pulse rate 0-3)"),
    "rpm": (anim_rpm, "rpm mode (rate 1-100)"),
    "brake": (anim_brake, "brake (0-solid, 1-flash)"),
    "reverse": (anim_reverse, "reverse lights (0-solid, 1-blink)"),
    "turn": (anim_turn, "turn signal")
    }

errmsg = "$ERR"
okmsg = "$OK"

active_animation = None

def run_command(cmdargs):
    global active_animation
    ser_writeln("run_command()" + str(cmdargs))
    if cmdargs[0] in cmd_dict:
        cmdfn = cmd_dict[cmdargs[0]][0]
        active_animation = cmdfn(cmdargs)
        ser_writeln(okmsg)
    else:
        ser_writeln(errmsg)

def run_animation():
    if active_animation:
        active_animation.animate()

# command format
# ascii string
# $cmdname,val\n
# command starts with '$'
# followed by command name as a string, such as IDLE, RPM, etc
# commands are case insensitive
# command name is followed by a comma, no spaces
# comma is followed by integer as string, no spaces
# if the command does not need a value, then use 0
# the command is terminated by a newline '\n'
# if any return chars appear '\r' they are discarded


ser_writeln("\nFlashy Starting ...\n")

cp = cmdparser.CmdParser()

while True:
    incoming = ser_read()
    if incoming:
        ser_write(incoming)  # echo back to console
        cmdargs = cp.process_input(incoming)
        if cmdargs:
            run_command(cmdargs)

    run_animation()
