import sqlite3
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation as animation

usr = []
x_arr, y_arr, z_arr = [], [], []
x_gra, y_gra, z_gra = [], [], []
conn = sqlite3.connect('/home/dikshantraj09/Documents/DBMS/imu.db')
print("-----CONNECTED-----")
cur = conn.cursor()
cur.execute("SELECT * FROM Accelerometer,Spatial_Orientation")

rows = cur.fetchall()

for row in rows:
    usr.append(row[3])
    x_arr.append(row[0])
    y_arr.append(row[1])
    z_arr.append(row[2])
    x_gra.append(row[4])
    y_gra.append(row[5])
    z_gra.append(row[6])
    # x_gra = row[4]
    # y_gra = row[5]
    # z_gra = row[6]
    # x_gry = row[8]
    # y_gry = row[9]
    # z_gry = row[10]
    # x_so = row[12]
    # y_so = row[13]
    # z_so = row[14]

i = list(range(len(rows)))
fig = plt.figure()


def animate(y):

    plt.subplot(6, 1, 1)
    plt.plot(i, x_arr, '-g')
    plt.title("circle")
    plt.ylabel('X acc')

    plt.subplot(6, 1, 2)
    plt.plot(i, y_arr, '-k')
    plt.xlabel('time (s)')
    plt.ylabel('Y acc')

    plt.subplot(6, 1, 3)
    plt.plot(i, z_arr, '-b')
    plt.xlabel('time (s)')
    plt.ylabel('Z acc')

    plt.subplot(6, 1, 4)
    plt.plot(i, z_gra, '-y')
    plt.xlabel('time (s)')
    plt.ylabel('Z gry')

    plt.subplot(6, 1, 5)
    plt.plot(i, z_gra, '-r')
    plt.xlabel('time (s)')
    plt.ylabel('Z gry')

    plt.subplot(6, 1, 6)
    plt.plot(i, z_gra, '-c')
    plt.xlabel('time (s)')
    plt.ylabel('Z gry')


ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
