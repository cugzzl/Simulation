def get_algo_name(db_pool, algo_id):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select algo_name from res_algo where algo_id=%d' % algo_id
    cursor.execute(sql)

    result = cursor.fetchall()

    return result[0][0]