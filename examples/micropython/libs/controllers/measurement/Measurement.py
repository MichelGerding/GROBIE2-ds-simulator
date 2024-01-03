import math

class Measurement: 

    lumen: int
    temperature: float

    def __init__(self) -> None:
        self.data = {}

    def encode(self):
        """ encode data to bytes """
        temp_int = math.floor(self.data['temperature'])
        lumen_int = math.floor(self.data['lumen'])

        return b''.join([temp_int.to_bytes(2, 'big'), lumen_int.to_bytes(2, 'big')])
    
    @staticmethod
    def decode(inp: bytes):
        """ decode data from bytes """
        temp_int = int.from_bytes(inp[:2], 'big')
        lumen_int = int.from_bytes(inp[2:4], 'big')
        
        m = Measurement()
        m.data['temperature'] = temp_int
        m.data['lumen'] = lumen_int
        
        return m


    def __str__(self) -> str:
        return ','.join([str(value) for value in self.data.values()])


