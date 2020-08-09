#-*- coding:utf-8 -*-
import math
import numpy as np
import scipy.linalg as la
import sys
import time
import serial
import socket #UDP LAN
import pynmea2
import pymap3d
import matplotlib.pyplot as plt
import opti_test

# import pyserial
import threading
import queue

sys.path.append("C:/Users/sun84/Desktop/test") # C:/Users/Junhyeok/Desktop/test lab:  C:/Users/cvlab/Desktop/test

try:
    import cubic_spline_planner
except ImportError:
    raise

global WB,k,Lfc,dt

base_lat = 37.23896333333333  #37.2389619983  #37.23896  #37.3847120383
base_lon = 126.77297833333333  #126.772982033  #126.77298  #126.65599282
base_alt =  0.9 #29.976  #0.9    #45.5384


ser = serial.serial_for_url('COM1', baudrate=115200, timeout=1) #network with car

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP LAN
recv_address = ('127.0.0.1', 3051)
sock.bind(recv_address)

def pi_2_pi(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi

def make_path():
    # ax = [-0.00000, 37.710929]
    # ay = [0.184970, 71.583569]
    ax = []
    ay = []
    
    ayaw =[]
    ak = []
    a_s =[]


    path_cand= open("C:/Users/sun84/Desktop/ygs.txt")   # C:/Users/cvlab/Desktop/test/test_track.txt lab: "C:/erp/examples/simulation_example/path.txt",'r' "C:/Users/cvlab/Desktop/test/path.txt",'r'
    lines = path_cand.readlines()
    # print(lines)
    for line in lines:
        x_cand = line.split('\t')[0]
        y_cand = line.split('\t')[1]

        yaw_cand = line.split('\t')[2]
        k_cand = line.split('\t')[3]
        s_cand = line.split('\t')[4]

        ax.append(float(x_cand))
        ay.append(float(y_cand))

        ayaw.append(float(yaw_cand))
        ak.append(float(k_cand))
        a_s.append(float(s_cand))

    path_cand.close()

    return ax, ay, ayaw, ak, a_s


def get_xy(lat, lon, alt):
    e, n, u = pymap3d.geodetic2enu(lat, lon, alt, base_lat, base_lon, base_alt)
    return e, n

class TargetCourse:

    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.old_nearest_point_index = None

    def search_target_index(self, rear_x, rear_y, velocity):

        # To speed up nearest point search, doing it at only first time.
        if self.old_nearest_point_index is None:
            # search nearest point index
            dx = [rear_x - icx for icx in self.cx]
            dy = [rear_y - icy for icy in self.cy]
            d = np.hypot(dx, dy)
            ind = np.argmin(d)
            self.old_nearest_point_index = ind
        else:
            ind = self.old_nearest_point_index
            distance_this_index =  math.hypot(rear_x-self.cx[ind], rear_y-self.cy[ind])
            while True:
                distance_next_index = math.hypot(rear_x-self.cx[ind+1], rear_y-self.cy[ind+1])

                if distance_this_index < distance_next_index:
                    break
                ind = ind + 1 if (ind + 1) < len(self.cx) else ind
                distance_this_index = distance_next_index
            self.old_nearest_point_index = ind

        print('old_nearest_point_index is {}'.format(self.old_nearest_point_index))

        Lf = k * (20/3.6) + Lfc  # update look ahead distance
        # print(math.hypot(rear_x-self.cx[ind], rear_y-self.cy[ind]))

        # search look ahead target point index
        while Lf > math.hypot(rear_x-self.cx[ind], rear_y-self.cy[ind]):
            if (ind + 1) >= len(self.cx):
                break  # not exceed goal
            ind += 1

        return ind, Lf

def Data_reader(common_data):
    start_time = time.time() 
    print('data reader thread is running')
    x_trajec = []
    y_trajec = []
    while True:
        # network_data = ser.readline()
        if common_data['stop']:
            break
        if time.time() - start_time > 0.0333: #about 30Hz
            WB =1.57
            data, sender = sock.recvfrom(1024)
            # data = ser.readline()
            data = data.decode()
            RMC_msg =pynmea2.parse(data.split('\n')[0])
            GGA_msg =pynmea2.parse(data.split('\n')[1])

            lat = str(float(GGA_msg.lat[0:2]) + (float(GGA_msg.lat[2:9])/60))
            lon = str(float(GGA_msg.lon[0:3]) + (float(GGA_msg.lon[3:10])/60))
            # common_data['heading'] = pi_2_pi( np.radians(-float(RMC_msg.true_course) + 1.6102703428444105) )
            common_data['heading'] = pi_2_pi(np.radians(-float(RMC_msg.true_course)) + np.radians(92.0+0.06169452006880505))
            # common_data['heading'] = pi_2_pi(np.radians(float(RMC_msg.true_course)))
            common_data['x'], common_data['y'] = get_xy(float(lat), float(lon), GGA_msg.altitude)
            x_trajec.append(common_data['x'])
            y_trajec.append(common_data['y'])
            common_data['rear_x'] = common_data['x'] - ((WB / 2) * math.cos(common_data['heading']))
            common_data['rear_y'] = common_data['y'] - ((WB / 2) * math.sin(common_data['heading']))
            # print('rx is {}'.format(common_data['rear_x'] ))
            # print('ry is {}'.format(common_data['rear_y'] ))
            start_time = time.time()


    plt.subplot(212)
    plt.plot(x_trajec, y_trajec)
    
    print ('Data_reader end')

def speed_reader(common_data):
    start_time = time.time()
    while True:
        network_data = ser.readline()
        if common_data['stop']:
            break         
        if time.time() - start_time > 0.00333:
            if len(network_data) > 16:
                # print(network_data)
                common_data['v'] = int((network_data[6] + network_data[7])/10)
                # print('current_speed: {}'.format(common_data['v']))

                # print('current v is {}'.format(common_data['v']))
                start_time = time.time()


    print ('speed_reader end')


def quit_process(common_data):
    while True:
        data3 = input('quite : 0, ->')
        if float(data3) == 0:
            common_data['stop'] = True
            break      
        else:
            pass
    print ('process end')

def pure_pursuit_steer_control(rear_x, rear_y, heading, trajectory, pind, velocity):
    ind, Lf = trajectory.search_target_index(rear_x, rear_y, velocity)

    if pind >= ind:
        ind = pind

    if ind < len(trajectory.cx):
        tx = trajectory.cx[ind]
        ty = trajectory.cy[ind]
    else:  # toward goal
        tx = trajectory.cx[-1]
        ty = trajectory.cy[-1]
        ind = len(trajectory.cx) - 1

    alpha = math.atan2(ty - rear_y, tx - rear_x) - heading

    delta = math.atan2(2.0 * WB * math.sin(alpha) / Lf, 1.0)

    return delta, ind
    
def sender(common_data):
    global WB,k,Lfc,dt
    if common_data['v'] < 5:
        k = 0.1
        Lfc = 8
    elif common_data['v'] < 10:
        k = 0.2
        Lfc = 5
    elif common_data['v'] < 15:
        k = 0.3
        Lfc = 3
    else:
        k= 0.22
        Lfc = 2.2
      # look forward gain
      # [m] look-ahead distance
    dt = 0.1  # [s] time tick
    WB = 1.57  # [m] wheel base of vehicle
    

    vel = 200
    

    cte_data = []
    temp = []
    tmp = 0


    cx, cy, _ , ck , _  = make_path()
    brk = 1
    old_nearest_point_index = None
    target_course = TargetCourse(cx, cy)
    target_ind, _ = target_course.search_target_index(common_data['rear_x'],common_data['rear_y'], common_data['v'])
    

    start_time = time.time()

    while True:
        if common_data['stop']:
            break
        if time.time() - start_time > 0.0333:

            tmp  = tmp + 1

            dx = [common_data['x'] - icx for icx in cx ]
            dy = [common_data['y'] - icy for icy in cy ]

            d = [idx ** 2 + idy ** 2 for (idx, idy) in zip(dx, dy)]
            mind = min(d)
            ind = d.index(mind)
            mind = math.sqrt(mind)
            # real_mind = abs((cy[ind+1]-cy[ind])*common_data['x'] -(cx[ind+1]-cx[ind])*common_data['y'] 
            #     - (cy[ind+1]-cy[ind])*cx[ind] + (cx[ind+1]-cx[ind])*cy[ind] ) / ((cy[ind+1]-cy[ind])**2 + (cx[ind+1]-cx[ind])**2 )**0.5
            print('entire index is {} and target index is {}'.format(len(cx), ind))
            if (ind+200) > len(ck):
                vel = 0
                brk = 33
            elif ck[ind] > 0.05:
                vel = 190
            elif ck[ind] >0.1:
                vel = 180
            else:
                vel = 200

            if ind == 0:
                dir_vertor = np.array([1, 1])
                x_mid = 0.5
                y_mid = 0.5
            else:
                dir_vertor = np.array([cx[ind]-cx[ind-1], cy[ind]-cy[ind-1] ])
                x_mid = float((cx[ind]+cx[ind-1])/2)
                y_mid = float((cy[ind]+cy[ind-1])/2)
            

            error_vector = np.array([common_data['x']-x_mid, common_data['y']-y_mid])
            vec_prod = np.cross(dir_vertor, error_vector)

            if vec_prod > 0:
                cte = mind
            else:
                cte = - mind

            print('cte is {}'.format(cte))
            # print('cte coordinate : {},{}'.format(cx[ind], cy[ind]))
            cte_data.append(cte)
            temp.append(0.0333*tmp)

            delta, target_ind = pure_pursuit_steer_control(common_data['rear_x'],common_data['rear_y'],common_data['heading'],
            target_course, target_ind, common_data['v'])
            # print('current speed is {}'.format(common_data['v']))
            print('-'*30)
            delta = -np.degrees(delta)
            print('delta is {}'.format(delta))

           
            # ff =  -math.atan2(WB * ck[ind], 1)
            # ff_delta = 0.2*math.degrees(ff)



            delta = min(delta, 28)
            delta = max(delta, -28)
            delta = int(delta)
            delta *= 71
            true_degree = float(delta / 71)

            print('acutual degree : {}'.format(true_degree))

            nbits = 16
            hex_del = hex((delta + (1 << nbits)) % (1 << nbits))  
            if len(hex_del) ==5 :
                fst_steer = int("0x0" + hex_del[2:3],16)
                scd_steer = int("0x" + hex_del[3:5],16)
            elif len(hex_del) ==4 :
                fst_steer = int("0x00",16)
                scd_steer = int("0x" + hex_del[2:4],16)
            elif len(hex_del)==3 :
                fst_steer = int("0x00",16)
                scd_steer = int("0x0" + hex_del[2:3],16)
            elif len(hex_del) ==6:
                fst_steer = int("0x" + hex_del[2:4],16)
                scd_steer = int("0x" + hex_del[4:6],16)


            # # print(type(fst_steer))
            # print('f is {}, s is {}'.format(fst_steer,scd_steer))



            packet = bytearray()
            packet.append(0x53) #msg_s #변경 X
            packet.append(0x54) #msg_t #변경 X
            packet.append(0x58) #msg_x #변경 X
            packet.append(0x01) #msg_AorM #변경 X
            packet.append(0x00) #msg_Estop
            packet.append(0x00) #msg_gear
            packet.append(0x00) #msg_speed_
            packet.append(vel) #msg_speed_  0x64 : 10km/h , 0xc8 : 20km/h
            packet.append(fst_steer) #msg_steer_
            packet.append(scd_steer) #msg_steer_
            packet.append(brk) #mag_break
            packet.append(0x09) #msg_alive #변경 X
            packet.append(0x0D) #msg_etx_0 #변경 X
            packet.append(0x0A) #msg_etx_1 #변경 X

            ser.write(packet)

            start_time = time.time()

    plt.subplot(211)
    plt.plot(temp, cte_data)

    
    print ('sender end')

def main():
    stop = False
    data2, sender2 = sock.recvfrom(1024)
    data2 = data2.decode()
    GGA_msg =pynmea2.parse(data2.split('\n')[1])

    lat = str(float(GGA_msg.lat[0:2]) + (float(GGA_msg.lat[2:9])/60))
    lon = str(float(GGA_msg.lon[0:3]) + (float(GGA_msg.lon[3:10])/60))
    tmpX, tmpY= get_xy(float(lat), float(lon), GGA_msg.altitude)
    
    opti_test.make_txt(tmpX, tmpY)
    fig = plt.figure()
    plt.grid(True)
    plt.tight_layout()
    
    common_data = {'x':0.0, 'y':0.0,'heading':0.0,'v':0,'rear_x':0.0, 'rear_y':0.0, 'stop':False}
    read_thread = threading.Thread(target=Data_reader, args=(common_data,))
    send_thread = threading.Thread(target=sender, args=(common_data,))
    quit_thread = threading.Thread(target=quit_process, args=(common_data,))
    speed_thread = threading.Thread(target=speed_reader, args=(common_data,))
  
    read_thread.daemon=True
    send_thread.daemon=True 
    read_thread.start() 
    send_thread.start()
    quit_thread.start()
    speed_thread.start()

    read_thread.join()
    send_thread.join()
    
    plt.show()


if __name__ == "__main__":
    main()