import numpy as np
import pymysql


def get_plan_single_task(db_pool, experimentID, updateTime):
    my = db_pool.connection()
    cursor = my.cursor()
    cursor.execute("SELECT * FROM plan_single_task where sim_id='%d' and update_time='%d'" % (experimentID, updateTime))
    results = cursor.fetchall()
    return results


def save_plan_single_task(db_pool, tasks, experimentID, updateTime):
    conn = db_pool.connection()
    cursor = conn.cursor()
    s = "truncate table plan_single_task;"
    cursor.execute(s)
    conn.commit()

    for task in tasks:
        sql = "INSERT INTO plan_single_task  VALUES ('" + \
              str(task[0]) + "', '" + str(task[1]).strip('[]') + "', '" + str(task[2]) + "', '" + str(
            task[3]) + "', '" + str(experimentID) + "', '" + str(updateTime) + "');"
        cursor.execute(sql)
    conn.commit()
    conn.close()


# 根据任务id获取每一个任务的位置和工作时间
def get_position_and_workTime_by_task_id(db_pool, sim_id, task_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = 'select task_position, work_time, task_profit from plan_single_task where ` task_id`=%s and sim_id=%s'
    data = [task_id, sim_id]
    cursor.execute(sql, data)
    result = cursor.fetchall()
    task_position = result[0][0]
    work_time = result[0][1]
    task_profit = result[0][2]
    return task_position, work_time, task_profit

# 根据任务id获取每一个任务的工作时间
def get_workTime_by_task_id(db_pool, sim_id, task_id):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = 'select work_time from plan_single_task where sim_id=%s and ` task_id`=%s'
    data = [sim_id, task_id]
    cursor.execute(sql, data)
    result = cursor.fetchall()
    work_time = result[0][0]
    return work_time
