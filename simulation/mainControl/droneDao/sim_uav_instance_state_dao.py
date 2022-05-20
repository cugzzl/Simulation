def get_sim_uav_instance_state(db_pool, experiment_id, time):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM sim_uav_instance_state where sim_id='%d' and update_time='%d'" % (experiment_id, time)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def save_sim_uav_state(db, shared_uav_status):
    conn = db.connection()
    cursor = conn.cursor()
    conn.begin()

    # # 得到无人机仿真结果，将结果存入数据库中
    # for all_uav_status in shared_uav_status:
    #     # 每一个step
    #     for uav_status in all_uav_status:
    #         uav_id = uav_status[0]
    #         uav_position = uav_status[1]
    #         uav_orientation = uav_status[2]
    #         current_step = uav_status[6]
    #         experiment_id = uav_status[5]
    #         uav_name = uav_status[3]
    #         uav_type_id = uav_status[4]
    #         current_load = uav_status[7]
    #         current_max_distance = uav_status[8]
    #         sql = "insert into `sim_uav_instance_state` (uav_id, current_position, current_orientation, update_time, sim_id, uav_name, uav_type_id, current_load, current_max_distance) value('" + \
    #               str(uav_id) + "', '" + str(uav_position) + \
    #               "', '" + str(uav_orientation) + "', '" + str(current_step) + "', '" + str(experiment_id) + \
    #               "', '" + str(uav_name) + "', '" + str(uav_type_id) + "', '" + str(current_load) + "', '" + str(
    #             current_max_distance) + "')"
    #         cursor.execute(sql)
    # conn.commit()
    # cursor.close()
    # conn.close()

    for all_uav_status in shared_uav_status:
        sql = "insert into `sim_uav_instance_state` (uav_id, current_position, current_orientation, uav_name, " \
              "uav_type_id, sim_id, update_time, current_load, current_max_distance, current_map_x, current_map_y, current_map_z, Q_x, Q_y, Q_z, Q_w) value(%s, %s, %s, %s, %s, %s, " \
              "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        cursor.executemany(sql, all_uav_status)
    conn.commit()
    cursor.close()
    conn.close()
