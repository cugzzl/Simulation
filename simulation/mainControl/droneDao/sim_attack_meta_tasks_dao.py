def get_sim_attack_meta_tasks(db_pool, experiment_id, time):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM sim_attack_meta_tasks where sim_id='%d' and update_time='%d'" % (experiment_id, time)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_sim_attack_meta_tasks_unfininsed(db_pool, experiment_id, time):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM sim_attack_meta_tasks where sim_id='%d' and update_time='%d and work_time > 0'" % (experiment_id, time)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result




