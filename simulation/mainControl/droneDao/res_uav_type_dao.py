def get_res_uav_type(db_pool, uav_type_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM res_uav_type where uav_type_id='%d'" % uav_type_id
    cursor.execute(sql)
    result = cursor.fetchall()
    return result