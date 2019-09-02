from machine import Pin, ADC
from neopixel import NeoPixel
import time
import ujson
import blynklib
import gc

gc.collect()

# a 256 step 2.0 gamma table
gamma_table = [
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3,
3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11,
11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20,
21, 21, 22, 23, 23, 24, 24, 25, 26, 26, 27, 28, 28, 29, 30, 30, 31, 32, 32, 33,
34, 35, 35, 36, 37, 38, 38, 39, 40, 41, 42, 42, 43, 44, 45, 46, 47, 47, 48, 49,
50, 51, 52, 53, 54, 55, 56, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
69, 70, 71, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, 91,
92, 93, 94, 95, 97, 98, 99, 100, 102, 103, 104, 105, 107, 108, 109, 111, 112,
113, 115, 116, 117, 119, 120, 121, 123, 124, 126, 127, 128, 130, 131, 133, 134,
136, 137, 139, 140, 142, 143, 145, 146, 148, 149, 151, 152, 154, 155, 157, 158,
160, 162, 163, 165, 166, 168, 170, 171, 173, 175, 176, 178, 180, 181, 183, 185,
186, 188, 190, 192, 193, 195, 197, 199, 200, 202, 204, 206, 207, 209, 211, 213,
215, 217, 218, 220, 222, 224, 226, 228, 230, 232, 233, 235, 237, 239, 241, 243,
245, 247, 249, 251, 253, 255 ]

seven_seg = [
    [ True,  True,  True,  False, True,  True,  True  ], # 0
    [ False, False, True,  False, False, False, True  ], # 1
    [ False, True,  True,  True,  True,  True,  False ], # 2
    [ False, True,  True,  True,  False, True,  True  ], # 3
    [ True,  False, True,  True,  False, False, True  ], # 4
    [ True,  True,  False, True,  False, True,  True  ], # 5
    [ True,  True,  False, True,  True,  True,  True  ], # 6
    [ False, True,  True,  False, False, False, True  ], # 7
    [ True,  True,  True,  True,  True,  True,  True  ], # 8
    [ True,  True,  True,  True,  False, True,  True  ]  # 9
]

def hsv_to_rgb(h, s, v):
    if s == 0.0: v*=255; return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

def update_digit(leds, index, value, color_rgb):
    for seg in range(0,7):
        if (seven_seg[value][seg]):
            leds[index*7+seg] = (int(color_rgb[1]*255),int(color_rgb[0]*255),int(color_rgb[2]*255))
        else:
            leds[index*7+seg] = (0,0,0)

pin = Pin(5, Pin.OUT)
np = NeoPixel(pin, 28);

np.fill((0,0,0,0))
np.write()

adc = ADC(0)

f = open('config.json')
config = ujson.load(f)
f.close()

if "blynk_server" in config and "blynk_port" in config:
    blynk = blynklib.Blynk(config["blynk_key"],server=config["blynk_server"],port=int(config["blynk_port"]),log=print)
else:
    blynk = blynklib.Blynk(config["blynk_key"],log=print)

@blynk.handle_event("connect")
def connect_handler():
    blynk.internal("rtc","sync")
    print("sent rtc sync request to blynk server")

@blynk.handle_event("internal_rtc")
def rtc_event(rtc_data_list):
    print("recieved rtc data from blink server")
    print(str(rtc_data_list[0]))
    now = time.localtime(int(rtc_data_list[0]))
    print(str(now))

@blynk.handle_event("write V3")
def hue_event(pin,value):
    print("V{} Value:'{}'".format(str(pin),str(value)))

while True:
    blynk.run()
