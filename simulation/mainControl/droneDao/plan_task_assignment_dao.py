
def save_plan_task_assignment(db_pool, uav_task, exist_uav, experiment_id, time):

    conn = db_pool.connection()
    cursor = conn.cursor()
    s = "truncate table plan_task_assignment;"
    cursor.execute(s)
    conn.commit()

    UAVID = 0
    for path in uav_task:
        realPath = []
        for p in path:
            realPath.append(p-1)
        sql = "insert into plan_task_assignment values ('" + str(exist_uav[UAVID][0]) + "', '" + str(realPath) + "', '" +  \
              str(experiment_id) + "', '" + str(time) + "');"
        cursor.execute(sql)
        UAVID = UAVID + 1

    conn.commit()
    cursor.close()
    conn.close()