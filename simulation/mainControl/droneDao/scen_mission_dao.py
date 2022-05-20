def get_scen_mission(db_pool, mission_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = 'select scene_id from scen_mission where mission_id=%d' % mission_id
    cursor.execute(sql)

    result = cursor.fetchone()

    return result[0]


def get_total_time_mission(db_pool, mission_id):

    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = 'select total_time from scen_mission where mission_id = %d' % mission_id
    cursor.execute(sql)
    result = cursor.fetchone()

    return result[0]/1000


