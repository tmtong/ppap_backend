import sys
sys.path.append(".")

from signal import signal, SIGINT
import threading
import ssl
import traceback
from bson import json_util
import socket
import random
import hashlib
import json
import time
import websockets
import asyncio
from ppap import libshared, libcrypt


class Client:
    sock = None

    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name

        self.rpc_handler = {}
        self.handler = {}
        # self.srpserver_init()
        self.handler[libshared.PACKET_TYPE_DATA] = self.handle_encrypteddata
        self.handler[libshared.PACKET_TYPE_CONNECTED] = self.handle_connected
        self.handler[libshared.PACKET_TYPE_PING] = self.handle_ping

        if libshared.symmetrykey == "":
            f = open('./sec/bus.sec', 'r')
            libshared.symmetrykey = f.readlines()[0].rstrip()

    async def connect(self):
        uri = 'ws://' + self.host + ':' + str(self.port)
        while True:
            try:
                self.sock = await websockets.connect(uri)
                #libshared.log("wsclient: " + self.name +
                #              " connected to " + self.host)
                break
            except:
                libshared.log("wsclient: wsbus server " +
                              self.host + " is offline")
                # traceback.print_exc(file=sys.stdout)
                time.sleep(1)
                continue

    async def receive(self):
        await self.connect()
        while True:
            try:
                message = await self.sock.recv()
                if message[libshared.lengthsize] in self.handler:
                    await self.handler[message[libshared.lengthsize]](message[(libshared.lengthsize + 1):])
            except Exception as e:
                libshared.log("wsclient: exception on receive " + str(e))
                traceback.print_exc(file=sys.stdout)
                await self.connect()
                continue

    def receiveloop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.receive())

    async def handle_encrypteddata(self, data):
        encrypted_data = bytes(data)
        try:
            data_str = libcrypt.twoway_decrypt(
                encrypted_data, str(libshared.symmetrykey))
        except:
            libshared.log('wsclient: cannot decrypt')
            return
        data_dict = json.loads(data_str)
        if data_dict["dest"] == self.name:
            await self.handle_rpc(data_dict)

    async def handle_connected(self, data):
        pass

    async def handle_ping(self, data):
        await self.send_plainmsg(libshared.PACKET_TYPE_PINGREPLY, data.decode())


    async def handle_rpc(self, data_dict):
        if 'func' not in data_dict:
            libshared.log("wsclient: func name not specified")
            return
        func = data_dict['func']
        if func not in self.rpc_handler:
            libshared.log("wsclient: func " + func +
                          " not found in rpc_handler")
            return
        libshared.log("wsclient: receive " + str(data_dict))
        await self.rpc_handler[func](data_dict)

    async def send_encryptedmsg(self, data_dict):
        while True:
            try:
                data_str = json.dumps(data_dict, default=json_util.default)

                encrypted_data = libcrypt.twoway_encrypt(
                    data_str, str(libshared.symmetrykey))
                # print("encrypted length: " + str(len(encrypted_data)))

                packet = [None] * libshared.bufsize
                packet[libshared.lengthsize] = libshared.PACKET_TYPE_DATA
                packet[libshared.lengthsize + 1:] = encrypted_data
                packet[0:libshared.lengthsize] = (len(encrypted_data)).to_bytes(
                    libshared.lengthsize, byteorder='big')
                libshared.log("wsclient: send msg " + str(data_dict))
                await self.sock.send(bytes(packet))
                return
            except Exception as e:
                libshared.log("wsclient: exception on send " + str(e))
                traceback.print_exc(file=sys.stdout)
                await self.connect()
                time.sleep(2)
                continue

    def wait_socket(self):
        while True:
            if self.sock is None:
                time.sleep(0.2)
            else:
                break

    ##########################################
    # SRP Stack
    ##########################################

    def H(self, *a):  # a one-way hash function
        a = ':'.join([str(a) for a in a])
        return int(hashlib.sha256(a.encode('ascii')).hexdigest(), 16)

    def cryptrand(self, n=1024):
        # return random.SystemRandom().getrandbits(n) % self.N
        return 256
    N = '''00:c0:37:c3:75:88:b4:32:98:87:e6:1c:2d:a3:32:
       4b:1b:a4:b8:1a:63:f9:74:8f:ed:2d:8a:41:0c:2f:
       c2:1b:12:32:f0:d3:bf:a0:24:27:6c:fd:88:44:81:
       97:aa:e4:86:a6:3b:fc:a7:b8:bf:77:54:df:b3:27:
       c7:20:1f:6f:d1:7f:d7:fd:74:15:8b:d3:1c:e7:72:
       c9:f5:f8:ab:58:45:48:a9:9a:75:9b:5a:2c:05:32:
       16:2b:7b:62:18:e8:f1:42:bc:e2:c3:0d:77:84:68:
       9a:48:3e:09:5e:70:16:18:43:79:13:a8:c3:9c:3d:
       d0:d4:ca:3c:50:0b:88:5f:e3'''

    N = int(''.join(N.split()).replace(':', ''), 16)  # public modulus
    g = 2        # generator


    def srpclient_init(self, handle_srpconnected):
        self.handler[libshared.PACKET_TYPE_REGISTER_RESULT] = self.srpclient_registerresult
        self.handler[libshared.PACKET_TYPE_LOGIN2] = self.srpclient_login2
        self.handler[libshared.PACKET_TYPE_LOGIN4] = self.srpclient_login4
        self.handler[libshared.PACKET_TYPE_FAIL] = self.srpclient_fail
        self.handle_srpconnected = handle_srpconnected
        self.k = self.H(self.N, self.g)

    async def send_plainmsg(self, packet_type, data_dict):
        data_str = json.dumps(data_dict)
        packet = [None] * libshared.bufsize
        packet[libshared.lengthsize] = packet_type
        packet[libshared.lengthsize + 1:] = data_str.encode()
        packet[0:libshared.lengthsize] = (len(data_str)).to_bytes(
            libshared.lengthsize, byteorder='big')

        await self.sock.send(bytes(packet))

    async def srpclient_register(self, username, password):
        I = username         # Username
        p = password         # Password
        s = self.cryptrand(64)    # Salt
        x = self.H(s, I, p)       # Private key
        v = pow(self.g, x, self.N)     # Password verifier
        data_dict = {'source': self.name, 'dest': 'thinker',
                     'I': username, 's': str(s), 'v': str(v)}
        libshared.log("wsclient srpclient_register send " + str(data_dict))
        await self.send_plainmsg(libshared.PACKET_TYPE_REGISTER, data_dict)


    async def srpclient_registerresult(self, data_dict):
        pass


    async def srpclient_login1(self, username, password):
        a = self.cryptrand()      # Secret ephemeral value
        A = pow(self.g, a, self.N)
        self.A = A
        self.I = username
        self.p = password
        self.a = a
        data_dict = {'source': self.name,
                     'dest': 'thinker', 'I': username, 'A': str(A)}
        await self.send_plainmsg(libshared.PACKET_TYPE_LOGIN1, data_dict)

    async def srpclient_login2(self, data_str):
        data_dict = json.loads(data_str)
        if data_dict["dest"] != self.name:
            return
        if data_dict['I'] != self.I:
            return
        A = self.A
        I = self.I
        p = self.p
        a = self.a
        s = int(data_dict['s'])
        B = int(data_dict['B'])
        u = self.H(A, B)      # Random scrambling parameter
        x = self.H(s, I, p)
        S_c = pow(B - self.k * pow(self.g, x, self.N), a + u * x, self.N)
        K_c = self.H(S_c)
        M_c = self.H(self.H(self.N) ^ self.H(self.g), self.H(I), s, A, B, K_c)
        data_dict = {'source': self.name,
                     'dest': 'thinker', 'M_c': str(M_c), 'I': I}
        await self.send_plainmsg(libshared.PACKET_TYPE_LOGIN3, data_dict)
        self.M_c = M_c
        self.K_c = K_c

    async def srpclient_login4(self, data_str):
        data_dict = json.loads(data_str)
        if data_dict["dest"] != self.name:
            return
        if data_dict['I'] != self.I:
            return
        M_s_server = int(data_dict['M_s'])
        A = self.A
        M_c = self.M_c
        K_c = self.K_c
        M_s_client = self.H(A, M_c, K_c)

        # Check equality of keys
        if M_s_server == M_s_client:
            self.handle_srpconnected('success')
            libshared.authkey = K_c
        else:
            self.handle_srpconnected('fail')

    async def srpclient_fail(self, data_dict):
        self.handle_srpconnected('fail')

#############################################
## SAMPLE CODE TO USE WSCLIENT
#############################################
'''
class PacketInjector(Client):
    def __init__(self, host, port, name):
        self.rpc_handler = {
            'echo': self.echo
        }
        self.name = name
        super(PacketInjector, self).__init__(host, port, name)


    async def echo(self, data_dict):
        dest = data_dict["source"]
        data_dict = {
            "source": self.name,
            "dest": dest,
            "func": "echoreply",
            "reply": "alive",
        }
        libshared.log("action: send " + json.dumps(data_dict))
        await self.send_encryptedmsg(data_dict)
    def main(self, bedid, eprid):

        data_dict = {
            'source': 'thinker', 'dest': 'action', 'func': 'order',
            'homeworkstr': 'write cis note',
            'bedid': bedid, 'eprid': eprid
        }
        print("packetinjector: send " + str(data_dict))
        asyncio.run(self.send_encryptedmsg(data_dict))
def main():
    packetinjector = PacketInjector(
        libshared.bushost, libshared.busport, 'packetinjector')
    thread_receive = threading.Thread(
        target=packetinjector.receiveloop, args=())
    thread_receive.daemon = True

    thread_main = threading.Thread(target=packetinjector.main, args=())

    thread_receive.start()
    time.sleep(2)
    thread_main.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        sys.exit(0)
'''
if __name__ == "__main__":
    busport = 7801
    bushost = '192.168.1.145'
    client = Client(bushost, busport, "client")
    client.receiveloop()