import pymysql
from dbutils.persistent_db import PersistentDB

from mainControl.Simulation.uav_static_param import UavStaticParam


def get_scen_uav(db_pool):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select * from scen_uav'
    cursor.execute(sql)

    result = cursor.fetchall()

    return result


def get_scen_uav_by_category(db_pool, task_type, scenario_id):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select * from scen_uav where uav_type_category=%d and scenario_id=%s' % (task_type, scenario_id)
    cursor.execute(sql)

    result = cursor.fetchall()

    return result


def get_scen_uav_by_category_and_endTime(db_pool, task_type, scenario_id, endTime):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select * from scen_uav where uav_type_category=%d and scenario_id=%s and uav_end_time > %s' % (
    task_type, scenario_id, endTime)
    cursor.execute(sql)

    result = cursor.fetchall()

    return result


def save_scen_uav(db_pool, all_scen_uav, scenario_id):
    my = db_pool.connection()
    cursor = my.cursor()
    s = ' DELETE FROM scen_uav where scenario_id=%s' % scenario_id
    cursor.execute(s)
    my.commit()

    s = 'alter table scen_uav AUTO_INCREMENT=1;'
    cursor.execute(s)
    my.commit()

    for data in all_scen_uav:
        sql = "INSERT INTO scen_uav (uav_name, position, scenario_id, uav_type_id, uav_type_category, uav_max_speed, uav_max_height, uav_max_distance, uav_min_radius, radius, action_interval_time, max_load, parent_uav_id, map_x, map_y, map_z, icon_path, uav_type_name) VALUES ('" + str(
            data[0]) + "', '" + str(data[1]) + "', '" + str(
            data[2]) + "', '" + str(data[3]) + "', '" + str(data[4]) + "', '" + str(data[5]) + "', '" + str(
            data[6]) + "', '" + str(data[7]) + "', '" + str(data[8]) + "', '" + str(data[9]) + "', '" + str(
            data[10]) + "', '" + str(data[11]) + "', '" + str(data[12]) + "', '" + str(data[13]) + "', '" + str(
            data[14]) + "', '" + str(data[15]) + "', '" + str(data[16]) + "', '" + str(data[17]) + "');"
        cursor.execute(sql)
    my.commit()
    my.close()


def get_uav_position(db_pool, task_type, scenario_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = 'select uav_id, map_x, map_y, map_z from scen_uav where uav_type_category = %s and scenario_id = %s'
    data = [task_type, scenario_id]
    cursor.execute(sql, data)
    results = cursor.fetchall()
    uav_position = {}
    for result in results:
        position = []
        uav_id = result[0]
        position.append(result[1])
        position.append(result[2])
        position.append(result[3])
        uav_position.update({uav_id: position})
    return uav_position


def get_id_and_position_by_category(db_pool, task_type, scenario_id):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select uav_id, map_x, map_y, map_z from scen_uav where uav_type_category=%s and scenario_id=%s'
    data = [task_type, scenario_id]
    cursor.execute(sql, data)
    results = cursor.fetchall()
    uav_num = len(results)
    ans = []
    for result in results:
        uav_id = result[0]
        map_x = result[1]
        map_y = result[2]
        ans.append(uav_id)
        ans.append(map_x)
        ans.append(map_y)
    return uav_num, str(ans)


# 获取初始状态下所有无人机的参数
def get_uav_param(db, scene_id, task_type):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select uav_id, uav_type_category, uav_type_id, action_interval_time, radius, max_load, uav_max_distance, ' \
          'uav_max_speed  from scen_uav where ' \
          'scenario_id=%s' % scene_id
    cursor.execute(sql)
    results = cursor.fetchall()
    all_uav_static_param = {}
    uav_load = {}
    uav_max_distance = {}
    uav_distance = {}
    all_uav_speed = {}
    all_uav_id = []
    for result in results:
        uav_id = result[0]
        uav_type_category = result[1]
        if int(uav_type_category) != task_type:
            continue
        uav_type_id = result[2]
        action_interval_time = result[3]
        radius = result[4] / 100
        max_load = result[5]
        max_distance = result[6]
        uav_speed = result[7] * 100
        # uav_static_param = UavStaticParam(uav_id, uav_type_category, uav_type_id, action_interval_time, radius)
        # all_uav_static_param.update({uav_id: uav_static_param})
        uav_param = [uav_id, uav_type_category, uav_type_id, action_interval_time, radius]
        all_uav_static_param.update({uav_id: uav_param})
        uav_load.update({uav_id: max_load})
        uav_max_distance.update({uav_id: max_distance})
        uav_distance.update({uav_id: 0})
        all_uav_speed.update({uav_id: uav_speed})
        all_uav_id.append(uav_id)

    return all_uav_static_param, uav_load, uav_max_distance, uav_distance, all_uav_speed, all_uav_id
