
def get_scen_sudden(db_pool, scenario_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = 'select * from scen_sudden where scenario_id=%d' % scenario_id
    cursor.execute(sql)
    result = cursor.fetchall()

    return result


def get_sudden(db, scene_id):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select object_kind, object_id, start_time, end_time from scen_sudden where scenario_id=%s' % scene_id
    cursor.execute(sql)

    all_sudden = cursor.fetchall()

    return all_sudden
