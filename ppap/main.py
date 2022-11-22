import sys
sys.path.append(".")
from ppap import libshared, libcrypt, wsclient
import json
import threading, time
import asyncio


class Main(wsclient.Client):
    def __init__(self, host, port, name):
        self.rpc_handler = {
            'echo': self.echo
        }
        self.name = name
        super(Main, self).__init__(host, port, name)


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
            'source': 'ppap_backend', 'dest': 'action', 'func': 'order',
            'homeworkstr': 'write cis note',
            'bedid': bedid, 'eprid': eprid
        }
        print("ppap_backend: send " + str(data_dict))
        asyncio.run(self.send_encryptedmsg(data_dict))
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