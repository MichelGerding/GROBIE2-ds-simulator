

from libs.controllers.config.Ledger import Ledger
from libs.controllers.config.NodeConfigData import NodeConfigData
from libs.controllers.network import Frame
from libs.helpers.dict import deserialize_dict

class ConfigController: 

    def __init__(self, config: NodeConfigData):
        self._config = config

        self._ledger = Ledger()

    
    @property
    def config(self):
        return self._config
    
    @property
    def ledger(self):
        return self._ledger
    

    def handle_message(self, frame: Frame):

        # check if it is a discovery message
        if frame.type == Frame.FRAME_TYPES['discovery']:
            # parse the message
            config = NodeConfigData.deserialize(frame.data)
            # update the ledger
            self._ledger[config.addr] = config

        # check if it is a config message. contain a diff
        elif frame.type == Frame.FRAME_TYPES['config']:
            # parse the message
            config = deserialize_dict(frame.data)
            # apply the diff to the config
            self._ledger.apply_diff(config, frame.source_address)



        