# GROBIE2 simulator

this project contains a minimalistic simulator for the grobie 2 project of the minor IoT of the hanze universitie of 
applied sciences. the project is done in collaberation with the hochschule Bremen.

## the simulator

the simulator is currently a simple python tui which runs the network nodes and ui inn a separate thread. the simulator 
will only simulate perfect networks as message collisions, seperated meshes, and other network issues are not simulated.

what is included is the ability to implement routing protocols. the system makes use of a simple routing protocol. it 
currently just broadcasts all messages it hasn't seen and aren't for itself.

you can also connect to the simulator using sockets. the server will open a socket connection on port 9174 or specified 
by the `--port` argument. the simulator will see the connection as a node and will send the measurements to the 
connected client.

## running the simulator

to run the simulator you need to have python 3.7 or higher installed on your system.
once you have python installed you can run the simulator by running the following command in the root of the project:

```bash
python3 main.py --port 9174
```

this will open the simulator tui and shown will be the commands you can use to interact with the simulator.
to close it you can use the ctrl+c command.

### windows

for windows an additional package will need to be installed. that can be done with the following command

```bash
pip install windows-curses
```

### macos

the simulator is not tested on macOS. if you have any issues running it on macos please contact us.

## using the simulator

the simulator can be used in two ways. the first is by using the tui and the second is by connecting nodes to the
simulator using sockets. sending commands to the network will always be done using the tui.

### tui

the tui is the main way to interact with the simulator. it will show the network topology and the commands you can use
to interact with it. the tui exists of 2 parts. a network log on the right and a command log on the left. on the bottom 
there is a input to enter commands.

#### commands

the simulator has a few commands you can use to interact with it. these commands are shown in the simulator tui.
the commands are as follows: arguments surrounded with `[]` are optional and arguments surrounded with `()` are
required.

- `load [filename]` load a file with commands to run in the simulator. the default file is `cmds_load.txt`. the file
  should contain a single command per line.
- `create (node_id) (x_pos) (y_pos) (range)` creates one or more new nodes
- `delete (node_id)` deletes a node
- `modify (node_id) (replications) (delay)` changes the config of a node
- `save [filename]` saves the nodes info into a file called `tmp/config.json`. if filename ends in .pickle it will save
  it using the pickle format.
- `print [filename]` store the network topography as an image or open in separate window.
- `exit` closes the simulator

#### load command

with the load command you can load a file with comman ds to run in the simulator. the default location of the file is 
`cmds_load.txt`. the file should contain a single command per line. theses commands are exactly the same as input into 
the tui. the commands will be executed in the order they are in the file with no delay inbetween. an example of this 
file is located in the `cmds_load_example.txt` file. that example file wil create 7 nodes which are not all directly 
connected. it also showcases that it is possible to have 1 way connections between nodes.

#### print command
the print command can be used to export the network topology as an image. this command can be run with an optional 
argument, `filename`. if this argument is not provided it will open an image in a separate window. if the argument is 
provided it will save the image to the given filename. the image will be saved as the provided extension. the currently supported and tested extensions are png, svg and pdf.


this image will show the network topology and the connections between the nodes. it will also draw a circle around each 
node which represents the range of the node.

### connecting using socket

the simulator also supports connecting nodes using sockets. connecting to the server uses a simple protocol.
once joined the server will expect a pickled object containing the following fields:

- `node_id` the id of the node
- `x` the x position of the node
- `y` the y position of the node
- `r` the range of the node

once this is received the server will create a node with the given information. any data this node receives will be 
forwarded to the client. all filtering and routing should be done by the client itself.

this node will receive messages from the server as pickled Message classes. these classes can be found in the 
`libs/network/Message.py` file. the message class contains the following fields:

- `receiving_id` the id of the node that needs to receive the message
- `sending_id` the id of the node that send the message
- `channel` the channel the message was sent on
- `payload` the payload of the message
- `msg_id` the id of the message
- `hops` the amount of hops the message has taken

the network expects the client to send message of the same class back to the server.

an example socket node can be found in the file `examples/SocketClientNode.py`. this node will connect to 
the network and propagate messages on the network. next to that it will print message that are send to it. so it is a 
minimal example of how to connect to the network using sockets.

#### advantages
the biggest advantage of using sockets to connect is that you can use any language you want to connect to the network. 
next to that it will also make it easier to test your own routing protocol as you can more easily test it in isolation. 
as it will be on its own process. because it is on a separate process it will also increase the performance as all normal 
nodes run on a separate thread. due to this the simulator will be able to handle more nodes. 

### file structure

the simulator creates a large amount of files to store data, log network messages, commands and terminal output and
more. the file structure is as follows:

- `tmp/` contains temporary files used by the simulator
    - `log.txt` contains a log of terminal messages
    - `network_log.txt` contains a log of network messages
    - `commands/` contains log of all commands send in the simulator
        - `cmds_{timestamp}.txt` contains a log of commands send in the sessions started at timestamp
    - `databases/` contains all databases of all nodes that are created
        - `{timestamp}_{random_number}_{node_id}.csv` contains the database of node with id node_id


## TODO
the todos are unordered but have a priority assigned to them. for this the moscow method is used.
the todos are as follows:

- [ ] convert threads to processes to allow for concurrent execution              **_must have_**
- [ ] add support for network issues                                              **_must have_**
  - [ ] add support for message collisions                                        **_must have_**
  - [ ] add support for message loss                                              **_must have_**
  - [ ] add support for message corruption                                        **_must have_**
  - [ ] add support for mesh separation                                           **_must have_**
    - [ ] add support for mesh separation due to node failure                     **_must have_**
    - [ ] add support for mesh separation due to network issues                   **_must have_**
  - [ ] add support for high interference areas (e.g. near a microwave)           **_nice to have_**
    - [ ] add non-uniform transmission range (e.g. ellipse instead of circle)     **_nice to have_**       
  - [ ] add support for node failure                                              **_should have_**
- [ ] test support for merging meshes                                             **_must have_**
- [ ] address todos in code                                                       **_must have_**
- [ ] config not always correctly shared                                          **_must have_**