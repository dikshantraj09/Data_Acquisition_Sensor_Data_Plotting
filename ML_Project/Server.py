import socket
import select
from mpl_toolkits import mplot3d
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation as animation
import matplotlib.animation as animation
from numpy.core.fromnumeric import shape
from tensorflow.keras.models import model_from_json
model = model_from_json(open("model1.json", "r").read())
model.load_weights('weights.h5')
model.summary()
HEADER_LENGTH = 10

IP = "0.0.0.0"
PORT = 1234
x_arr, y_arr, z_arr = [], [], []
x_gry, y_gry, z_gry = [], [], []

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        return False


fig = plt.figure()

while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
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

            print('Accepted new connection from {}:{}, username: {}'.format(
                *client_address, user['data'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(
                    clients[notified_socket]['data'].decode('utf-8')))
                plt.close('all')
                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]

            print(
                f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            x = message["data"].decode("utf-8")

            split = x.split(",")
            # print(split)
            time_between_samples = 0.333
            try:
                x, y, z, x_g, y_g, z_g = float(split[1]), float(split[2]), float(
                    split[3]), float(split[5]), float(split[6]), float(split[7])
                #print(x, y, z, x_g, y_g, z_g)
            except:
                continue
            if len(x_arr) > 714:
                x_arr.pop(0)
            x_arr.append(x)
            if len(y_arr) > 714:
                y_arr.pop(0)
            y_arr.append(y)
            if len(z_arr) > 714:
                z_arr.pop(0)
            z_arr.append(z)
            if len(x_gry) > 714:
                x_gry.pop(0)
            x_gry.append(x_g)
            if len(y_gry) > 714:
                y_gry.pop(0)
            y_gry.append(y_g)
            if len(z_gry) > 714:
                z_gry.pop(0)
            z_gry.append(z_g)
            print(len(x_arr))
            i = list(range(len(x_arr)))

            if len(x_arr) > 713:

                test_value = np.array(
                    [[x_arr], [y_arr]])
                print(np.shape(test_value))

                #test = [1.26, 5.68, 47]

                predictions = model.predict(test_value)
                output = np.round(predictions, decimals=3)
                print("predictions =\n", output)
                root = tk.Tk()
                if (output[1][0][0] == 1):
                    print('flex')
                    T = tk.Text(root, height=1, width=8)
                    T.config(font=("Courier", 44))
                    T.pack()
                    T.insert(tk.END, "FLEX")
                    tk.mainloop()
                    # server_socket.close()
                else:
                    print("Punch")
                    T = tk.Text(root, height=1, width=8)
                    T.config(font=("Courier", 44))
                    T.pack()
                    T.insert(tk.END, "PUNCH")
                    tk.mainloop()
                    # server_socket.close()

            # plt.clf()
            # plt.subplot(1, 1, 1)
            # plt.plot(i, x_arr, "-r")
            # plt.plot(i, y_arr, "-g")
            # plt.plot(i, z_arr, "-b")
            # plt.title('X,Y,Z Acceleration Subplots')
            # plt.ylabel('acc')
            # plt.pause(0.001)
            # Iterate over connected clients and broadcast message
            for client_socket in clients:

                # But don't sent it to sender
                if client_socket != notified_socket:

                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(
                        user['header'] + user['data'] + message['header'] + message['data'])

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]
