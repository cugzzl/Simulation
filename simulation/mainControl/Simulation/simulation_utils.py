import copy

from Simulation.simulation_status_enum import Event


def get_init_model(model, task_sudden, current_step):
    current_id = set()
    current_model = []
    not_exist = set()
    for sudden in task_sudden:
        # 判断是否应该在当前时间出现，添加进集合中
        if sudden[1] > current_step or sudden[2] < current_step:
            sudden_model_id = sudden[0]
            not_exist.add(sudden_model_id)

    for model_id in model:
        if not_exist.__contains__(model_id):
            continue
        current_model.append(model.get(model_id))
        current_id.add(model_id)
    return current_model, current_id


def filter_current_model(all_kind_sudden, static_model,
                         current_step, experiment_id):
    """
    根据突发状况时间，得到当前step中应当存在的模型
    :param experiment_id: 试验id
    :param all_kind_sudden: 突发的目标事件
    :param static_model: 模型静态参数
    :param current_step: 当前步长
    :return: 当前step中应该出现的模型的静态参数（原始目标、威胁、无人机）
    """
    not_exist = set()
    for sudden in all_kind_sudden:
        # 判断是否应该在当前时间出现，添加进集合中
        if sudden[1] > current_step or sudden[2] < current_step:
            sudden_model_id = sudden[0]
            not_exist.add(sudden_model_id)
    current_static_model = []
    current_model_id = set()
    for model_id in static_model:
        model = static_model.get(model_id)
        if not_exist.__contains__(model_id):
            continue
        tmp = copy.deepcopy(model)
        tmp.append(experiment_id)
        tmp.append(current_step)
        current_static_model.append(tmp)
        current_model_id.add(model_id)

    return current_static_model, current_model_id


def filter_current_unit_task(current_original_target_id, unit_task_param):
    """
    根据当前step存在的原始目标得到元任务组
    :param current_original_target_id: 当前step中应当出现的原始目标id
    :param unit_task_param: 所有的元任务组参数
    :param current_step:
    :param experiment_id:
    :return:
    """
    current_static_unit_task = []
    current_unit_task_id = set()
    for task_id in unit_task_param:
        static_unit_task_param = unit_task_param.get(task_id)
        tmp = []
        for e in static_unit_task_param:
            tmp.append(e)
        zone_id = static_unit_task_param[1]
        if not current_original_target_id.__contains__(zone_id):
            continue
        current_unit_task_id.add(task_id)
        current_static_unit_task.append(tmp)

    return current_static_unit_task, current_unit_task_id


def get_kind_sudden(sudden, sudden_kind):
    """
    根据突发状况的类型，获得不同突发状况
    :param sudden_kind:
    :param sudden: 所有的突发状况
    :return: 目标突发状况
    """
    # 1. 过滤，更新当前状态下的元任务组状态
    all_kind_sudden = []
    for i in sudden:
        if int(i[0]) == sudden_kind:
            kind_sudden = []
            # 对象id
            kind_sudden.append(i[1])
            # 开始时间
            kind_sudden.append(i[2]/1000)
            # 结束时间
            kind_sudden.append(i[3]/1000)
            all_kind_sudden.append(kind_sudden)
    return all_kind_sudden


def update_by_event(ahead_event, current_step, task_type,
                    dynamic_shoot, event_type_id, current_event):
    """
    对于当前step发生的事件，对动态参数进行更新
    :param event_type_id: 事件类型
    :param current_event: 当前step中应该发生的事件
    :param task_type: 任务类型
    :param ahead_event: 等待发生的元任务组/原始目标事件/爆炸事件
    :param current_step: 当前步长
    :param dynamic_shoot: 元任务组/原始目标区 当前余量
    :return:
    """

    # 如果当前step存在事件
    if ahead_event.__contains__(current_step):

        # 获取当前step的所有事件
        tmp_current_event = ahead_event.get(current_step)
        # 如果为爆炸事件，则只将爆炸事件添加至当前事件，不进行进一步的处理
        if event_type_id == Event.BOOM.value:
            current_event.append(tmp_current_event)
        # 为元任务事件或者原始目标事件
        else:
            # 对于每一个事件
            for object_id in tmp_current_event.keys():
                # 若当前血量已经很少或者已经为0，则直接将当前血量置0
                pre_shoot = dynamic_shoot.get(object_id)
                if pre_shoot >= tmp_current_event.get(object_id):
                    current_shoot = pre_shoot - tmp_current_event.get(object_id)
                # 更新对应id的元任务组/原始目标的当前血量
                else:
                    current_shoot = 0
                dynamic_shoot.update({object_id: current_shoot})
                # 如果为原始目标类型的突发事件
                if event_type_id == Event.ORIGINAL_TARGET.value:
                    # 加入到current_event中
                    target_event = {}
                    target_event.update({'event_type_id': event_type_id})
                    target_event.update({'object_id': object_id})
                    target_event_param = [task_type, current_shoot]
                    target_event.update({'event_param': target_event_param})
                    current_event.append(target_event)

        # 将当前step的事件移除
        ahead_event.pop(current_step)


def get_uav_source(all_uav_id):
    uav_source = 0
    uav_id_to_ip = {}
    uav_ip_to_id = {}
    for uav_id in all_uav_id:
        uav_id_to_ip.update({uav_id: uav_source})
        uav_ip_to_id.update({uav_source: uav_id})
        uav_source += 1

    return uav_id_to_ip, uav_ip_to_id


def get_changed_unit_task(static_task_param, task_work_time,
                          pre_unit_task, current_task_id):
    """
    获得变化的元任务组
    :param static_task_param:
    :param task_work_time:
    :param pre_unit_task:
    :param current_task_id:
    :return:
    """
    add_task = {}
    missed_task = {}
    for unit_task in pre_unit_task:
        task_id = unit_task[0]
        # 如果当前id中没有上一步中的task，则表明该task消失
        if not current_task_id.__contains__(task_id):
            missed_task.update({task_id: unit_task})
            continue
        current_task_id.remove(task_id)

    for task_id in current_task_id:
        static_param = static_task_param.get(task_id)
        tmp = copy.deepcopy(static_param)
        tmp.append(task_work_time.get(task_id))
        add_task.update({task_id: tmp})

    return missed_task, add_task
