def get_sim_scout_meta_tasks(db_pool, experiment_id, time):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM sim_scout_meta_tasks where sim_id='%d' and current_step='%d'" % (experiment_id, time)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_sim_scout_meta_tasks_unfininsed(db_pool, experiment_id, time):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM sim_scout_meta_tasks where sim_id='%d' and current_step='%d' and work_time > 0" % (
    experiment_id, time)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def save_sim_unit_task(db, shared_unit_task):
    conn = db.connection()
    cursor = conn.cursor()
    conn.begin()
    for all_unit_task in shared_unit_task:
        # 每一个step
        sql = "insert into `sim_scout_meta_tasks` (task_id, zone_id, position, profit, sim_id, current_step, " \
              "work_time) values (%s, %s, %s, %s, %s, %s, %s) "
        cursor.executemany(sql, all_unit_task)
    conn.commit()
    cursor.close()
    conn.close()
