# 获取当前step中所有原始目标的状态

def get_current_status_of_zone(sim_id, current_step, db_pool):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select zone_id, zone_type, current_entropy, current_profit from sim_scout_target_situation where sim_id=%s ' \
          'and update_time= %s '
    data = [sim_id, current_step]
    cursor.execute(sql, data)
    results = cursor.fetchall()

    current_zone_status = {}
    for result in results:
        zone_id = result[0]
        zone_type = result[1]
        current_entropy = result[2]
        current_profit = result[3]
        zone_status = {}
        zone_status.update({'zone_type': zone_type})
        zone_status.update({'current_entropy': current_entropy})
        zone_status.update({'current_profit': current_profit})
        current_zone_status.update({zone_id: zone_status})

    return current_zone_status


# 将仿真时间段内的所有数据存入数据库中
def save_sim_target_situation(db, shared_original_target):
    conn = db.connection()
    cursor = conn.cursor()
    conn.begin()
    for all_original_target in shared_original_target:
        sql = "insert into `sim_scout_target_situation` (zone_id, zone_name, zone_type, current_position, " \
              "current_profit, current_entropy, sim_id,  update_time) values (%s, %s, %s, %s, %s,%s, %s, %s) "
        cursor.executemany(sql, all_original_target)
    conn.commit()
    cursor.close()
    conn.close()
