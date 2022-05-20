import json

import pymysql
import rospy  # ros在python语言中的头文件
from dbutils.persistent_db import PersistentDB
from std_msgs.msg import String  # 消息头文件

from mainControl.Simulation.re_plan_handler import get_re_plan_algorithm_param
from mainControl.Simulation.simulation_status_enum import AlgorithmTypeId
from mainControl.droneDao.sim_result_dao import get_scenario_id

message = ''


def callback(data):
    global message
    message = data.data


if __name__ == '__main__':

    config = json.load(open('../config/dataBase_config.json', 'r', encoding='utf-8'))
    db_pool = PersistentDB(pymysql, **config)

    # 接收任务重规划参数，进行任务重规划
    rospy.init_node('re_plan')
    rospy.Subscriber('re_plan_start', String, callback)
    while message == '':
        continue
    re_plan_message = eval(message)

    experiment_id = re_plan_message.get('experiment_id')
    uav_num = re_plan_message.get('uav_num')
    target_num = re_plan_message.get('target_num')
    all_target_lists = re_plan_message.get('all_target_lists')
    uav_speed_list = re_plan_message.get('uav_speed_list')
    uav_flight_distance_list = re_plan_message.get('uav_flight_distance_list')
    time_lim = re_plan_message.get('time_lim')
    task_type = re_plan_message.get('task_type')
    uav_load_list = re_plan_message.get('uav_load_list')
    task_algorithm_param_list = re_plan_message.get('task_algorithm_param_list')
    current_position_list = re_plan_message.get('current_position_list')
    assign_list = re_plan_message.get('assign_list')
    new_task = re_plan_message.get('new_task')
    current_threat = re_plan_message.get('current_threat')
    re_plan_algorithm_param = re_plan_message.get('re_plan_algorithm_param')
    # 获取任务重分配和航迹重规划算法的id和参数
    task_algorithm_param = re_plan_algorithm_param[0]
    path_algorithm_param = re_plan_algorithm_param[1]

    # 将数据发送至重规划框架 TODO

    for task_id in task_algorithm_param:
        if task_id == AlgorithmTypeId.GA_TASK.value:
            # 调用重分配算法
            pass

    for path_id in path_algorithm_param:
        if path_id == AlgorithmTypeId.GA_PATH:
            # 调用遗传算法
            pass
        elif path_id == AlgorithmTypeId.ACO_PATH:
            # 调用蚁群算法
            pass
        elif path_id == AlgorithmTypeId.PSO_PATH:
            # 调用粒子群算法
            pass
        else:
            print('算法id错误')
