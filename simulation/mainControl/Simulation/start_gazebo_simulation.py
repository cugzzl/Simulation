import json

import pymysql
from dbutils.persistent_db import PersistentDB
from dronePlan.planMain import planMain
from mainControl.Simulation.simulation_status_enum import TaskType
from mainControl.Simulation.after_simulation_handler import evaluate, save_database, save_attack_database
from mainControl.Simulation.pre_simulation_handler import get_ros_code_one, pre_handler_uav_simulation, \
    get_re_plan_algorithm_param
from mainControl.Simulation.update_simulation import save_uav_task
from mainControl.droneDao.plan_route_dao import get_uav_route
from mainControl.droneDao.plan_scout_meta_tasks_dao import get_unit_task_param, get_unit_task_param_without_db
from mainControl.droneDao.plan_attack_meta_tasks_dao import get_unit_attack_task_param
from mainControl.droneDao.scen_scenario_dao import get_constraint_and_mission_id
from mainControl.droneDao.scen_scene_dao import get_position_by_scenario_id
from mainControl.droneDao.scen_scout_target_dao import get_original_target_param
from mainControl.droneDao.scen_threat_dao import get_scen_threat_param
from mainControl.droneDao.scen_attack_target_dao import get_original_attack_target_param
from mainControl.droneDao.scen_timer_dao import get_sudden
from mainControl.droneDao.scen_uav_dao import get_id_and_position_by_category, get_uav_param, get_uav_position
from mainControl.droneDao.sim_result_dao import get_scenario_id
from mainControl.droneDao.scen_scenario_dao import get_scen_scenario
from mainControl.droneDao.scen_mission_dao import get_scen_mission, get_total_time_mission
import time as tm
import os
import copy


def start_simulation(experiment_id, start_0):
    start_time1 = tm.time()
    config = json.load(open('../config/dataBase_config.json', 'r', encoding='utf-8'))

    db_pool = PersistentDB(pymysql, **config)

    current_step = 0

    # 获得当前试验id的想定环境id
    scenario_id = get_scenario_id(db_pool, experiment_id)
    re_plan_algorithm_param = get_re_plan_algorithm_param(db_pool, scenario_id)
    mission_id = get_scen_scenario(db_pool, scenario_id)
    scene_id = get_scen_mission(db_pool, mission_id)
    total_time = get_total_time_mission(db_pool, mission_id)

    # 根据想定id获取所有的突发状况
    sudden = get_sudden(db_pool, mission_id)

    # 获取约束模板id和mission_id，并获得任务类型      TODO(发送给子路）
    # constraint_id, mission_id = get_constraint_and_mission_id(db_pool, scenario_id)
    # task_type = get_task_type(db_pool, constraint_id)

    constraint_id, mission_id = get_constraint_and_mission_id(db_pool, scenario_id)
    task_type = 1

    # 1. all_unit_task
    # 2. plan_route表存储正确
    # 3. plan_single_task正确

    # plan_main = planMain(db_pool, task_type, scenario_id, experiment_id)
    # plan_main.run()

    # 获取当前想定环境id的左下角经纬度，根据想定id和任务类型获取无人机的数量,无人机的初始位置(新生需要的)  TODO: 发布到ros总线中
    longitude, latitude = get_position_by_scenario_id(db_pool, scenario_id)
    all_uav_start_position = get_uav_position(db_pool, task_type, scenario_id)

    '''
        获取想定的参数: 无人机参数, 原始目标参数, 元任务组参数, 威胁参数
    '''
    # 无人机的静态和动态参数
    uav_static_param, uav_load, uav_max_distance, uav_distance, all_uav_speed, all_uav_id = get_uav_param(
        db_pool,
        scenario_id, task_type)
    # 元任务组的静态和动态参数
    unit_task_static_param, unit_task_work_time = get_unit_task_param(db_pool, experiment_id)
    unit_attack_task_static_param, unit_attack_task_work_time, meta_task_to_zone = get_unit_attack_task_param(db_pool,
                                                                                                              experiment_id)
    # 获取原始目标的静态和动态参数
    original_target_static_param, original_target_work_time = \
        get_original_target_param(db_pool, scene_id, experiment_id)
    # 获取威胁的参数
    all_threat = get_scen_threat_param(db_pool, mission_id)

    # 获取打击原始目标的静态和动态参数
    original_attack_target_static_param, original_attack_target_work_time, original_target_is_detected = \
        get_original_attack_target_param(db_pool, mission_id, experiment_id)

    # TODO: 从任务规划模块直接获得输出
    # static_unit_task, unit_task_work_time, num_unit_task_of_zone = get_unit_task_param_without_db(all_unit_task)
    # original_target_static_param, original_target_work_time = get_original_target_param(db_pool, scenario_id, num_unit_task_of_zone)

    # 任务规划完成之后:无人机准备起飞.
    #   获取所有无人机的：
    #   1. 指令格式2: 所有无人机的路径      TODO
    #   2. 每一个任务目标的位置
    #   3. 每一个任务的工作时间
    #   4. 指令格式3： 无人机起飞指令       TODO
    #   5. 无人机仿真ip和无人机id的反射

    second_ros_code, all_task_id, all_task_start_flag, \
    all_task_position, all_task_work_time, third_ros_code, uav_ip_to_id, all_task_profit = \
        pre_handler_uav_simulation(db_pool, experiment_id, all_uav_speed)
    all_uav_route = get_uav_route(db_pool, experiment_id, current_step)

    uav_num = len(uav_ip_to_id)
    # 指令格式1: 无人机数量和无人机基地经纬度     TODO    ROS总线
    first_ros_code = get_ros_code_one(uav_num, longitude, latitude)

    # 无人机实时状态、元任务组实时状态、触发事件、触发事件参数、目标实例状态、原始目标状态
    pre_time = tm.time() - start_time1
    print('仿真准备时间：', pre_time)
    dynamic_target_work_time = copy.deepcopy(original_target_work_time)
    dynamic_uav_load = copy.deepcopy(uav_load)

    os.system("sh ~/version/5.7/uav/auto.sh %s" % start_0[1])

    # 开始仿真
    print('仿真开始')
    current_step, running_time, shared_uav_status, \
    shared_unit_task, shared_original_target, \
    shared_event, shard_original_attack_target, shared_threat_status = save_uav_task(sudden, task_type, current_step,
                                                                                     experiment_id,
                                                                                     uav_static_param, dynamic_uav_load,
                                                                                     unit_task_static_param,
                                                                                     unit_task_work_time,
                                                                                     original_target_static_param,
                                                                                     dynamic_target_work_time,
                                                                                     all_threat,
                                                                                     all_task_id, all_task_position,
                                                                                     all_task_work_time,
                                                                                     all_task_start_flag,
                                                                                     uav_ip_to_id, all_uav_route,
                                                                                     all_uav_speed, uav_distance,
                                                                                     uav_max_distance,
                                                                                     all_uav_start_position, total_time,
                                                                                     all_task_profit, re_plan_algorithm_param,
                                                                                     unit_attack_task_static_param,
                                                                                     unit_attack_task_work_time,
                                                                                     meta_task_to_zone,
                                                                                     original_attack_target_static_param,
                                                                                     original_attack_target_work_time,
                                                                                     original_target_is_detected)

    print('仿真运行时间：', running_time, ",运行步长：", current_step)
    save_start_time = tm.time()
    # 将仿真过程中的无人机、原始目标状态存入数据库中
    save_database(db_pool, shared_uav_status, shared_original_target, shared_event,
                  shard_original_attack_target, shared_threat_status)
    save_time = tm.time() - save_start_time
    print('数据保存时间：', save_time)

    #     通过原始目标状态计算任务完成率和任务收益（初始状态->终止状态）
    # success_rate, all_profit, zone_completion_rate = evaluate(current_step - 1, experiment_id,
    #                                                          original_target_work_time,
    #                                                         db_pool)


def attack_simulation(experiment_id, start_0):
    start_time1 = tm.time()
    config = json.load(open('../config/dataBase_config.json', 'r', encoding='utf-8'))
    db_pool = PersistentDB(pymysql, **config)

    current_step = 0
    # 获得当前试验id的想定环境id
    scenario_id = get_scenario_id(db_pool, experiment_id)
    re_plan_algorithm_param = get_re_plan_algorithm_param(db_pool, scenario_id)
    mission_id = get_scen_scenario(db_pool, scenario_id)
    total_time = get_total_time_mission(db_pool, mission_id)

    # 根据想定id获取所有的突发状况
    sudden = get_sudden(db_pool, mission_id)

    # constraint_id, mission_id = get_constraint_and_mission_id(db_pool, scenario_id)
    task_type = 2
    # task_type = get_task_type(db_pool, constraint_id)

    # plan_main = planMain(db_pool, task_type, scenario_id, experiment_id)
    # plan_main.run()

    # 获取当前想定环境id的左下角经纬度，根据想定id和任务类型获取无人机的数量,无人机的初始位置(新生需要的)  TODO: 发布到ros总线中
    longitude, latitude = get_position_by_scenario_id(db_pool, scenario_id)
    all_uav_start_position = get_uav_position(db_pool, task_type, scenario_id)

    # 无人机的静态和动态参数
    uav_static_param, uav_load, uav_max_distance, uav_distance, all_uav_speed, all_uav_id = get_uav_param(
        db_pool,
        scenario_id, task_type)
    # 元任务组的静态和动态参数
    unit_task_static_param, unit_task_work_time, meta_task_to_zone = get_unit_attack_task_param(db_pool, experiment_id)
    # 获取原始目标的静态和动态参数
    original_target_static_param, original_target_work_time, original_target_is_detected = \
        get_original_attack_target_param(db_pool, mission_id, experiment_id)
    # 获取威胁的参数
    all_threat = get_scen_threat_param(db_pool, mission_id)

    # TODO: 从任务规划模块直接获得输出
    # static_unit_task, unit_task_work_time, num_unit_task_of_zone = get_unit_task_param_without_db(all_unit_task)
    # original_target_static_param, original_target_work_time = get_original_target_param(db_pool, scenario_id, num_unit_task_of_zone)

    second_ros_code, all_task_id, all_task_start_flag, \
    all_task_position, all_task_work_time, third_ros_code, uav_ip_to_id, all_task_profit = \
        pre_handler_uav_simulation(db_pool, experiment_id, all_uav_speed)
    all_uav_route = get_uav_route(db_pool, experiment_id, current_step)

    uav_num = len(uav_ip_to_id)
    # 指令格式1: 无人机数量和无人机基地经纬度     TODO    ROS总线
    first_ros_code = get_ros_code_one(uav_num, longitude, latitude)

    pre_time = tm.time() - start_time1
    print('仿真准备时间：', pre_time)

    dynamic_target_work_time = copy.deepcopy(original_target_work_time)
    dynamic_uav_load = copy.deepcopy(uav_load)

    # # 开始仿真
    os.system("sh ~/version/5.5/uav/auto.sh %s" % start_0[1])
    print('仿真开始')

    current_step, running_time, shared_uav_status, \
    shared_unit_task, shared_original_target, \
    shared_event, shard_original_attack_target, shared_threat_status = save_uav_task(sudden, task_type, current_step,
                                                                                     experiment_id,
                                                                                     uav_static_param, dynamic_uav_load,
                                                                                     unit_task_static_param,
                                                                                     unit_task_work_time,
                                                                                     original_target_static_param,
                                                                                     dynamic_target_work_time,
                                                                                     all_threat,
                                                                                     all_task_id, all_task_position,
                                                                                     all_task_work_time,
                                                                                     all_task_start_flag,
                                                                                     uav_ip_to_id, all_uav_route,
                                                                                     all_uav_speed, uav_distance,
                                                                                     uav_max_distance,
                                                                                     all_uav_start_position, total_time,
                                                                                     all_task_profit, re_plan_algorithm_param)

    print('仿真运行时间：', running_time, ",运行步长：", current_step)
    save_start_time = tm.time()
    # 将仿真过程中的无人机、原始目标状态存入数据库中
    save_attack_database(db_pool, shared_uav_status, shared_original_target,
                         shared_event, shared_threat_status, TaskType.ATTACK.value)
    save_time = tm.time() - save_start_time
    print('数据保存时间：', save_time)

    #     通过原始目标状态计算任务完成率和任务收益（初始状态->终止状态）
    # success_rate, all_profit, zone_completion_rate = evaluate(current_step - 1, experiment_id,
    #                                                           original_target_work_time,
    #                                                           db_pool)
