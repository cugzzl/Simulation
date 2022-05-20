import json


def socket_save_target_status(static_original_target, original_target_work_time):
    socket_all_zone_status = []
    for original_target in static_original_target:
        socket_zone_status = {}
        zone_id = original_target[0]
        work_time = original_target_work_time.get(zone_id)
        #  添加需要给可视化传递的变量
        socket_zone_status.update({'zone_id': zone_id})
        socket_zone_status.update({'current_load': work_time})
        is_detected = 0
        if original_target_work_time.get(zone_id) == 0:
            is_detected = 1
        socket_zone_status.update({'is_detected': is_detected})
        socket_all_zone_status.append(socket_zone_status)
    return socket_all_zone_status


def socket_save_attack_target_status(static_original_attack_target_status, original_target_is_detected):
    socket_all_zone_status = []
    for original_target in static_original_attack_target_status:
        socket_zone_status = {}
        zone_id = original_target[0]
        #  添加需要给可视化传递的变量
        socket_zone_status.update({'zone_id': zone_id})
        socket_zone_status.update({'is_detected': original_target_is_detected.get(zone_id)})
        socket_all_zone_status.append(socket_zone_status)
    return socket_all_zone_status


def socket_save_uav_status(shared_current_uav_status, all_uav_load):
    socket_all_uav_status = []
    for uav_status in shared_current_uav_status:
        socket_uav_status = {}
        uav_id = uav_status[0]
        uav_real_position = uav_status[1]
        uav_orientation = uav_status[2]
        uav_load = all_uav_load.get(uav_id)
        uav_real_load = uav_status[7]
        if uav_load != uav_real_load:
            print('无人机载弹数据错误')
        socket_uav_status.update({'uav_id': uav_id})
        socket_uav_status.update({'position': uav_real_position})
        socket_uav_status.update({'orientation': uav_orientation})
        socket_uav_status.update({'current_load': uav_load})
        socket_all_uav_status.append(socket_uav_status)

    return socket_all_uav_status


def socket_save_current_status(uav_status, zone_status, current_event,
                               current_step, socket_attack_target_status=None):
    current_status = {}
    current_status.update({'step': current_step})
    current_status.update({0: uav_status})
    current_status.update({1: zone_status})
    current_status.update({2: current_event})

    if socket_attack_target_status is not None:
        current_status.update({3: socket_attack_target_status})
    socket_current_status = json.dumps(current_status)
    return socket_current_status
