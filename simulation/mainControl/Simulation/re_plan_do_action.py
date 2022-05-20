import random

from mainControl.Simulation.simulation_status_enum import UavStatus


def re_plan_uav_action(current_step,
                       gazebo_uav_status, uav_static_param, uav_load,
                       all_task_id, all_task_position, all_task_cost, all_task_start_flag,
                       static_unit_task,
                       unit_task_ahead_event, original_target_ahead_event,
                       all_uav_speed, all_uav_max_distance
                       ):
    """

    @param experiment_id:
    @param task_type:
    @param current_step:
    @param gazebo_uav_status:
    @param uav_static_param:
    @param uav_load:
    @param all_task_id:
    @param all_task_position:
    @param all_task_cost:
    @param all_task_start_flag:
    @param static_unit_task:
    @param unit_task_ahead_event:
    @param original_target_ahead_event:
    @param current_event:
    @param uav_ip_to_id:
    @param all_uav_speed:
    @param all_uav_max_distance:
    @return:
    """
    for uav_status in gazebo_uav_status:
        uav_id = uav_status[0]
        uav_position = uav_status[1]
        uav_action_status = uav_status[2]
        static_param = uav_static_param.get(uav_id)
        uav_type_category = static_param[1]
        uav_height = 20
        uav_interval_time = static_param[3]
        uav_action_radius = static_param[4]
        uav_current_load = uav_load.get(uav_id)

        uav_speed = all_uav_speed.get(uav_id)
        uav_max_distance = all_uav_max_distance.get(uav_id)
        distance = uav_speed * (current_step + 1)
        all_uav_max_distance.update({uav_id: uav_max_distance - uav_speed})

        task_start_flag = all_task_start_flag.get(uav_id)[0]

        if uav_action_status == UavStatus.SCOUT.value or uav_action_status == UavStatus.ATTACK.value \
                or (task_start_flag and all_task_cost.get(uav_id)[0] > 0):
            # TODO: 将每一架无人机无人机action的位置传入，并与uav_real_position比较，判断是否进行动作
            # if check_arrive(task_position, uav_real_position):
            # 如果当前任务还没有开始
            if not task_start_flag:
                # 侦察次数，投弹数量
                task_cost = all_task_cost.get(uav_id)[0]
                #  如果进行动作，则直接减对应的投弹量
                uav_current_load -= task_cost
                if uav_current_load <= 0:
                    uav_load.update({uav_id: 0})
                # 无人机的载荷减少
                else:
                    uav_load.update({uav_id: uav_current_load})
                # 触发无人机事件
                trig_event(current_step,
                           uav_position, task_cost, uav_interval_time, uav_height,
                           static_unit_task,
                           unit_task_ahead_event, original_target_ahead_event,
                           uav_action_radius)
                all_task_start_flag.get(uav_id)[0] = True

            # 如果当前任务已开始，则对其进行减一，表示剩下的任务时间
            all_task_cost.get(uav_id)[0] -= 1
        # 如果当前任务已完成，则删除当前任务
        if all_task_cost.get(uav_id)[0] == 0:
            all_task_start_flag.get(uav_id).pop(0)
            all_task_id.get(uav_id).pop(0)
            all_task_position.get(uav_id).pop(0)
            all_task_cost.get(uav_id).pop(0)


def trig_event(current_step,
               position, action_time, interval_time, height,
               static_unit_task,
               unit_task_ahead_event, original_target_ahead_event,
               radius, probability=1):
    # 产生action_time次爆炸/侦察事件，向event表中插入
    do_action(current_step, action_time, interval_time,
              height, radius, probability,
              position,
              static_unit_task, unit_task_ahead_event, original_target_ahead_event)


def do_action(current_step, action_time, interval_time,
              height, radius, probability,
              position,
              static_unit_task, unit_task_ahead_event, original_target_ahead_event):
    # 产生action_time次爆炸事件，向event表中插入
    new_step = current_step
    for i in range(action_time):
        # # 第一次投弹不需要计算间隔时间
        # if i != 0:
        #     new_step += interval_time
        # # 计算炸药延迟时间 / 拍照时间
        # # do_action_time = math.sqrt(2 * height / 9.8)
        # # 爆炸/拍照真实发生时间： 新的步长，与原来的步长不一致了
        # TODO: 当前设定，在无人机投弹之后的一个step后，爆炸发生
        new_step += 1
        # 发生爆炸, 目标掉血
        change_target(position, radius, probability,
                      new_step, static_unit_task,
                      unit_task_ahead_event, original_target_ahead_event)


def change_target(position, radius, probability,
                  new_step, static_unit_task,
                  unit_task_ahead_event, original_target_ahead_event):

    # 将radius以格子作为单位
    dem_accuracy = 12.5
    radius = radius * dem_accuracy
    distance = radius * radius
    # 对于所有的元任务组
    for unit_task_id in static_unit_task:
        # 获取元任务组位置
        result = static_unit_task.get(unit_task_id)
        meta_task_id = result[0]
        meta_task_position = result[2]
        meta_task_position = meta_task_position.split(',')

        # 判断目标位置是否在以任 务位置为中心，半径为radius的杀伤半径内
        x_interval = float(meta_task_position[0]) * dem_accuracy - float(position[0])
        y_interval = float(meta_task_position[1]) * dem_accuracy - float(position[1])

        flag = x_interval * x_interval + y_interval * y_interval <= distance
        # 如果目标在爆炸范围之内
        if flag:
            # 考虑毁伤概率
            random_pro = random.random()
            if random_pro < probability:
                # 保存元任务组掉血事件
                save_ahead_event(unit_task_ahead_event, new_step, meta_task_id)
                zone_id = result[1]
                # 保存原始目标区掉血事件
                save_ahead_event(original_target_ahead_event, new_step, zone_id)


def save_ahead_event(ahead_event, new_step, target_id):
    #  判断当前目标在新步长是否已经掉血过
    if ahead_event.__contains__(new_step) and \
            ahead_event.get(new_step).__contains__(target_id):
        # 多加1点掉血
        new_val = ahead_event.get(new_step).get(target_id) + 1
        ahead_event.get(new_step).update({target_id: new_val})
    elif ahead_event.__contains__(new_step):
        # 新步长当前目标产生掉血
        ahead_event.get(new_step).update({target_id: 1})
    else:
        ahead_event.update({new_step: {target_id: 1}})
