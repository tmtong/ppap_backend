import sys
sys.path.append(".")
import asyncio
import websockets
from ppap import libshared
import json
# import traceback
# import ssl
# import pathlib
# from mimo import db


class Server:
    handler = {}
    clients = set()

    def __init__(self, host, port):
        self.host = "0.0.0.0" # if inside docker, need to listen to 0.0.0.0, not localhost, not 127.0.0.1
        self.port = port
        libshared.log("start wsbus at " + self.host + " with port " + str(self.port))
        self.handler[libshared.PACKET_TYPE_DATA] = self.handle_data
        

    async def receive(self, websocket, path):
        self.clients.add(websocket)
        await self.send_connected(websocket)
        while True:
            try:
                packet = await websocket.recv()
                if isinstance(packet, str) and ',' in packet: # flutter web, send out a comma seperated string, but not flutter linux
                    packet = packet.split(',')
                    packet = [int(i) for i in packet] 
                    packet = bytes(packet)
                # packet = self.handler[packet[libshared.lengthsize]](packet[libshared.lengthsize + 1:], websocket)
                await self.broadcast(packet)
            
            except websockets.exceptions.ConnectionClosedOK :
                libshared.log("wsbus: connection close")
                await websocket.close()
                self.clients.discard(websocket)
                break
            except Exception as e:
                libshared.log("wsbus: crashed on receive")
                libshared.log(str(e))
                await websocket.close()
                self.clients.discard(websocket)
                break
    def handle_data(self, data, websocket):
        packet = [None] * libshared.bufsize
        packet[libshared.lengthsize] = libshared.PACKET_TYPE_DATA
        packet[libshared.lengthsize + 1:] = data
        packet[0:libshared.lengthsize] = (len(data)).to_bytes(libshared.lengthsize, byteorder='big')
        
        return bytes(packet)          
    async def broadcast(self, packet):
        for client in self.clients:
            try:
                await client.send(packet)
            except:
                continue
    def serve_forever(self):
        # start_server = websockets.serve(self.receive, self.host, self.port, ping_timeout=None)
        start_server = websockets.serve(self.receive, self.host, self.port)
        
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    async def send_connected(self, websocket):
        clientip = websocket.remote_address[0]
        payloadjson = {}
        payloadjson['clientip'] = clientip
    
        data = json.dumps(payloadjson)
        packet = [None] * libshared.bufsize
        packet[libshared.lengthsize] = libshared.PACKET_TYPE_CONNECTED
        packet[libshared.lengthsize + 1:] = data.encode()
        packet[0:libshared.lengthsize] = (len(data)).to_bytes(libshared.lengthsize, byteorder='big')
        libshared.log("wsbus: send " + data)
        await websocket.send(bytes(packet))

def main():
    host = libshared.bushost
    port = libshared.busport
    server = Server(host, port)

    server.serve_forever()
if __name__ == '__main__':
    main()

