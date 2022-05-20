import copy
import json
import websockets
import time as tm
from droneDao.plan_attack_meta_tasks_dao import read_map
from mainControl.Simulation.do_action import uav_action_handler
from mainControl.Simulation.re_plan_handler import get_re_plan_data, re_plan_data_to_ros
from mainControl.Simulation.simulation_utils import filter_current_model, filter_current_unit_task, get_kind_sudden, \
    update_by_event, get_init_model, get_changed_unit_task
from mainControl.Simulation.re_plan_simulation import sudden_handler, supper_over_time_simulation
from mainControl.Simulation.save_socket_status import socket_save_target_status, socket_save_uav_status, \
    socket_save_current_status, socket_save_attack_target_status
from mainControl.Simulation.simulation_status_enum import Sudden, Event, IsDetected, TaskType

# import rospy
# from std_msgs.msg import String  # 消息头文件


terminate_command = '0'
websocket = ''
all_uav_status_ = '[[0, [650,650,500], [100, 100, 100,100], 2, 10], [1, [650,650,500], [100, 100, 100,100], 2, 10]]'


# all_uav_status_ = ''


#  获取无人机实时状态： id, position, orientation
def uav_status_callback(data):
    global all_uav_status_
    all_uav_status_ = data.data


# 接收指令信息，判断仿真是否结束
def command_callback(data):
    global terminate_command
    terminate_command = data.data


def save_uav_task(sudden, task_type, current_step, experiment_id,
                  uav_static_param, uav_load,
                  unit_task_static_param, unit_task_current_shoot,
                  original_target_static_param, original_target_work_time,
                  all_threat,
                  all_task_id, all_task_position, all_task_cost, all_task_start_flag,
                  uav_ip_to_id, all_uav_route,
                  uav_speed, all_uav_distance, all_uav_max_distance, all_uav_start_position,
                  total_time, all_task_profit, re_plan_algorithm_param,
                  unit_attack_task_static_param=None, unit_attack_task_work_time=None, meta_task_to_zone=None,
                  original_attack_target_static_param=None, original_attack_target_work_time=None,
                  original_target_is_detected=None
                  ):
    """

    :param all_uav_route:
    :param all_uav_start_position:
    :param all_task_profit:
    :param total_time:
    :param all_uav_max_distance:
    :param all_uav_distance:
    :param uav_speed:
    :param all_task_start_flag:
    :param all_task_id:
    :param uav_ip_to_id:
    :param all_threat: 所有的威胁
    :param task_type: 任务类型
    :param sudden: 突发事件
    :param current_step: 当前步长
    :param experiment_id: 试验id
    :param uav_static_param: 无人机静态参数
    :param uav_load: 无人机当前载荷
    :param unit_task_static_param: 元任务组静态参数
    :param unit_task_current_shoot: 元任务组当前余量
    :param original_target_static_param: 原始目标静态参数
    :param original_target_work_time: 原始目标当前余量
    :param shared_uav_status: 进程共享无人机参数
    :param shared_unit_task: 进程共享元任务组参数
    :param shared_original_target: 进程共享原始目标区参数
    :param shared_event: 进程共享事件
    :param shared_event_param: 进程共享事件参数
    :param all_task_cost: 每一个任务的工作时间
    :param all_task_position: 每个任务的坐标
    :return:
    """
    # TODO: 初始化ROS订阅发布
    """
        订阅消息： 1. 无人机实时位置信息
                 2，仿真是否结束
        发布消息： 1. 可视化信息
                 2. 重规划信息
    """
    # rospy.Subscriber("return_pose", String, uav_status_callback)
    # while all_uav_status_ == '':
    #       continue
    # rospy.Subscriber('return_complete', String, command_callback)
    # view_pub = rospy.Publisher('view_data', String, queue_size=10)
    # re_plan_pub = rospy.Publisher('re_plan_start', String, queue_size=10)

    # 得到所有的目标突发状况, 目标突发类型为1
    all_target_sudden = get_kind_sudden(sudden, Sudden.TARGET.value)
    # 得到所有的无人机突发状况，突发类型为0
    all_uav_sudden = get_kind_sudden(sudden, Sudden.UAV.value)
    # 得到所有的威胁突发状况,突发类型为2
    all_threat_sudden = get_kind_sudden(sudden, Sudden.THREATEN.value)

    """
    在同一个步长内，需要去判断是否无人机攻击事件，如果发生了，则进行目标掉血事件，
    但是在无人机攻击和目标掉血事件中间应该是隔了好几个步长的，不是在同一个步长内更新掉血事件.
    因此需要在当前步长内，将下几个步长将要发生的事件缓存起来，当到达指定步长时，再更新目标.
    需要确定的东西：哪一个step中，哪一个id的目标，掉几滴血.
    数据结构形式：当步长为3时，id为0的目标掉两滴血，id为1的目标掉1滴血，id为2的目标掉1滴血；
                当步长为4时，id为0的目标掉1滴血，id为1的目标掉2滴血，id为2的目标掉3滴血
    a = {3: {0: 2,
             1: 1,
             2: 1},
         4: {0: 1,
             1: 2,
             2: 3},
         5: {0: 1,
             1: 2,
             2: 1}
         }
    """
    unit_task_ahead_event = {}
    original_target_ahead_event = {}
    action_ahead_event = {}

    current_static_uav, current_threat = [], []
    pre_step_uav_status, pre_step_original_target_status, pre_step_unit_task_status = [], [], []

    # 得到step为1时，应该存在的元任务组和原始目标
    current_static_original_target, current_target_id = get_init_model(original_target_static_param,
                                                                       all_target_sudden, current_step)
    current_static_unit_task, current_unit_task_id = get_init_model(unit_task_static_param,
                                                                    all_target_sudden, current_step)

    shared_uav_status = []
    shared_unit_task = []
    shared_original_target = []
    shared_event = []
    shard_original_attack_target = []
    all_original_attack_target_status = []
    shared_threat_status = []
    socket_attack_target_status = None

    config_param = json.load(open('../config/simulation_config.json', 'r', encoding='utf-8'))
    prediction_time = config_param.get('prediction_time')
    step = config_param.get('step')
    uav_height = config_param.get('uav_height')
    map_accuracy = config_param.get('map_accuracy')
    dem_accuracy = config_param.get('dem_accuracy')

    map_list = read_map('testread.txt')
    task_algorithm_param_list = []
    start_time = tm.time()

    while True:
        current_time = tm.time()
        # 如果仿真结束，则中断进程 TODO: 使用kill杀死进程
        if terminate_command == 'complete':
            break

        if current_time - start_time > total_time:
            break

        if current_step == 11:
            break

        gazebo_uav_status = eval(all_uav_status_)
        # 如果当前还没有收到ros传递的信息
        if len(gazebo_uav_status) == 0:
            continue

        # 当前step会发生的事件，用以广播
        current_event = []

        # 对目标掉血事件，进行更新
        # 如果当前step存在元任务组掉血事件（元任务组掉血事件不在可视化端进行展示）
        update_by_event(unit_task_ahead_event, current_step, task_type,
                        event_type_id=-1, dynamic_shoot=unit_task_current_shoot,
                        current_event=None)

        # 如果当前step存在爆炸事件
        update_by_event(action_ahead_event, current_step, task_type,
                        event_type_id=Event.BOOM.value, dynamic_shoot=None,
                        current_event=current_event)

        # 如果当前step存在原始目标掉血事件
        update_by_event(original_target_ahead_event, current_step,
                        task_type, event_type_id=Event.ORIGINAL_TARGET.value, dynamic_shoot=original_target_work_time,
                        current_event=current_event)

        # 监听突发事件，若发生突发事件，进入任务重规划模块
        # 具体方案：根据前一个步长和当前步长所过滤得到的模型size，判断是否有新增或者减少
        target_sudden_flag, uav_sudden_flag, threat_sudden_flag = False, False, False
        num_pre_step_static_unit_task = len(current_static_unit_task)
        num_pre_step_static_uav = len(current_static_uav)
        num_pre_step_threat = len(current_threat)

        if task_type == TaskType.ATTACK.value:
            # 根据目标突发状况，对当前元任务组进行更新, 得到当前应该存在的元任务组（此时元任务组仅包含静态参数，缺少当前血量值）
            current_static_original_target, current_target_id = filter_current_model(all_target_sudden,
                                                                                     original_target_static_param,
                                                                                     current_step, experiment_id)
            # 根据当前应该存在的原始目标，得到当前应当存在的元任务组
            current_static_unit_task, current_unit_task_id = filter_current_model(all_target_sudden,
                                                                                  unit_task_static_param,
                                                                                  current_step, experiment_id)
        # 根据无人机突发状况,对当前无人机进行更新,得到当前step中应当存在的无人机
        current_static_uav, current_uav_id = filter_current_model(all_uav_sudden, uav_static_param,
                                                                  current_step, experiment_id)
        # 根据威胁突发状况,对当前威胁进行更新,得到当前step中应当存在的威胁
        current_threat = filter_current_model(all_threat_sudden, all_threat,
                                              current_step, experiment_id)[0]

        # 判断是否发生突发状况
        if num_pre_step_static_unit_task != len(current_static_unit_task):
            target_sudden_flag = True
        if num_pre_step_static_uav != len(current_static_uav):
            uav_sudden_flag = True
        if num_pre_step_threat != len(current_threat):
            threat_sudden_flag = True

        # 如果发生任意一种突发事件
        if current_step == 1 or (current_step > 0 and (target_sudden_flag or uav_sudden_flag or threat_sudden_flag)):
            # 对各种类型的突发状况进行处理, 得到当前所有模型的态势
            current_uav_status, current_original_target_status, current_unit_task_status, current_threat, uav_next_point = \
                sudden_handler(experiment_id, current_step,
                               target_sudden_flag, uav_sudden_flag, threat_sudden_flag,
                               gazebo_uav_status, pre_step_uav_status, current_uav_id,
                               pre_step_original_target_status,
                               original_target_static_param, original_target_work_time,
                               pre_step_unit_task_status,
                               unit_task_static_param, unit_task_current_shoot,
                               current_threat,
                               current_target_id, current_unit_task_id)

            # 对当前数据进行深拷贝
            re_current_uav_status = copy.deepcopy(current_uav_status)
            re_all_task_position = copy.deepcopy(all_task_position)
            re_all_task_cost = copy.deepcopy(all_task_cost)
            re_all_task_id = copy.deepcopy(all_task_id)
            re_all_task_start_flag = copy.deepcopy(all_task_start_flag)
            re_current_unit_task_status = copy.deepcopy(current_unit_task_status)
            re_current_original_target_status = copy.deepcopy(current_original_target_status)

            #   得到10s内所有模型的态势 TODO: 黄子路
            re_all_uav_load, re_plan_uav_max_distance, \
            re_all_uav_position = supper_over_time_simulation(experiment_id, task_type, current_step,
                                                              prediction_time, step,
                                                              uav_static_param, re_current_uav_status,
                                                              uav_speed, all_uav_route, all_uav_start_position,
                                                              re_current_unit_task_status,
                                                              re_current_original_target_status,
                                                              re_all_task_position, re_all_task_cost,
                                                              re_all_task_id, re_all_task_start_flag,
                                                              map_list, current_threat)

            #   找到变换的元任务组
            missed_task, add_task = None, None
            if task_type == TaskType.ATTACK.value:
                missed_task, add_task = get_changed_unit_task(unit_task_static_param, unit_task_current_shoot,
                                                              pre_step_unit_task_status, current_unit_task_id)

            #   对数据进行封装 TODO: 缺少task_type, task_algorithm_param_list
            uav_num, task_num, all_target_lists, uav_speed_list, \
            uav_flight_distance_list, uav_load_list, \
            current_position_list, assign_list, new_task = get_re_plan_data(current_uav_status, task_type,
                                                                            re_all_task_position, re_all_task_cost,
                                                                            all_task_profit, re_all_task_id,
                                                                            uav_speed, re_plan_uav_max_distance,
                                                                            re_all_uav_load, re_all_uav_position,
                                                                            missed_task, add_task)
            time_lim = total_time - current_time
            message = re_plan_data_to_ros(uav_num, task_num, all_target_lists, uav_speed_list,
                                          uav_flight_distance_list, time_lim, task_type, uav_load_list,
                                          task_algorithm_param_list, current_position_list, assign_list, new_task,
                                          current_threat, experiment_id, re_plan_algorithm_param)

            #  通过ros发送数据 TODO： 发布任务重规划数据
            # re_plan_pub.publish(message)

        # 存储当前step下所有的元任务组状态
        all_unit_task = copy.deepcopy(current_static_unit_task)
        for unit_task in all_unit_task:
            unit_task_id = unit_task[0]
            unit_task.append(unit_task_current_shoot.get(unit_task_id))
        pre_step_unit_task_status = all_unit_task

        # 保存原始目标区域至socket变量
        all_original_target_status, shared_all_original_target = get_all_original_target_status(
            current_static_original_target, original_target_work_time, current_step, experiment_id)
        socket_all_zone_status = socket_save_target_status(current_static_original_target, original_target_work_time)
        pre_step_original_target_status = all_original_target_status

        # 3. 无人机动作事件
        # current_all_uav_status 包含了action_status和next_point的状态
        shared_current_uav_status, current_all_uav_status = \
            uav_action_handler(experiment_id, task_type, current_step,
                               gazebo_uav_status, uav_static_param, uav_load,
                               all_task_id, all_task_position, all_task_cost, all_task_start_flag,
                               shared_event,
                               current_static_unit_task,
                               unit_task_ahead_event, original_target_ahead_event, current_event,
                               action_ahead_event,
                               uav_ip_to_id,
                               uav_speed, all_uav_distance, all_uav_max_distance,
                               uav_height, map_accuracy, dem_accuracy)
        socket_all_uav_status = socket_save_uav_status(shared_current_uav_status, uav_load)
        pre_step_uav_status = current_all_uav_status

        # 在侦察任务中更新打击目标的状态
        if task_type == TaskType.SCOUT.value:
            get_original_attack_target_status(all_unit_task, meta_task_to_zone,
                                              original_target_is_detected
                                              )
            all_original_attack_target_status = get_all_original_attack_target_status(
                original_attack_target_static_param,
                original_attack_target_work_time,
                original_target_is_detected,
                current_step, experiment_id)
            socket_attack_target_status = socket_save_attack_target_status(all_original_attack_target_status,
                                                                           original_target_is_detected)

        # 4.向可视化端口发送无人机实时状态，目标区实时状态，当前事件
        # 当前step状态下需要发给可视化的所有状态
        if task_type == TaskType.ATTACK.value:
            socket_current_status = \
                socket_save_current_status(socket_all_uav_status,
                                           socket_all_zone_status,
                                           current_event, current_step)
        else:
            socket_current_status = \
                socket_save_current_status(socket_all_uav_status,
                                           socket_all_zone_status,
                                           current_event, current_step, socket_attack_target_status)

        # message = str(socket_current_status)  TODO: 通过ros发布至可视化端
        # view_pub.publish(message)

        # 5. 缓存无人机、元任务组、目标区、威胁实时状态
        shared_uav_status.append(shared_current_uav_status)
        # shared_unit_task.append(all_unit_task)
        shared_original_target.append(shared_all_original_target)
        shared_threat_status.append(current_threat)

        if task_type == TaskType.SCOUT.value:
            shard_original_attack_target.append(all_original_attack_target_status)

        current_step += step
        one_loop_time = tm.time()
        cost_time = one_loop_time - current_time
        if cost_time < step:
            tm.sleep(step - cost_time)

    end_time = tm.time()

    return current_step, end_time - start_time, shared_uav_status, \
           shared_unit_task, shared_original_target, shared_event, shard_original_attack_target, shared_threat_status


def get_all_original_target_status(static_original_target, original_target_work_time,
                                   current_step, experiment_id):
    """

    :param static_original_target: 原始目标的静态参数
    :param original_target_work_time: 当前step所有原始目标的状态
    :param current_step: 当前步长
    :param experiment_id: 试验id
    :return: 可视化端需要的原始目标数据，数据库端需要的原始目标数据
    """

    all_original_target = []
    shared_original_target = []
    for result in static_original_target:
        tmp = []
        original_target_param = result
        zone_id = original_target_param[0]
        zone_name = original_target_param[1]
        zone_type = original_target_param[2]
        zone_position = original_target_param[3]
        zone_profit = original_target_param[4]
        tmp.append(zone_id)
        tmp.append(zone_name)
        tmp.append(zone_type)
        tmp.append(zone_position)
        tmp.append(zone_profit)
        tmp.append(original_target_work_time.get(zone_id))
        all_original_target.append(tmp)
        shared_tmp = copy.deepcopy(tmp)
        shared_tmp.append(experiment_id)
        shared_tmp.append(current_step)
        shared_original_target.append(shared_tmp)

    return all_original_target, shared_original_target


def get_all_original_attack_target_status(static_original_target, original_target_work_time,
                                          original_target_is_detected,
                                          current_step, experiment_id):
    """

    :param static_original_target: 原始目标的静态参数
    :param original_target_work_time: 当前step所有原始目标的状态
    :param current_step: 当前步长
    :param experiment_id: 试验id
    :return: 可视化端需要的原始目标数据，数据库端需要的原始目标数据
    """

    all_original_target = []
    for result in static_original_target:
        tmp = []
        original_target_param = static_original_target.get(result)
        zone_id = original_target_param[0]
        zone_name = original_target_param[1]
        zone_type = original_target_param[2]
        zone_position = original_target_param[3]
        zone_profit = original_target_param[4]
        tmp.append(zone_id)
        tmp.append(zone_name)
        tmp.append(zone_type)
        tmp.append(zone_position)
        tmp.append(zone_profit)
        tmp.append(experiment_id)
        tmp.append(current_step)
        tmp.append(original_target_work_time.get(zone_id))
        tmp.append(original_target_is_detected.get(zone_id))

        all_original_target.append(tmp)

    return all_original_target


# 获取socket连接
def get_websocket():
    global websocket
    host = '127.0.0.1'
    port = '8999'
    address = host.__add__(':').__add__(port)
    websocket = websockets.connect("ws://127.0.0.1:8999")
    return websocket


def get_original_attack_target_status(all_unit_task, meta_task_to_zone,
                                      original_target_is_detected
                                      ):
    for unit_task in all_unit_task:
        meta_task_id = unit_task[0]
        work_time = unit_task[4]
        if work_time == 0:
            zone_id = meta_task_to_zone.get(meta_task_id)
            if original_target_is_detected.get(zone_id) == IsDetected.No.value:
                original_target_is_detected.update({zone_id: IsDetected.YES.value})
