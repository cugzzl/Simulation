import numpy as np
from mainControl.Simulation.simulation_status_enum import TaskType



def get_re_plan_data(current_uav_status, task_type,
                     all_task_position, all_task_cost, all_task_profit, all_uav_task_id,
                     all_uav_speed, uav_max_distance, all_uav_load, all_uav_position,
                     missed_task=None, add_task=None):
    # add_task格式：{task_id: [task_id, zone_id, position, profit, work_time]}

    uav_num = len(current_uav_status)
    current_uav_id = set()
    for uav_status in current_uav_status:
        current_uav_id.add(uav_status[0])
    all_task_id = set()
    single_task_position = {}
    single_task_cost = {}
    assign_list = []
    for uav_id in current_uav_id:
        # 获得single_task的编号
        single_task_id = all_uav_task_id.get(uav_id)
        assign_list.append(single_task_id)
        tmp_task_position = all_task_position.get(uav_id)
        tmp_task_cost = all_task_cost.get(uav_id)
        num_task = len(single_task_id)
        for i in range(num_task):
            task_id = single_task_id[i]
            task_position = tmp_task_position[i]
            task_cost = tmp_task_cost[i]
            single_task_position.update({task_id: task_position})
            single_task_cost.update({task_id: task_cost})
            all_task_id.add(task_id)

    if task_type == TaskType.SCOUT.value:
        task_num = len(all_task_id)
    else:
        task_num = len(all_task_id) + len(add_task)

    all_target_lists = np.zeros(shape=(task_num + 1, 6), dtype=np.int32)
    if task_type == TaskType.SCOUT.value:
        i = 0
        for task_id in all_task_id:
            task_position = single_task_position.get(task_id)
            position = task_position.split(',')
            all_target_lists[i + 1, 0] = int(position[0])
            all_target_lists[i + 1, 1] = int(position[1])
            all_target_lists[i + 1, 2] = int(position[2])
            all_target_lists[i + 1, 4] = single_task_cost.get(task_id)
            all_target_lists[i + 1, 3] = all_task_profit.get(task_id)
            i += 1
    elif task_type == TaskType.ATTACK.value:
        i = 0
        for task_id in all_task_id:
            task_position = single_task_position.get(task_id)
            position = task_position.split(',')
            all_target_lists[i + 1, 0] = int(position[0])
            all_target_lists[i + 1, 1] = int(position[1])
            all_target_lists[i + 1, 2] = int(position[2])
            all_target_lists[i + 1, 5] = single_task_cost.get(task_id)
            all_target_lists[i + 1, 3] = all_task_profit.get(task_id)
            i += 1
        for task_id in add_task:
            task_param = add_task.get(task_id)
            task_position = task_param[2]
            position = task_position.split(',')
            all_target_lists[i + 1, 0] = int(position[0])
            all_target_lists[i + 1, 1] = int(position[1])
            all_target_lists[i + 1, 2] = int(position[2])
            all_target_lists[i + 1, 3] = task_param[4]
            all_target_lists[i + 1, 4] = task_param[3]
    new_task_id = []
    new_task_flag = []
    if missed_task is not None:
        for task_id in missed_task:
            new_task_id.append(task_id)
            new_task_flag.append(0)
    if add_task is not None:
        for task_id in add_task:
            new_task_id.append(task_id)
            new_task_flag.append(1)
    new_task = [new_task_id, new_task_flag]
    uav_speed_list, uav_flight_distance_list, uav_load_list, current_position_list = [], [], [], []
    for uav_id in current_uav_id:
        uav_speed_list.append(all_uav_speed.get(uav_id) / 10)
        uav_flight_distance_list.append(uav_max_distance.get(uav_id))
        uav_load_list.append(all_uav_load.get(uav_id))
        current_position_list.append(all_uav_position.get(uav_id))

    return uav_num, task_num, all_target_lists, uav_speed_list, \
           uav_flight_distance_list, uav_load_list, current_position_list, assign_list, new_task


def re_plan_data_to_ros(uav_num, task_num, all_target_lists,
                        uav_speed_list, uav_flight_distance_list,
                        time_lim, task_type, uav_load_list,
                        task_algorithm_param_list, current_position_list,
                        assign_list, new_task, current_threat, experiment_id,
                        re_plan_algorithm_param):
    message = {}
    message.update({'uav_num': uav_num})
    message.update({'target_num': task_num})
    message.update({'all_target_lists': all_target_lists})
    message.update({'uav_speed_list': uav_speed_list})
    message.update({'uav_flight_distance_list': uav_flight_distance_list})
    message.update({'time_lim': time_lim})
    message.update({'task_type': task_type})
    message.update({'uav_load_list': uav_load_list})
    message.update({"task_algorithm_param_list": task_algorithm_param_list})
    message.update({"current_position_list": current_position_list})
    message.update({'assign_list': assign_list})
    message.update({'new_task': new_task})
    message.update({'current_threat': current_threat})
    message.update({'experiment_id': experiment_id})
    message.update({'re_plan_algorithm_param': re_plan_algorithm_param})

    return message



