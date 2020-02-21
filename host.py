import asyncio
import websockets
from time import sleep
import threading

class AudioServer():
    def __init__(self):
        self.start = False #asyncio.Event()
        self.stop = False #asyncio.Event()
        self.rec_folder = ""
        self.filename = "test.wav"

        start_server = websockets.serve(self.record, 'localhost', 8765) #169.254.136.174' 169.254.136.174
        asyncio.get_event_loop().run_until_complete(start_server)
        t = threading.Thread(target=asyncio.get_event_loop().run_forever, args=())
        t.start()

    async def record(self, websocket, path):
        while True:
            while True:
                if self.start:
                    break
                sleep(1)

            await websocket.send("Start")
            await websocket.recv()

            await websocket.recv() #asking_for_path
            await websocket.send(self.rec_folder)

            await websocket.recv() #asking for filename
            await websocket.send(self.filename)
            
            while True:
                if self.stop:
                    break
                sleep(1)

            await websocket.send(path)
            self.start = False
            self.stop = False
            #self.start.clear()
            #self.stop.clear()

#s = AudioServer()
#s.start.set()
