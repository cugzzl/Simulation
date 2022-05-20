import numpy as np
import pymysql

# 从目标表中获取所有的目标
def get_plan_attack_meta_tasks(db_pool):
    my = db_pool.connection()
    cursor = my.cursor()
    cursor.execute("SELECT * FROM plan_attack_meta_tasks")
    results = cursor.fetchall()
    return results

def get_plan_attack_meta_tasks_by_simid(db_pool, sim_id):
    my = db_pool.connection()
    cursor = my.cursor()
    sql = 'SELECT * FROM plan_attack_meta_tasks where sim_id=%d' % sim_id
    cursor.execute(sql)
    results = cursor.fetchall()
    return results

def read_map(file_path):
    fin = open(file_path, 'r')
    new_map = []
    for row in fin.readlines():
        heights = [float(point) for point in row.strip().split(' ')]
        new_map.append(heights)
    new_map.reverse()
    # 将地理栅格模型的y轴反转
    new_map = np.array(new_map)
    return new_map

# 获取初始状态下所有的元任务组参数
def get_unit_attack_task_param(db, sim_id):
    conn = db.connection()
    cursor = conn.cursor()
    sql = 'select task_id, zone_id, task_position, task_profit, work_time, meta_tasks_id ' \
          'from plan_attack_meta_tasks where sim_id=%d' % sim_id
    cursor.execute(sql)
    results = cursor.fetchall()
    static_unit_task = {}
    unit_task_work_time = {}
    meta_task_to_zone = {}
    for result in results:
        task_id = result[0]
        zone_id = result[1]
        task_position = result[2]
        task_profit = result[3]
        work_time = result[4]
        meta_task_id = result[5]
        static_param = [task_id, zone_id, task_position, task_profit]
        static_unit_task.update({task_id: static_param})
        unit_task_work_time.update({task_id: work_time})
        meta_task_to_zone.update({meta_task_id: zone_id})

    return static_unit_task, unit_task_work_time, meta_task_to_zone


def save_plan_attack_meta_tasks(db_pool,attack_meta_targets):
    conn = db_pool.connection()
    cursor = conn.cursor()
    s = "truncate table plan_attack_meta_tasks;"
    cursor.execute(s)
    conn.commit()

    for data in attack_meta_targets:
        sql = "INSERT INTO plan_attack_meta_tasks VALUES ('" + str(data[0]) + "', '" + str(data[1]) + "', '" + str(
            data[2]) + "', '" + str(data[3]) + "', '" + str(data[4]) + "', '" + str(data[5]) + "', '" + str(data[6]) +"');"
        cursor.execute(sql)
        conn.commit()
    conn.close()


def save_plan_attack_meta_tasks_many(db_pool, tasks):

    conn = db_pool.connection()
    cursor = conn.cursor()
    # z = read_map('testread.txt')
    # s = "delete from plan_scout_meta_tasks;"
    # cursor.execute(s)
    # conn.commit()

    conn.begin()

    sql = "INSERT INTO plan_attack_meta_tasks VALUES (%s, %s, %s, %s, %s, %s, %s) "
    cursor.executemany(sql, tasks)
    conn.commit()
    cursor.close()
    conn.close()