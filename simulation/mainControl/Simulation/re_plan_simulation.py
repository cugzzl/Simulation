import copy

from mainControl.Simulation.simulation_utils import update_by_event
from mainControl.Simulation.re_plan_do_action import re_plan_uav_action
from mainControl.Simulation.simulation_status_enum import UavStatus, Event

# 任务重规划模块


"""

    当前突发状况只能为一种 TODO
    触发任务重规划的机制：
        1. 无人机坠毁
        2. 新增目标、目标消失
        3. 新增威胁

    进入任务重规划,需要得到当前step下:
        1. 所有无人机的态势 ( 上一个step中所有无人机的态势 +/-当前step中新增(减少)的无人机的态势)
            1.1. 无人机所在的位置: all_uav_status
            1.2. 无人机所剩弹药
            1.3. 无人机所剩最大飞行距离
        2. 原始目标态势 ( 上一个step中所有目标的态势 +/-当前step中新增(减少)的目标的态势)
            2.1 原始目标所在位置
            2.2 原始目标所需要的弹药量
            2.3 原始目标收益
        3. 威胁态势 (当前step中的威胁)
            3.1 威胁所在位置
            3.2 威胁半径
            3.3 关联的侦察元任务组id

        4.  无人机的任务完成状态（每一架无人机剩下的任务id，
                             剩下的任务位置以及在每一个任务位置上的投弹量）
"""

"""
    假定任务重规划算法运行事件为10s，在任务重规划阶段需要完成的事情：
        1. 在尽可能短的时间内完成（超前仿真）
            1.1. 计算并保存接下来10s内发生的：无人机、原始目标的态势，事件
            1.2. 计算10s后，无人机、原始目标、威胁态势，作为算法的输入
        2. 运行任务重规划算法，重新得到无人机的路径，生成新的作战指令
        3. 通过ros发布新的作战指令，无人机按照新的指令飞行
"""


def sudden_handler(experiment_id, current_step,
                   target_sudden_flag, uav_sudden_flag, threat_sudden_flag,
                   gazebo_uav_status, pre_step_uav_status, current_uav_id,
                   pre_step_original_target_status,
                   original_target_param, original_target_work_time,
                   pre_step_unit_task_status,
                   unit_task_static_param, unit_task_current_shoot,
                   current_threat,
                   current_target_id, current_unit_task_id):
    """

    :param pre_step_uav_status: 上一个步长中所有存在的无人机的状态
    :param current_uav_id: 本步长中应当存在的无人机id
    :param pre_step_original_target_status: 上一个步长中所有存在的原始目标状态
    :param current_target_id: 本步长中应当存在的原始目标id
    :param original_target_param: 所有目标的静态参数
    :param original_target_work_time: 所有目标的动态参数
    :param current_threat: 当前应当存在的威胁
    :return:
    """
    # 若发生目标突发事件
    # 立即生效，但是在超前仿真中不会影响到其他模型，只是作为后续算法的输入
    current_original_target_status = get_current_target(experiment_id, current_step, current_target_id,
                                                        target_sudden_flag, pre_step_original_target_status,
                                                        original_target_param, original_target_work_time)
    current_unit_task_status = get_current_target(experiment_id, current_step, current_unit_task_id,
                                                  target_sudden_flag, pre_step_unit_task_status,
                                                  unit_task_static_param, unit_task_current_shoot)

    # 获得每一架无人机所当前已完成多少个航迹点
    uav_next_point = get_next_uav_point(gazebo_uav_status)

    # 若发生威胁突发事件
    # 立即生效，但是在超前仿真中不会影响到其他模型，只是作为后续算法的输入
    if threat_sudden_flag:
        # 威胁新增，则目标和无人机的态势不做任何变化
        return pre_step_uav_status, current_original_target_status, \
               current_unit_task_status, current_threat, uav_next_point

    # 若发生无人机突发事件
    # 更新当前状态下的无人机态势，立即生效，影响超前仿真
    current_uav_status = []
    if uav_sudden_flag:
        for uav_status in pre_step_uav_status:
            uav_id = uav_status[0]
            if not current_uav_id.__contains__(uav_id):
                pre_step_uav_status.pop()
        return current_uav_status, current_original_target_status, \
               current_unit_task_status, current_threat, uav_next_point

    return pre_step_uav_status, current_original_target_status, \
           current_unit_task_status, current_threat, uav_next_point


# 得到当前step中的目标态势（元任务组态势）
def get_current_target(experiment_id, current_step, current_target_id,
                       target_sudden_flag, pre_step_original_target_status,
                       original_target_param, original_target_work_time):
    current_original_target_status = []
    if target_sudden_flag:
        for original_target_status in pre_step_original_target_status:
            zone_id = original_target_status[0]
            # 如果目标消失
            if not current_target_id.__contains__(zone_id):
                continue
            # 将集合中的id删除，剩下的则为新增的目标id
            current_target_id.remove(zone_id)
            current_original_target_status.append(original_target_status)
    # 对于新增的目标
    for zone_id in current_target_id:
        static_param = original_target_param.get(zone_id)
        tmp = copy.deepcopy(static_param)

        tmp.append(original_target_work_time.get(zone_id))
        current_original_target_status.append(tmp)

    return current_original_target_status


# 获得无人机下一个路径点的id
def get_next_uav_point(all_uav_status):
    uav_next_point = {}
    for uav_status in all_uav_status:
        uav_id = uav_status[0]
        next_point_id = uav_status[4]
        uav_next_point.update({uav_id: next_point_id})

    return uav_next_point


def get_uav_param(all_uav_status, uav_static_param):
    """

    :param all_uav_status:
    :param uav_static_param:
    :return: uav_static_param: 超前仿真开始时的所有无人机静态参数
    """
    all_uav_load, uav_max_distance, all_uav_position, all_uav_order_type, \
    all_route_point_number, all_task_finished_time, all_action_interval_time = {}, {}, {}, {}, {}, {}, {}
    for uav_status in all_uav_status:
        uav_id = uav_status[0]
        uav_position = uav_status[1]
        uav_action_status = uav_status[3]
        uav_next_point = uav_status[4]
        action_keep_time = uav_status[5]
        action_interval_time = uav_static_param.get(uav_id)[3]
        uav_load = uav_status[-2]
        uav_distance = uav_status[-1]
        all_uav_load.update({uav_id: uav_load})
        uav_max_distance.update({uav_id: uav_distance})
        all_uav_position.update({uav_id: uav_position})
        all_uav_order_type.update({uav_id: uav_action_status})
        all_route_point_number.update({uav_id: uav_next_point})
        all_task_finished_time.update({uav_id: action_keep_time})
        all_action_interval_time.update({uav_id: action_interval_time})

    return all_uav_load, uav_max_distance, all_uav_position, all_uav_order_type, \
           all_route_point_number, all_task_finished_time, all_action_interval_time


def get_task_param(all_task_status):
    task_static_param, task_work_time = {}, {}
    for task_status in all_task_status:
        task_id = task_status[0]
        static_param = task_status[:-1]
        work_time = task_status[-1]
        task_static_param.update({task_id: static_param})
        task_work_time.update({task_id: work_time})
    return task_static_param, task_work_time


'''
    在进行超实时仿真时，无人机的当前状态可能为：
                1. 无人机在飞行状态
                2. 无人机正在执行任务 -> 当无人机正在执行任务时，需要知道无人机继续在此任务点的任务时间
'''


# 对于动态参数，需要拷贝一份副本过来
# 超实时仿真，得到10s钟内的实时态势，并作为任务重规划算法的输入
# TODO: 所有的动态参数需要进行深拷贝之后传递过来
# current_uav_status,
# all_task_position,all_task_cost, all_task_id, all_task_start_flag,
# unit_task_status, original_target_status
def supper_over_time_simulation(experiment_id, task_type, current_step,
                                supper_real_time, step,
                                uav_static_param, current_uav_status,
                                all_uav_speed, all_uav_route, all_uav_start_position,
                                unit_task_status, original_target_status,
                                all_task_position, all_task_cost,
                                all_task_id, all_task_start_flag,
                                map_list, current_threat):
    """

    :param all_uav_start_position:
    :param current_uav_status:
    :param experiment_id:
    :param task_type:
    :param current_step:
    :param supper_real_time:
    :param step:
    :param uav_static_param:
    :param all_uav_speed:
    :param all_uav_route:
    :param unit_task_status:
    :param original_target_status:
    :param all_task_position:
    :param all_task_cost:
    :param all_task_id:
    :param all_task_start_flag:
    :param map_list:
    :param current_threat:
    :return:
    """
    # 超实时仿真的初始状态
    all_uav_load, all_uav_max_distance, all_uav_position, all_uav_order_type, all_route_point_number, \
    all_task_finished_time, all_action_interval_time = get_uav_param(current_uav_status, uav_static_param)

    unit_task_static_param, unit_task_work_time = get_task_param(unit_task_status)
    original_target_static_param, original_target_work_time = get_task_param(original_target_status)

    unit_task_ahead_event = {}
    original_target_ahead_event = {}
    end_step = 0
    while True:

        # 1. 获得下一秒的所有模型的态势
        end_step += step
        all_uav_status = get_next_second_uav_status(all_uav_order_type, all_uav_speed, all_uav_position,
                                                    all_route_point_number, all_uav_start_position,
                                                    all_task_finished_time, step * 1000, map_list, all_uav_route,
                                                    all_task_id,
                                                    all_action_interval_time)

        current_event = []
        update_by_event(unit_task_ahead_event, current_step, task_type,
                        event_type_id=-1, dynamic_shoot=unit_task_work_time,
                        current_event=None)

        update_by_event(original_target_ahead_event, current_step,
                        task_type, event_type_id=Event.ORIGINAL_TARGET.value, dynamic_shoot=original_target_work_time,
                        current_event=current_event)

        re_plan_uav_action(current_step,
                           all_uav_status, uav_static_param, all_uav_load,
                           all_task_id, all_task_position, all_task_cost, all_task_start_flag,
                           unit_task_static_param,
                           unit_task_ahead_event, original_target_ahead_event,
                           all_uav_speed, all_uav_max_distance)
        # 达到超实时仿真限定时间
        if end_step > supper_real_time:
            break

    return all_uav_load, all_uav_max_distance, all_uav_position


def get_next_second_uav_status(order_type_dict, uav_speed_dict, uav_position_dict,
                               route_point_number_dict, all_uav_start_position,
                               task_finished_time_dict, step, map_list, route,
                               single_task, action_interval_time_dict):
    """

    @param all_uav_start_position:
    @param order_type_dict: 指令类型
    @param uav_speed_dict: 当前无人机的速度列表（厘米/毫秒）
    @param uav_position_dict: 当前无人机的位置（厘米）
    @param route_point_number_dict: 当前导航点编号
    @param task_finished_time_dict: 拍照或投弹已执行的时间（毫秒）
    @param step: 预测步长（毫秒）
    @param map_list: 读取txt高程地图为二维列表map是一个400*400的二维数组,只存储z已读，通过x,y索引得到z
    @param route: 航迹表
    @param single_task: 单机任务表
    @param action_interval_time_dict: 每个无人机单次拍照或投弹的操作时间
    @return: 二维列表	uav_over_time_position_list	无人机预测位置


    """

    return [[1322, [0, 0, 0], 2]]
