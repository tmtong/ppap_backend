import sys
sys.path.append(".")
from ppap import libshared, libcrypt, wsclient
import json
import threading, time
import asyncio
import livekit
from datetime import datetime, timedelta

class Main(wsclient.Client):
    def __init__(self, host, port, name):
        super(Main, self).__init__(host, port, name)
        self.rpc_handler = {
            'echo': self.echo,
            'livekittoken': self.livekittoken,
        }
        self.name = name


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
    async def livekittoken(self, data_dict):
        bedid = data_dict['bedid']
        room = data_dict['room']
        grant = livekit.VideoGrant(room_join = True, room = room)
        access_token = livekit.AccessToken(libshared.livekitapikey, libshared.livekitsecret, grant = grant, identity = bedid, name = bedid, ttl=timedelta(days=1000))
        token = access_token.to_jwt()
        data_dict = {
            'source': 'ppap_backend', 'dest': data_dict['source'], 'func': 'livekittokenreply',
            'bedid': bedid,
            'token': token,
        }
        print("ppap_backend: send " + str(data_dict))
        await self.send_encryptedmsg(data_dict)

    def main(self):

        while True:
            time.sleep(1)
def main():
    ppap_backend = Main(
        libshared.bushost, libshared.busport, 'ppap_backend')
    thread_receive = threading.Thread(
        target=ppap_backend.receiveloop, args=())
    thread_receive.daemon = True

    thread_main = threading.Thread(target=ppap_backend.main, args=())

    thread_receive.start()
    time.sleep(2)
    thread_main.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
