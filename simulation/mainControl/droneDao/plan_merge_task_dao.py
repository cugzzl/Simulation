def get_plan_merge_task(db_pool, experiment_id, time):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM plan_merge_task where sim_id='%d' and update_time='%d'" % (experiment_id, time)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def save_plan_merge_task(db_pool, tasks, experimentID, updateTime):

    conn = db_pool.connection()
    cursor = conn.cursor()
    s = "truncate table plan_merge_task;"
    cursor.execute(s)
    conn.commit()

    for task in tasks:
        sql = "INSERT INTO plan_merge_task VALUES ('" + \
            str(task[0]) + "', '" + str(task[1]).strip('[]') + "', '" + str(task[2]) + "', '" + str(task[3]) + "', '" + str(experimentID) +"', '" + str(updateTime) +"');"
        cursor.execute(sql)
    conn.commit()
    conn.close()


