from libs.controllers.config import ConfigController, NodeConfigData
from libs.controllers.measurement import MeasurementController
from libs.controllers.measurement.Measurement import Measurement
from libs.controllers.network import INetworkController
from libs.controllers.network.E220NetworkController import Frame, E220NetworkController
from libs.controllers.replication import ReplicationController
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
        
        self.config_controller = ConfigController(
            config = NodeConfigData(
                addr = network_controller.address,
                measurement_interval = 1,
                replication_count = 0
            ),
            send_message= network_controller.send_message
        )

        self.replication_controller = ReplicationController(self.config_controller)
        
        # get the correct path to the data
        self.storage_path = storage_controller.get_root_path() + 'measurements.txt'
        try:
            storage_controller.ensure_exists(self.storage_path)
        except:
            print('could not create file')


        # Register message callbacks
        self.network_controller.register_callback(-1, lambda frame: print('received a message'))  # -1 is a wildcard type

        self.network_controller.register_callback(Frame.FRAME_TYPES['measurment'], self.store_measurement_frame)   # decide if we want to store the measurement
        self.network_controller.register_callback(Frame.FRAME_TYPES['discovery'], self.config_controller.handle_message)  # new nodes will broadcast this type of message
        self.network_controller.register_callback(Frame.FRAME_TYPES['config'], self.config_controller.handle_message)  # handle config changes
        self.network_controller.register_callback(Frame.FRAME_TYPES['replication'], self.replication_controller.handle_bid)  # handle replication changes
        
        print(self.network_controller.callbacks)

        print('node has been initialized, starting controllers')


        # make and send measuremnt every 1 second
        self.measurement_controller.start()
        self.network_controller.start()
        print('node has been initialized, controllers started')

    def init_storage(self):
        self.storage_controller.mount('/sd')


    def store_measurement_frame(self, frame: Frame):
        print('storing measurement frame')

        # check if we should store 
        if self.replication_controller.should_replicate(frame.source_address):
            measurement = Measurement.decode(frame.data)
            return self.store_measurement(measurement)


        # check if it needs new replications
        if self.replication_controller.are_replicating(frame.source_address):
            # check if we have enough replications
            if len(self.replication_controller.config_controller.ledger[frame.source_address].replications) < self.replication_controller.config_controller.ledger[frame.source_address].replication_count:
                # send a bid
                self.network_controller.send_message(3, frame.ttl.to_bytes(4, 'big'), frame.source_address)
                return        

        


    def store_measurement(self, measurement: Measurement, address=None):
        print('storing measurement')

        f = None
        try: 
            f = open(self.storage_path, 'a')
        except:
            f = open(self.storage_path, 'w')

        if address is None:
            address = self.network_controller.address

        f.write(f'{address},{str(measurement)}\n')

        f.flush()
        f.close()

        return measurement

        
    