import pymysql
from dbutils.persistent_db import PersistentDB


def get_algo_id(db_pool, algo_param_id):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select algo_id from scen_algo_template where algo_param_id=%d' % algo_param_id
    cursor.execute(sql)

    result = cursor.fetchall()

    return result[0][0]


def get_algo_param(db_pool, algo_param_id):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select algo_id, algo_prop_values from scen_algo_template where algo_param_id=%d' % algo_param_id
    cursor.execute(sql)

    result = cursor.fetchone()
    algo_type_id = result[0]
    algorithm_param = result[1]

    return algo_type_id, algorithm_param



