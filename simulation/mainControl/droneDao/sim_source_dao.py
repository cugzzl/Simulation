
def get_uav_source(db, sim_id, uav_id):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select uav_source from sim_source where uav_id=%s and sim_id=%s'
    data = [uav_id, sim_id]
    cursor.execute(sql, data)

    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return result
