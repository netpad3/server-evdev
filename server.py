import socket, math, traceback
from evdev import UInput, AbsInfo, ecodes as ec

PORT = 6723

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))

info = {}

while True:
    data, addr = sock.recvfrom(1024)
    try:
        print(addr)
        print(data)
        spl = data.decode('utf-8').split(';')
        axes = spl[0].split(",")
        buttons = 1
        if len(spl) > 1:
            buttons = int(spl[1],16)
        btncount = math.floor(math.log(buttons)/math.log(2))
        if not (addr in info) or info[addr]["btncount"] != btncount or info[addr]["axiscount"] != len(axes):
            print("new address")
            if addr in info:
                # not really new, but needs to be destroyed
                info[addr]["device"].close()
            caps = {
                    ec.EV_ABS: [],
                    ec.EV_KEY: []
                    }
            for i in range(0, len(axes)):
                caps[ec.EV_ABS].append((i, AbsInfo(0, -32767, 32767, 0, 0, 0)))
            for i in range(0, btncount):
                caps[ec.EV_KEY].append(256+i)
            info[addr] = {
                    "device": UInput(caps, name=('Netpad3-'+str(len(axes))+'-'+str(btncount))),
                    "btncount": btncount,
                    "axiscount": len(axes)
                    }
        dev = info[addr]["device"]
        for i in range(0, len(axes)):
            dev.write(ec.EV_ABS, i, int(axes[i]))
        for i in range(0, btncount):
            value = (buttons >> (btncount-i)) % 2
            dev.write(ec.EV_KEY, 256+i, value)
        dev.syn()
    except:
        traceback.print_exc()
