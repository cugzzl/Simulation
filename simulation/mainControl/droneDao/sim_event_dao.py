
def save_sim_event(db, shared_event):

    conn = db.connection()
    cursor = conn.cursor()

    sql = 'truncate table sim_event'
    cursor.execute(sql)
    conn.commit()
    conn.begin()
    sql = 'insert into sim_event (event_id, event_type_id, object_id, event_param, sim_id, update_time, ' \
          'object_kind) VALUES (%s, %s, %s, %s, %s, %s, %s) '
    cursor.executemany(sql, shared_event)

    conn.commit()
    cursor.close()
    conn.close()
