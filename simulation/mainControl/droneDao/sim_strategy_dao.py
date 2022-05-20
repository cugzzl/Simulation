def get_algo_param_id_scenario(db_pool, strategy_id):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select algo_param_id1, algo_param_id3 from sim_strategy where strategy_id=%d' % strategy_id
    cursor.execute(sql)

    result = cursor.fetchall()

    return result


def get_re_plan_algorithm_id(db_pool, strategy_id):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select algo_param_id2, algo_param_id4 from sim_strategy where strategy_id=%d' % strategy_id
    cursor.execute(sql)

    result = cursor.fetchone()
    re_task_algo_id = result[0]
    re_path_algo_id = result[1]
    return re_task_algo_id, re_path_algo_id
