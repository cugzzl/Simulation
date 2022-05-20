from mainControl.Simulation.simulation_status_enum import IsDetected


def get_scen_attack_target(db_pool, mission_id):
    my = db_pool.connection()
    cursor = my.cursor()
    sql = 'SELECT * FROM scen_attack_target where mission_id=%d' % mission_id
    cursor.execute(sql)
    results = cursor.fetchall()
    my.commit()
    my.close()
    return results

def get_scen_attack_target_by_id(db_pool, id):
    my = db_pool.connection()
    cursor = my.cursor()
    sql = 'SELECT * FROM scen_attack_target where zone_id=%d' % id
    cursor.execute(sql)
    results = cursor.fetchall()
    my.commit()
    my.close()
    return results

def save_scen_attack_target(db_pool, all_attack_target, mission_id):

    my = db_pool.connection()
    cursor = my.cursor()
    s = ' DELETE FROM scen_attack_target where mission_id=%s' % mission_id
    cursor.execute(s)
    my.commit()

    s = 'alter table scen_attack_target AUTO_INCREMENT=1;'
    cursor.execute(s)
    my.commit()

    for data in all_attack_target:
        sql = "INSERT INTO scen_attack_target(target_name, positions, map_position, original_yaw, mission_id, target_type_id, meta_tasks_id, target_profit, original_hp, map_x, map_y, map_z) VALUES ('"  + str(data[1]) + "', '" + str(data[2]) + "', '" + str(data[3]) +"', '" + str(data[4]) +"', '" + str(data[5]) +"', '" + str(data[6]) +"', '" + str(data[7]) +"', '" + str(data[8]) +"', '" + str(data[9]) + "', '" + str(data[10]) +"', '" + str(data[11]) +"', '" + str(data[12]) +"');"
        cursor.execute(sql)
    my.commit()
    my.close()
    return True

def update_attack_scout_target(db_pool, all_attack_position, mission_id):
    my = db_pool.connection()
    cursor = my.cursor()
    target_id = 1
    for position in all_attack_position:
        cursor.execute("""update scen_attack_target set positions =%s where target_id=%s and mission_id=%s""", (position, target_id, mission_id))
        target_id = target_id + 1
    my.commit()
    my.close()
    return True


# 获取初始状态下所有原始目标的参数
def get_original_attack_target_param(db, mission_id, sim_id):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select target_id, target_name, target_type_id, positions, target_profit, original_hp from ' \
          'scen_attack_target where mission_id= %s' % mission_id
    cursor.execute(sql)

    results = cursor.fetchall()
    static_original_target_param = {}
    original_work_time = {}
    original_target_is_detected = {}
    for result in results:
        zone_id = result[0]
        zone_name = result[1]
        zone_type = result[2]
        position = result[3]
        profit = result[4]
        scout_difficulty = result[5]
        sql = 'select count(*) from plan_attack_meta_tasks where sim_id=%s and zone_id=%s'
        data = [sim_id, zone_id]
        cursor.execute(sql, data)
        len_unit_task = cursor.fetchone()[0]
        # len_unit_task = num_unit_task_of_zone.get(zone_id)
        original_target_param = [zone_id, zone_name, zone_type, position, profit]
        static_original_target_param.update({zone_id: original_target_param})
        original_work_time.update({zone_id: scout_difficulty * len_unit_task})
        original_target_is_detected.update({zone_id: IsDetected.No.value})

    return static_original_target_param, original_work_time, original_target_is_detected
