def get_scen_threat(db_pool, mission_id):
    my = db_pool.connection()
    cursor = my.cursor()
    sql = 'select * from scen_threat where mission_id=%d' % mission_id
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

def get_scen_threat_param(db, mission_id):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select threat_id, threat_name, position, threat_type_id, firing_range, meta_tasks_id from scen_threat ' \
          'where mission_id=%d' % mission_id
    cursor.execute(sql)
    
    results = cursor.fetchall()
    all_threat = {}
    for result in results:
        threat_id = result[0]
        threat_name = result[1]
        position = result[2]
        threat_type_id = result[3]
        firing_range = result[4]
        meta_task_id = result[5]
        orientation = str([0, 0, 0])
        threat_param = [threat_id, threat_name, threat_type_id, firing_range,position, orientation]
        all_threat.update({threat_id: threat_param})

    return all_threat
