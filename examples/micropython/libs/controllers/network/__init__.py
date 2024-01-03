import asyncio

class Frame: 
    FRAME_TYPES = {
        'discovery': 0x00,
        'data': 0x01,
        'config': 0x02
    }

    def __init__(self, type: int, message: bytes, source_address):
        self.type = type
        self.data = message
        self.source_address = source_address

    def serialize(self) -> bytes:
        return b''.join([
            self.type.to_bytes(1, 'big'), 
            self.source_address.to_bytes(1, 'big'), 
            self.data
        ])

    @staticmethod
    def deserialize(frame: bytes):
        type = frame[0]
        source_address = int.from_bytes(frame[1:3], 'big')
        message = frame[3:]

        return Frame(type, message, source_address)

class INetworkController: 
    """ the abstract base class for all network controllers """

    task: asyncio.Task
    callbacks: dict[int, list]

    def __init__(self):
        self.callbacks = {}
        

    def start(self):
        """ start the network controller """
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self._start())

    async def _start(self):
        """ the main loop of the network controller """
        raise NotImplementedError()

    def stop(self):
        """ stop the network controller """
        self.task.cancel()

    def send_message(self, type: int, message: bytes, addr=b'\xff\xff'):
        """ send a message to the specified address """
        raise NotImplementedError()

    def register_callback(self, addr: int, callback):
        """ register a callback for the specified address """
        if addr not in self.callbacks:
            self.callbacks[addr] = []

        self.callbacks[addr].append(callback)

    def on_message(self, message: bytes):
        """ called when a message is recieved """
        print(f'recieved message {message}')

        frame = Frame.deserialize(message)

        if frame.type in self.callbacks:
            for callback in self.callbacks[frame.type]:
                callback(frame)


    @property
    def address(self) -> bytes:
        """ the address of the network controller """
        return b'\x00\x00'

