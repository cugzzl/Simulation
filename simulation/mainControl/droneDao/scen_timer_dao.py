

def get_sudden(db, mission_id):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select object_kind, object_id, start_time, end_time from scen_timer where mission_id=%s' % mission_id
    cursor.execute(sql)

    all_sudden = cursor.fetchall()

    return all_sudden
