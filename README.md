# GROBIE2 simulator
this project contains a minimalistic simulator for the grobie 2 project of the minor IoT of the hanze universitie of applied sciences.
the project is done in collaberation with the hochschule Bremen.


## the simulator
the simulator is currently a simple python tui which runs the network nodes and ui inn a seperate thread. 
the simulator will only simulate perfect networks as message collisions, seperated meshes, and other network issues are not simulated.


## running the simulator
to run the simulator you need to have python 3.7 or higher installed on your system.

once you have python installed you can run the simulator by running the following command in the root of the project:
```bash
python3 main.py
```

this will open the simulator tui and shown will be the commands you can use to interact with the simulator.
to close it you can use the ctrl+c command.

### windows
for windows a aditional package will need to be installed. that can be done with the following command
```bash
pip install windows-curses
```

### macos
the simulator is not tested on macOS. if you have any issues running it on macos please contact us.


## simulator commands
the simulator has a few commands you can use to interact with it. these commands are shown in the simulator tui.
the commands are as follows:
- `create (node_ids, *) (channel)` creates one or more new nodes 
- `del (node_id)` deletes a node 
- `stop` stops a node from sending measurements
- `mod (node_id) (key) (value)` changes the config of a node
- `save` saves the nodes info into a file called `config.csv`
- `exit` closes the simulator
