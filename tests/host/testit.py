import serial

ser = serial.Serial('/dev/cu.usbmodem1424201', 115200)


def sendit(cmd):
    print("\nsending:", cmd)
    ser.write(bytes(cmd, 'ascii'))
    while True:
        ack = ser.read(1)
        print(ack, end="")
        if ack == b'K':
            return


count = 0

colors = ["15,0,0", "0,15,0", "0,0,15"]
coloridx = 0

for pix in range(0, 400, 10):
    color = colors[coloridx]
    coloridx = (coloridx + 1) % 3
    cmd = f"$range,{pix},10,{color}\n"
    sendit(cmd)

while True:
    print(count)
    for color in ["15,0,0", "0,15,0", "0,0,15"]:
        cmd = f"$range,4,4,{color}\n"
        sendit(cmd)
    count += 1

