import subprocess
import hid
import sys
import time


PROFILE_DEFAULT = 1
RATE_DEFAULT = 40

vendor_id = 0x258a  
product_id = 0x2022  

suported_mice = ["glorious model o wireless"]
output = subprocess.check_output(["lsusb"]).decode()


def check_for_supported_mice():
    for device in output.split("\n"):  
        if any(mouse in device.lower() for mouse in suported_mice):
            print("Found supported mouse!")
            return device

class Color:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

class Effect:
    class Glorious:
        def __init__(self, rate):
            self.rate = rate

    class Cycle:
        def __init__(self, rate):
            self.rate = rate

    class Pulse:
        def __init__(self, rate, colors):
            self.rate = rate
            self.colors = colors

    class Solid:
        def __init__(self, color):
            self.color = color

    class PulseOne:
        def __init__(self, rate, color):
            self.rate = rate
            self.color = color

    class Tail:
        def __init__(self, rate):
            self.rate = rate

    class Rave:
        def __init__(self, rate, colors):
            self.rate = rate
            self.colors = colors

    class Wave:
        def __init__(self, rate):
            self.rate = rate

    class Off:
        pass

def set_rgb(profile=None, effect=None):
    device = hid.Device(vendor_id, product_id)

    bfr = [0] * 65
    profile_id = profile if profile is not None else PROFILE_DEFAULT

    bfr[3] = 0x02
    bfr[5] = 0x02
    bfr[7] = profile_id
    bfr[8] = 0xFF

    if isinstance(effect, Effect.Glorious):
        bfr[4] = 0x05
        bfr[9] = 0x01
        bfr[11] = rate_check(effect.rate, 1)

    elif isinstance(effect, Effect.Cycle):
        bfr[4] = 0x05
        bfr[9] = 0x02
        bfr[11] = rate_check(effect.rate, 2)
        bfr[12] = 0xFF

    elif isinstance(effect, Effect.Pulse):
        bfr[4] = len(effect.colors) * 3 + 5
        bfr[9] = 0x03
        bfr[11] = rate_check(effect.rate, 3)

        for i in range(6):
            if i >= len(effect.colors):
                bfr[12 + 3 * i] = 0x00
                bfr[12 + 3 * i + 1] = 0x00
                bfr[12 + 3 * i + 2] = 0x00
            else:
                bfr[12 + 3 * i] = effect.colors[i].red
                bfr[12 + 3 * i + 1] = effect.colors[i].green
                bfr[12 + 3 * i + 2] = effect.colors[i].blue

    elif isinstance(effect, Effect.Solid):
        bfr[4] = 0x08
        bfr[9] = 0x04
        bfr[12] = effect.color.red
        bfr[13] = effect.color.green
        bfr[14] = effect.color.blue

    elif isinstance(effect, Effect.PulseOne):
        bfr[4] = 0x08
        bfr[9] = 0x05
        bfr[11] = rate_check(effect.rate, 5)
        bfr[12] = effect.color.red
        bfr[13] = effect.color.green
        bfr[14] = effect.color.blue

    elif isinstance(effect, Effect.Tail):
        bfr[4] = 0x05
        bfr[9] = 0x06
        bfr[11] = rate_check(effect.rate, 6)

    elif isinstance(effect, Effect.Rave):
        bfr[4] = len(effect.colors) * 3 + 5
        bfr[9] = 0x07
        bfr[11] = rate_check(effect.rate, 7)

        for i in range(2):
            if i >= len(effect.colors):
                bfr[12 + 3 * i] = 0x00
                bfr[12 + 3 * i + 1] = 0x00
                bfr[12 + 3 * i + 2] = 0x00
            else:
                bfr[12 + 3 * i] = effect.colors[i].red
                bfr[12 + 3 * i + 1] = effect.colors[i].green
                bfr[12 + 3 * i + 2] = effect.colors[i].blue

    elif isinstance(effect, Effect.Wave):
        bfr[4] = 0x05
        bfr[9] = 0x08
        bfr[11] = rate_check(effect.rate, 8)

    elif isinstance(effect, Effect.Off):
        bfr[4] = 0x05
        bfr[9] = 0x00

    device.send_feature_report(bytes(bfr))
    device.close()

def rate_check(rate, effect_id):
    rate_unwrapped = rate if rate is not None else RATE_DEFAULT
    if rate_unwrapped < 0 or rate_unwrapped > 100:
        print("Error: Rate must be 0-100!")
        sys.exit(1)

    if effect_id in [7, 8]:
        return (105 - rate_unwrapped) * 2
    else:
        return (105 - rate_unwrapped) // 5
    
def set_debounce_time(ms, profile):
    profile_id = profile if profile is not None else PROFILE_DEFAULT

    try:
        bfr = [0] * 65

        bfr[3] = 0x02
        bfr[4] = 0x01
        bfr[6] = 0x08
        bfr[7] = profile_id
        bfr[8] = ms

        device = hid.Device(vendor_id, product_id)
        device.send_feature_report(bytes(bfr))
        device.close()
        return True
    except:
        return False

def get_battery_status(wired):
    device = hid.Device(vendor_id, product_id)

    bfr_w = [0] * 65
    bfr_w[3] = 0x02
    bfr_w[4] = 0x02
    bfr_w[6] = 0x83

    device.send_feature_report(bytes(bfr_w))

    time.sleep(0.05) 

    bfr_r = device.get_feature_report(0, 65)
    
    if not bfr_r:
        return False

    percentage = bfr_r[8] if bfr_r[8] != 0 else 1

    status_map = [0xA1, 0xA4, 0xA2, 0xA0, 0xA3]
    
    try:
        status = status_map.index(bfr_r[1])
    except ValueError:
        status = 2 

    if bfr_r[6] != 0x83:
        status = 2

    if status == 0 and not wired:
        return f"{percentage}%"
    elif status == 0 and wired:
        charging_status = (
            "charging" if percentage < 100 else "fully charged"
        )
        return f"{percentage}% ({charging_status})"
    elif status == 1:
        return "(asleep)"
    elif status == 3:
        return "(waking up)"
    else:
        return f"[1:{bfr_r[1]:02X}, 6:{bfr_r[6]:02X}, 8:{bfr_r[8]:02X}] (unknown status)"



