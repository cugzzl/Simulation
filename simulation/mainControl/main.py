# -*- coding=utf-8 -*-
import sys
import rospy  # ros在python语言中的头文件
from std_msgs.msg import String  # 消息头文件
import os
import re

from mainControl.Simulation.start_gazebo_simulation import start_simulation

start='[9,9,9,9,9]'
start_sign=1
start_0=[9,9,9,9,9]
cs=''
def callback(data):  #开始仿真
    global start
    start=str(data.data)
    #print(start)


if __name__ == '__main__':

    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber('simulation', String, callback)
    while(start_sign==1):
        #rate=rospy.Rate(10)
        start_0=[int(float(s)) for s in re.findall("\d+\.?\d*",str(start))]
        if start_0[0]==1 and start_sign==1:
            #print(start_sign)
            start_sign=0
    # 从唐总获得试验id
    # experiment_id = sys.argv[0]
    experiment_id = 101
    start_simulation(experiment_id, start_0[1])

