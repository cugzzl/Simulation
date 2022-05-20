import pymysql
from dbutils.persistent_db import PersistentDB


def get_scen_uav_group_template(db_pool, group_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM scen_uav_group_template where group_id='%d'" % group_id
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
    res = get_scen_uav_group_template(sim_db_pool, 2)
    print(res)