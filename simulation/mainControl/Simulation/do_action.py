import random

from mainControl.Simulation.simulation_status_enum import Event, UavStatus


def uav_action_handler(experiment_id, task_type, current_step,
                       gazebo_uav_status, uav_static_param, uav_load,
                       all_task_id, all_task_position, all_task_cost, all_task_start_flag,
                       shared_event,
                       static_unit_task,
                       unit_task_ahead_event, original_target_ahead_event, current_event, action_ahead_event,
                       uav_ip_to_id,
                       all_uav_speed, all_uav_distance, all_uav_max_distance,
                       uav_height, map_accuracy, dem_accuracy
                       ):
    """
    判断无人机是否到达指定位置，进行动作。触发事件，保存当前无人机的实时状态
    :param dem_accuracy:
    :param map_accuracy:
    :param uav_height:
    :param all_uav_speed:
    :param all_uav_max_distance:
    :param all_uav_distance:
    :param all_task_id:
    :param all_task_start_flag:
    :param uav_ip_to_id:
    :param experiment_id: 试验id
    :param task_type: 任务类型
    :param current_step: 当前步长
    :param gazebo_uav_status: 所有无人机的状态
    :param uav_static_param: 无人机的静态参数
    :param uav_load: 无人机的动态参数（载荷）
    :param all_task_position: 每一架元任务的坐标
    :param all_task_cost: 每一个元任务的收益
    :param shared_event: 所有的事件
    :param shared_event_param: 所有的事件参数
    :param static_unit_task: 元任务组的静态参数
    :param unit_task_ahead_event: 缓存的提前发生的元任务组突发事件
    :param original_target_ahead_event: 缓存的提前发生的原始目标突发事件
    :param current_event: 当前事件
    :param action_ahead_event: 缓存的提前发生的动作突发事件
    :return: 可视化端需要的无人机数据，数据库端需要的无人机数据
    """
    # uav_status: [id, position, orientation, action_status, next_point,
    #               current_step, experiment_id, uav_name, uav_type_id, current_ammo]

    all_uav_status = []
    for uav_status in gazebo_uav_status:
        tmp = []
        uav_id = uav_ip_to_id.get(uav_status[0])
        uav_status[0] = uav_id
        uav_real_position = uav_status[1]
        uav_orientation = uav_status[2]
        uav_action_status = uav_status[3]
        uav_next_point = uav_status[4]
        static_param = uav_static_param.get(uav_id)
        if static_param[0] != uav_id:
            print('无人机id映射错误')
        uav_type_id = static_param[1]
        uav_name = static_param[2]
        uav_interval_time = static_param[3]
        uav_action_radius = static_param[4]
        uav_current_load = uav_load.get(uav_id)

        uav_status.append(uav_name)
        uav_status.append(uav_type_id)
        uav_status.append(experiment_id)
        uav_status.append(current_step)

        tmp.append(uav_id)
        tmp.append(str(uav_real_position))
        tmp.append(str(uav_orientation))
        tmp.append(uav_name)
        tmp.append(uav_type_id)
        tmp.append(experiment_id)
        tmp.append(current_step)

        # 更新无人机当前最远飞行距离
        uav_speed = all_uav_speed.get(uav_id)
        uav_max_distance = all_uav_max_distance.get(uav_id)

        distance = uav_speed * (current_step + 1)

        all_uav_distance.update({uav_id: distance})
        all_uav_max_distance.update({uav_id: uav_max_distance - uav_speed})

        if len(all_task_position.get(uav_id)) == 0:
            append_uav_status(tmp, uav_current_load, all_uav_max_distance.get(uav_id),
                              uav_real_position, uav_orientation,
                              map_accuracy)
            all_uav_status.append(tmp)
            continue
        #  获取无人机任务规划结果的目标位置     TODO
        task_position = all_task_position.get(uav_id)[0]

        # 任务开始标志
        task_start_flag = all_task_start_flag.get(uav_id)[0]

        # 无人机当前状态：2，3为侦察打击

        # 当无人机开始投弹或者还在投弹状态时
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
                trig_event(uav_id, task_type, experiment_id, current_step,
                           uav_real_position, task_cost, uav_interval_time, uav_height,
                           shared_event,
                           static_unit_task,
                           unit_task_ahead_event, original_target_ahead_event,
                           current_event, action_ahead_event,
                           uav_action_radius,
                           map_accuracy, dem_accuracy)
                all_task_start_flag.get(uav_id)[0] = True

            # 如果当前任务已开始，则对其进行减一，表示剩下的任务时间
            if all_task_cost.get(uav_id)[0] > 0:
                all_task_cost.get(uav_id)[0] -= 1

        # 如果当前任务已完成，则删除当前任务
        if all_task_cost.get(uav_id)[0] == 0:
            all_task_start_flag.get(uav_id).pop(0)
            all_task_id.get(uav_id).pop(0)
            all_task_position.get(uav_id).pop(0)
            all_task_cost.get(uav_id).pop(0)

        append_uav_status(tmp, uav_current_load, all_uav_max_distance.get(uav_id),
                          uav_real_position, uav_orientation,
                          map_accuracy)

        uav_status.append(uav_current_load)
        uav_status.append(all_uav_max_distance.get(uav_id))

        all_uav_status.append(tmp)

    return all_uav_status, gazebo_uav_status


"""
pre: 需要实时监听无人机的位置
当无人机到达任务位置之后，触发本函数，开始打击/侦察事件

需要提供的关键参数：
本次任务类型： 从初始时就可以得到
无人机的id：px4中返回
当前时间：px4中返回 update_time
任务位置: 根据无人机位置，得到当前的(x,y)坐标，再通过高程文件获得z，得到position=(x,y,z)
投弹数/侦察次数: 由任务分配得到，task_cost.和target中的health_point/info_point在数值上是相同的
间隔时间：interval_time, 无人机参数，固定值
投弹高度：height，无人机所在高度-高程值，position[2]-z
杀伤半径: radius，炸弹参数，固定值，作为无人机参数的一部分
毁伤概率: probability, 根据random产生的随机数
"""


def trig_event(object_id, task_type, experiment_id, current_step,
               position, action_time, interval_time, height,
               shared_event,
               static_unit_task,
               unit_task_ahead_event, original_target_ahead_event,
               current_event, action_ahead_event,
               radius, dem_accuracy,
               probability=1):
    """

    :param dem_accuracy:
    :param action_ahead_event: 缓存接下来几个步长要发生的动作事件
    :param current_event: 当前步长发生的事件
    :param experiment_id: 试验id
    :param object_id: 事件发生的对象
    :param task_type: 任务类型
    :param current_step: 当前步长
    :param position: 事件发生的位置
    :param action_time： 无人机动作时间
    :param interval_time: 无人机攻击间隔
    :param height: 无人机与目标相对高度
    :param shared_event: 所有的事件，存储至数据库
    :param shared_event_param: 所有的事件参数，存储至数据库
    :param static_unit_task: 元任务组的静态参数
    :param unit_task_ahead_event: 缓存接下来几个步长要发生的元任务组事件
    :param original_target_ahead_event: 缓存接下来几个步长要发生的原始目标事件
    :param radius: 无人机拍照/轰炸半径
    :param probability: 本次任务成功概率
    :return:
    """

    # 触发无人机拍照/攻击事件，添加至shared_event中

    event_num = len(shared_event)
    event_id = event_num + 1
    uav_event_param = [task_type, action_time]
    uav_event_store = [event_id, Event.UAV_ACTION.value, object_id, str(uav_event_param),
                       experiment_id, current_step, Event.UAV_ACTION.value]
    shared_event.append(uav_event_store)

    # 当前step，发生的事件
    uav_event = {}
    uav_event.update({'event_type_id': Event.UAV_ACTION.value})
    uav_event.update({'object_id': object_id})
    uav_event_param = {'event_param': [task_type, action_time]}
    uav_event.update(uav_event_param)

    current_event.append(uav_event)

    """
    无人机载弹量减少已经提取到外部去做
    """

    # 产生action_time次爆炸/侦察事件，向event表中插入
    do_action(current_step, task_type, action_time, interval_time,
              height, object_id, radius, probability,
              position, experiment_id, shared_event,
              static_unit_task, unit_task_ahead_event, original_target_ahead_event, action_ahead_event,
              dem_accuracy)


def do_action(current_step, task_type, action_time, interval_time,
              height, object_id, radius, probability,
              position, experiment_id, shared_event,
              static_unit_task, unit_task_ahead_event, original_target_ahead_event, action_ahead_event,
              dem_accuracy,):
    """

    :param action_ahead_event: 爆炸提前事件
    :param current_step:
    :param action_time:
    :param interval_time:
    :param height:
    :param object_id:
    :param task_type:
    :param radius:
    :param probability:
    :param position:
    :param experiment_id:
    :param shared_event:
    :param static_unit_task:
    :param unit_task_ahead_event:
    :param original_target_ahead_event:
    :return:
    """

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

        event_id = len(shared_event) + 1
        action_event_param_store = [[task_type, radius], position]
        boom_event = [event_id, Event.BOOM.value, object_id, str(action_event_param_store),
                      experiment_id, new_step, Event.BOOM.value]
        shared_event.append(boom_event)

        """
            # 将action_event添加至缓存的action_ahead_event中，
            # 在步长到来的时候对action_ahead_event进行处理（添加至指定步长的事件中，并发送给可视化端）
        """
        '''
            爆炸事件不需要格外进行处理，因为掉血事件存在叠加，而爆炸事件不考虑多架无人机轰炸一个目标的显示问题。
            爆炸的本质上为影响目标的血量，因此通过一个action_ahead_event即可存储，在对应的step中进行显示即可
        '''
        action_event = {}
        action_event.update({'event_type_id': Event.BOOM.value})
        action_event.update({'object_id': object_id})
        action_event_param = {'event_param': [[task_type, radius], position]}
        action_event.update(action_event_param)
        action_ahead_event.update({new_step: action_event})

        # 发生爆炸, 目标掉血
        change_target(position, radius, probability, experiment_id,
                      new_step, static_unit_task,
                      unit_task_ahead_event, original_target_ahead_event,
                      dem_accuracy)


def change_target(position, radius, probability, experiment_id,
                  new_step, static_unit_task,
                  unit_task_ahead_event, original_target_ahead_event,
                  dem_accuracy):
    """

    :param dem_accuracy:
    :param position: 爆炸发生位置
    :param radius: 爆炸发生半径
    :param probability:
    :param task_type:
    :param experiment_id:
    :param new_step: 目标事件发生时的步长
    :param static_unit_task:
    :param shared_event:
    :param unit_task_ahead_event:
    :param original_target_ahead_event:
    :return:
    """
    # 将radius以格子作为单位

    radius = radius * dem_accuracy
    distance = radius * radius
    # 对于所有的元任务组
    for result in static_unit_task:
        # 获取元任务组位置
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


def append_uav_status(uav_status, uav_current_load, current_max_distance,
                      uav_real_position, uav_orientation,
                      map_accuracy):
    uav_status.append(uav_current_load)
    uav_status.append(current_max_distance)
    uav_status.append(uav_real_position[0] * map_accuracy)
    uav_status.append(uav_real_position[1] * map_accuracy)
    uav_status.append(uav_real_position[2] * map_accuracy)
    uav_status.append(uav_orientation[0])
    uav_status.append(uav_orientation[1])
    uav_status.append(uav_orientation[2])
    uav_status.append(uav_orientation[3])
