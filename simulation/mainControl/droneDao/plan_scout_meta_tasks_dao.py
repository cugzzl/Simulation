import numpy as np
import pymysql

# 从目标表中获取所有的目标
from dbutils.persistent_db import PersistentDB


def get_plan_scout_meta_tasks(db_pool):
    my = db_pool.connection()
    cursor = my.cursor()
    cursor.execute("SELECT * FROM plan_scout_meta_tasks")
    results = cursor.fetchall()
    return results


def get_plan_scout_meta_tasks_by_simid(db_pool, sim_id):
    my = db_pool.connection()
    cursor = my.cursor()
    sql = 'SELECT * FROM plan_scout_meta_tasks where sim_id=%d' % sim_id
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


# 根据任务id获取每一个任务的工作时间
def get_workTime_by_task_id(db_pool, sim_id, task_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = 'select work_time from plan_scout_meta_tasks where sim_id=%s and task_id =%s'
    data = [sim_id, task_id]
    cursor.execute(sql, data)
    result = cursor.fetchall()
    work_time = result[0][0]
    return work_time


# 获取初始状态下所有的元任务组参数
def get_unit_task_param(db, sim_id):
    conn = db.connection()
    cursor = conn.cursor()
    sql = 'select task_id, zone_id, task_position, task_profit, work_time ' \
          'from plan_scout_meta_tasks where sim_id=%d' % sim_id
    cursor.execute(sql)
    results = cursor.fetchall()
    static_unit_task = {}
    unit_task_work_time = {}
    for result in results:
        task_id = result[0]
        zone_id = result[1]
        task_position = result[2]
        task_profit = result[3]
        work_time = result[4]
        static_param = [task_id, zone_id, task_position, task_profit]
        static_unit_task.update({task_id: static_param})
        unit_task_work_time.update({task_id: work_time})

    return static_unit_task, unit_task_work_time


def get_unit_task_param_without_db(all_unit_task):
    static_unit_task = {}
    unit_task_work_time = {}
    num_unit_task_of_zone = {}
    for unit_task in all_unit_task:
        task_id = unit_task[0]
        zone_id = unit_task[1]
        task_position = unit_task[2]
        task_profit = unit_task[3]
        work_time = unit_task[4]
        static_param = [task_id, zone_id, task_position, task_profit]
        static_unit_task.update({task_id: static_param})
        unit_task_work_time.update({task_id: work_time})
        if num_unit_task_of_zone.__contains__(zone_id):
            num_unit_task_of_zone.update({zone_id: num_unit_task_of_zone.setdefault(zone_id) + 1})
        else:
            num_unit_task_of_zone.update({zone_id: 1})

    return static_unit_task, unit_task_work_time, num_unit_task_of_zone


if __name__ == '__main__':
    config = {
        'host': '58.45.191.73',
        'port': 9123,
        'database': 'drone',
        'user': 'drone',
        'password': 'abc123.',
        'charset': 'utf8mb4'
    }

    db_pool = PersistentDB(pymysql, **config)



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


def save_plan_scout_meta_tasks(db_pool, result, sim_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    z = read_map('testread.txt')
    s = "truncate table plan_scout_meta_tasks;"
    cursor.execute(s)
    conn.commit()

    for i in range(len(result[0])):
        position = "%d,%d,%d" % (result[0][i], result[1][i], z[result[0][i]][result[1][i]])
        sql = "INSERT INTO plan_scout_meta_tasks VALUES ('" + str(i + 1) + "', '" + str(result[3][i]) + "', '" + str(
            position) + "', '" + str(result[2][i]) + "', '" + str(result[4][i]) + "', '" + str(sim_id) + "');"
        cursor.execute(sql)
        conn.commit()
    conn.close()


def save_plan_scout_meta_tasks_many(db_pool, tasks):

    conn = db_pool.connection()
    cursor = conn.cursor()
    # z = read_map('testread.txt')
    # s = "delete from plan_scout_meta_tasks;"
    # cursor.execute(s)
    # conn.commit()

    conn.begin()

    sql = "INSERT INTO plan_scout_meta_tasks VALUES (%s, %s, %s, %s, %s,%s) "
    cursor.executemany(sql, tasks)
    conn.commit()
    cursor.close()
    conn.close()