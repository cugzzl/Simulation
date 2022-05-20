def get_sim_threaten_instance_state(db_pool, experiment_id, time):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM sim_threaten_instance_state where sim_id='%d' and update_time='%d'" % (experiment_id, time)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def save_threat_instance_state(db, shared_threat):
    conn = db.connection()
    cursor = conn.cursor()
    conn.begin()
    for all_threat in shared_threat:
        sql = 'insert into sim_threaten_instance_state values (%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.executemany(sql, all_threat)
    conn.commit()
    cursor.close()
    conn.close()