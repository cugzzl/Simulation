import pymysql
from dbutils.persistent_db import PersistentDB


def get_scen_base(db_pool, scene_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM scen_base where scene_id='%d'" % scene_id
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

if __name__ == '__main__':
    sim_config = {
        'host': '58.45.191.73',
        'port': 9123,
        'database': 'drone',
        'user': 'drone',
        'password': 'abc123.',
        'charset': 'utf8mb4'
    }
    sim_db_pool = PersistentDB(pymysql, **sim_config)
    res = get_scen_base(sim_db_pool, 10)
    print(res)