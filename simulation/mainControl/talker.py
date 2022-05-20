# -*- coding=utf-8 -*-
import pymysql
from dbutils.persistent_db import PersistentDB


from mainControl.Simulation.pre_simulation_handler import get_ros_code_one, pre_handler_uav_simulation
from mainControl.droneDao.plan_scout_meta_tasks_dao import get_unit_task_param, get_unit_task_param_without_db
from mainControl.droneDao.scen_scenario_dao import get_constraint_and_mission_id
from mainControl.droneDao.scen_scene_dao import get_position_by_scenario_id
from mainControl.droneDao.scen_scout_target_dao import get_original_target_param
from mainControl.droneDao.scen_sudden_dao import get_sudden
from mainControl.droneDao.scen_threat_dao import get_scen_threat_param
from mainControl.droneDao.scen_uav_dao import get_id_and_position_by_category, get_uav_param
from mainControl.droneDao.sim_result_dao import get_scenario_id
import time as tm
from mainControl.Simulation.simulation_utils import get_uav_source
import rospy  # ros在python语言中的头文件
from std_msgs.msg import String  # 消息头文件
import os

cs = ''


def talker():
    for i in range(10):  # 1
        # while(1):
        pub.publish(str(cs))
        rate.sleep()
    init_sign = 0

    print('continue')

    for i in range(1):  # chushi
        for j in range(5):
            hello_str = "%s" % all_uav_start_position
            init_wz.publish(hello_str)  # 发布字符串
            rate.sleep()  # 配合发布频率的休眠

    for i in range(1):  # 2
        for j in range(len(second_ros_code)):
            hello_str = "%s" % second_ros_code[j]
            pub.publish(hello_str)  # 发布字符串
            rate.sleep()  # 配合发布频率的休眠

    for i in range(1):  # 3
        for j in range(len(third_ros_code)):
            hello_str = "%s" % third_ros_code[j]
            # rospy.loginfo(hello_str)  # 写入log日志   print
            pub.publish(hello_str)  # 发布字符串
            rate.sleep()  # 配合发布频率的休眠


if __name__ == '__main__':
    pub = rospy.Publisher('simulation', String, queue_size=10)  # 发布消息到话题 chatter 中,队列长度10
    init_wz = rospy.Publisher('chushizhi', String, queue_size=10)  # 发布消息到话题 chatter 中,队列长度10
    rospy.init_node('talker', anonymous=True)  # 初始化节点名字为talker,加入一个随机数使得节点名称唯一

    rate = rospy.Rate(2)  # 10hz  设置发布频率

    start_time1 = tm.time()

    config = {
        'host': '58.45.191.73',
        'port': 9123,
        'database': 'drone',
        'user': 'drone',
        'password': 'abc123.',
        'charset': 'utf8mb4'
    }

    db_pool = PersistentDB(pymysql, **config)

    current_step = 0
    experiment_id = 201

    # 获得当前试验id的想定环境id
    scenario_id = get_scenario_id(db_pool, experiment_id)

    task_type = 1
    # task_type = get_task_type(db_pool, constraint_id)

    # 获取当前想定环境id的左下角经纬度，根据想定id和任务类型获取无人机的数量,无人机的初始位置(新生需要的)  TODO: 发布到ros总线中
    longitude, latitude = get_position_by_scenario_id(db_pool, scenario_id)
    uav_num, all_uav_start_position = get_id_and_position_by_category(db_pool, task_type, scenario_id)

    # 指令格式1: 无人机数量和无人机基地经纬度     TODO    ROS总线
    first_ros_code = get_ros_code_one(uav_num, longitude, latitude)

    '''
        获取想定的参数: 无人机参数, 原始目标参数, 元任务组参数, 威胁参数
    '''
    # 无人机的静态和动态参数
    uav_static_param, uav_load, uav_max_distance, uav_distance, all_uav_speed, all_uav_id = get_uav_param(
        db_pool,
        scenario_id, task_type)

    second_ros_code, all_task_id, all_task_start_flag, \
    all_task_position, all_task_work_time, third_ros_code, uav_ip_to_id, all_task_profit = \
        pre_handler_uav_simulation(db_pool, experiment_id, all_uav_speed)

    cs = first_ros_code

    rospy.loginfo(str(cs))  # 写入log日志

    try:
        while (1):
            talker()
    except rospy.ROSInterruptException:
        pass
