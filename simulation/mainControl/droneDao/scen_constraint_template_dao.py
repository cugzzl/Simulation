def get_task_type(db, constraint_id):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select uav_type_category from scen_constraint_template where constraint_id=%s' % constraint_id
    cursor.execute(sql)

    result = cursor.fetchone()
    return result
