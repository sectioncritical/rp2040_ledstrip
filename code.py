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
from busio import UART

import cmdparser

from adafruit_neopxl8 import NeoPxl8
from adafruit_led_animation.color import RED, GREEN, BLUE, WHITE
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.chase import Chase

start_gpio = board.D2
num_strands = 2
pix_per_strand = 144
total_pix = num_strands * pix_per_strand
brightness=1
stride = 144
pulselen = 1


COLORON = (15, 0, 0)
COLOROFF = (0, 0, 0)

pxl8 = NeoPxl8(start_gpio, total_pix, num_strands=num_strands,
               brightness=brightness, auto_write=False)

uart = UART(tx=board.TX, rx=board.RX, baudrate=115200, timeout=0)

# take a string, append CRLF and send to uart
def uart_print(printstr):
    uart.write((printstr+"\r\n").encode("utf-8"))

# animation to turn everything off
def anim_off(cmdargs):
    for idx in range(total_pix):
        pxl8[idx] = COLOROFF
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

def cmd_help(cmdargs):
    uart_print("\nCommands")
    uart_print("--------")
    for key, val in cmd_dict.items():
        uart_print(f"{key:<8}: {val[1]}")
    uart_print("")
    return None

cmd_dict = {
    "help": (cmd_help, "show list of commands"),
    "off": (anim_off, "stop animations"),
    "idle": (anim_idle, "idle mode (0-3)"),
    "rpm": (anim_rpm, "rpm mode (1-100)")
    }

errmsg = bytes("$ERR\n", 'utf-8')
okmsg = bytes("$OK\n", 'utf-8')

active_animation = None

def run_command(cmdargs):
    global active_animation
    uart_print("run_command()" + str(cmdargs))
    if cmdargs[0] in cmd_dict:
        cmdfn = cmd_dict[cmdargs[0]][0]
        active_animation = cmdfn(cmdargs)
        uart.write(okmsg)
    else:
        uart.write(errmsg)

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


uart_print("\nFlashy Starting ...\n")

cp = cmdparser.CmdParser()

while True:
    in_available = uart.in_waiting
    if in_available:
        incoming = uart.read(in_available)
        uart.write(incoming)  # echo back to console
        cmdargs = cp.process_input(incoming)
        if cmdargs:
            run_command(cmdargs)

    run_animation()
