from libs.controllers.measurement import MeasurementController
from libs.controllers.measurement.Measurement import Measurement
from libs.controllers.network import INetworkController
from libs.controllers.network.E220NetworkController import Frame, E220NetworkController
from libs.sensors import ISensor
from libs.controllers.storage import IStorageController


class Node(): 

    def __init__(self, 
                 sensors: list[ISensor], 
                 storage_controller: IStorageController, 
                 network_controller: INetworkController) -> None:
        
        self.sensors = sensors
        self.storage_controller = storage_controller
        self.network_controller = network_controller

        self.init_storage()

        self.measurement_controller = MeasurementController(
            sensors = self.sensors, 
            actions = [
                lambda m: print(type(m), str(m)),
                lambda measurement: self.store_measurement(measurement),
                lambda measurement: network_controller.send_message(1, measurement.encode())
            ])
        
        # get the correct path to the data
        self.storage_path = storage_controller.get_root_path() + 'measurements.txt'
        try:
            storage_controller.ensure_exists(self.storage_path)
        except:
            print('could not create file')

        self.network_controller.register_callback(1, self.store_measurement_frame)
        print('node has been initialized, starting controllers')


        # make and send measuremnt every 1 second
        self.measurement_controller.start()
        self.network_controller.start()
        print('node has been initialized, controllers started')

    def init_storage(self):
        self.storage_controller.mount('/sd')


    def store_measurement_frame(self, frame: Frame):
        print('storing measurement frame')
        measurement = Measurement.decode(frame.data)
        return self.store_measurement(measurement)



    def store_measurement(self, measurement: Measurement, address=None):
        print('storing measurement')

        f = None
        try: 
            f = open(self.storage_path, 'a')
        except:
            f = open(self.storage_path, 'w')

        if address is None:
            address = int.from_bytes(self.network_controller.address, 'big')

        f.write(f'{address},{str(measurement)}\n')

        f.flush()
        f.close()

        return measurement

        
    