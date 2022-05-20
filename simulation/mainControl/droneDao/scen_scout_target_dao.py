
def get_scen_scout_target(db_pool, scene_id):
    my = db_pool.connection()
    cursor = my.cursor()
    sql = 'SELECT * FROM scen_scout_target where scene_id=%d' % scene_id
    cursor.execute(sql)
    results = cursor.fetchall()
    my.commit()
    my.close()
    return results

def get_scen_scout_target_by_id(db_pool, id, scene_id):
    my = db_pool.connection()
    cursor = my.cursor()
    sql = 'SELECT * FROM scen_scout_target where zone_id=%d and scene_id=%s' % (id, scene_id)
    cursor.execute(sql)
    results = cursor.fetchall()
    my.commit()
    my.close()
    return results

def update_scen_scout_target_position(db_pool, all_position, scene_id):
    my = db_pool.connection()
    cursor = my.cursor()
    zone_id = 1
    for position in all_position:
        if len(position) == 1:
            position_str = position[0]
            zone_type = 0
            sql = 'update scen_scout_target set zone_category=%d where zone_id=%d and scene_id=%s' % (zone_type, zone_id, scene_id)
            cursor.execute(sql)
        if len(position) == 2:
            position_str = position[0] + ';' + position[1]
            zone_type = 1
            sql = 'update scen_scout_target set zone_category=%d where zone_id=%d and scene_id=%s' % (zone_type, zone_id, scene_id)
            cursor.execute(sql)
        if len(position) == 4:
            position_str = position[0] + ';' + position[1] + ';' + position[2] + ';' + position[3]
            zone_type = 2
            sql = 'update scen_scout_target set zone_category=%d where zone_id=%d and scene_id=%s' % (zone_type, zone_id, scene_id)
            cursor.execute(sql)

        cursor.execute("""update scen_scout_target set positions =%s where zone_id=%s and scene_id=%s""", (position_str, zone_id, scene_id))
        zone_id = zone_id + 1

    my.commit()
    my.close()

    return True

def update_scen_scout_target_map_position(db_pool, map_position, scene_id, target_id):
    my = db_pool.connection()
    cursor = my.cursor()
    i = 0
    for position in map_position:
        cursor.execute("""update scen_scout_target set map_position =%s where scene_id=%s and zone_id=%s""", (position, scene_id, target_id[i]))
        i = i + 1
    my.commit()
    my.close()

    return True

# 获取初始状态下所有原始目标的参数
def get_original_target_param(db, scene_id, sim_id):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select zone_id, zone_name, zone_category, positions, zone_priority, ' \
          'scout_difficulty from scen_scout_target where scene_id= %s' %scene_id
    cursor.execute(sql)

    results = cursor.fetchall()
    static_original_target_param = {}
    original_work_time = {}
    for result in results:
        zone_id = result[0]
        zone_name = result[1]
        zone_type = result[2]
        position = result[3]
        profit = result[4]
        scout_difficulty = result[5]
        sql = 'select count(*) from plan_scout_meta_tasks where sim_id=%s and zone_id=%s'
        data = [sim_id, zone_id]
        cursor.execute(sql, data)
        len_unit_task = cursor.fetchone()[0]
        # len_unit_task = num_unit_task_of_zone.get(zone_id)
        original_target_param = [zone_id, zone_name, zone_type, position, profit]
        static_original_target_param.update({zone_id: original_target_param})
        original_work_time.update({zone_id: scout_difficulty * len_unit_task})

    return static_original_target_param, original_work_time


