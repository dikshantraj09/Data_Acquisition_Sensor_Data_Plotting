
import socket
import select
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation as animation
import pyautogui as pa

HEADER_LENGTH = 10

IP = "0.0.0.0"
PORT = 1234
x_arr, y_arr, z_arr = [], [], []
x_gry, y_gry, z_gry = [], [], []

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Handles message receiving
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False
fig = plt.figure()
while True:

    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    
    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                plt.close('all')
                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]
            
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            x=message["data"].decode("utf-8")

            split=x.split(",")
            time_between_samples = 0.333
            try:
                x, y, z,x_g,y_g,z_g= float(split[0]), float(split[1]), float(split[2]), float(split[3]), float(split[4]),float(split[5])
            except:
                continue
                
            pa.move(-x_g*3,-y_g*3,0.5,pa.easeInOutQuad)


            '''
            if len(x_arr) > 20:
                x_arr.pop(0)
            x_arr.append(x)
            if len(y_arr) > 20:
                y_arr.pop(0)
            y_arr.append(y)
            if len(z_arr) > 20:
                z_arr.pop(0)
            z_arr.append(z)
            
            if len(x_gry) > 20:
                x_gry.pop(0)
            x_gry.append(x_g)
            if len(y_gry) > 20:
                y_gry.pop(0)
            y_gry.append(y_g)
            if len(z_gry) > 20:
                z_gry.pop(0)
            z_gry.append(z_g)'''

            '''
            v_lx = [sum(x_arr[:i]) * time_between_samples for i in range(len(x_arr))]
            #d_lx = [sum(v_lx[:j]) * time_between_samples for j in range(len(v_lx))]
            v_ly = [sum(y_arr[:i]) * time_between_samples for i in range(len(y_arr))]
            #d_ly = [sum(v_ly[:j]) * time_between_samples for j in range(len(v_ly))]            
            v_lz = [sum(z_arr[:i]) * time_between_samples for i in range(len(z_arr))]
            #d_lz = [sum(v_lz[:j]) * time_between_samples for j in range(len(v_lz))]                 
            
            i = list(range(len(x_arr)))
           
        
            ax = plt.axes(projection='3d')
            ax.set_xlim3d(-10,10)
            ax.set_ylim3d(-10,10)
            ax.set_zlim3d(-10,10)
            ax.plot(v_lx,v_ly, v_lz, '-g')
            plt.pause(0.0001)
            
            plt.clf()
            plt.subplot(4, 1, 1)
            plt.plot(i, d_lx, '-g')
            plt.title('X,Y,Z Acceleration Subplots')
            plt.ylabel('X velocity')
            plt.subplot(4, 1, 2)
            plt.plot(i, y_arr, '-k')
            plt.xlabel('time (s)')
            plt.ylabel('Y acceleration')
            plt.subplot(4, 1, 3)
            plt.plot(i, z_arr, '-b')
            plt.xlabel('time (s)')
            plt.ylabel('Z acceleration')
            plt.pause(.2)
            '''

            # Iterate over connected clients and broadcast message
            for client_socket in clients:

                # But don't sent it to sender
                if client_socket != notified_socket:

                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]
