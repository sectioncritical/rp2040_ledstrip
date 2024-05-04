
import array
import cmdif

try:
    import ws2812_pio as wspio
except ImportError:
    from tests import ws2812_test as wspio


ws = wspio.WS2812(0, 16)
pixels = array.array("I", [0 for _ in range(144*3)])
ci = cmdif.CmdInterface(framebuf=pixels)

# this is the execution loop
# can add return/exit conditions here
# this is where display update should be called
# right now delay is handled in command update method but consider
# putting it here instead
# also need to add code to allow for repeated calls to update when a
# pattern command needs to keep running
# consider passing pixels to run
while True:
    ci.run()
    ws.show(pixels)

"""

def range(param_list, config_list):
    global pixels
    dot0 = int(param_list[1])
    numdots = int(param_list[2])
    red = int(param_list[3])
    green = int(param_list[4])
    blue = int(param_list[5])
    color = green << 16
    color += red << 8
    color += blue
    for idx in range(numdots):
        pixels[dot0+idx] = color
    ws.show(pixels)

"""
