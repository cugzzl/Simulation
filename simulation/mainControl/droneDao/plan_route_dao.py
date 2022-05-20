# 根据id获取一架无人机的路径和对应的任务id（通过task_order保证了路径的顺序）
import pymysql
from dbutils.persistent_db import PersistentDB

from mainControl.droneDao.plan_single_task_dao import get_workTime_by_task_id
from mainControl.droneDao.sim_source_dao import get_uav_source


def get_task_route_by_uav_id(db, uav_id, sim_id):
    conn = db.connection()
    cursor = conn.cursor()
    sql = 'select task_route from plan_route where uav_id=%s and sim_id=%s order by task_order'
    data = [uav_id, sim_id]
    cursor.execute(sql, data)
    results = cursor.fetchall()
    path = []
    path.append(uav_id)
    path0 = []
    for tmp1 in results:
        tmp = tmp1[0].split(';')
        for s in tmp:
            path0.append(list(map(float, s.strip('(').strip(')').split(','))))
    path.append(path0)
    return path


def get_uav_route(db, experiment_id, update_time):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select * from plan_route where sim_id = %d and update_time = %d' % (experiment_id, update_time)
    cursor.execute(sql)

    result = cursor.fetchall()

    return result


# 获取一架无人机的所有任务编号
def get_task_id_by_uav_id(db, uav_id, sim_id):
    conn = db.connection()
    cursor = conn.cursor()
    sql = 'select task_id from plan_route where uav_id=%s and sim_id=%s order by task_order'
    data = [uav_id, sim_id]
    cursor.execute(sql, data)
    results = cursor.fetchall()
    task_id = []
    for result in results:
        task_id.append(result[0])
    return task_id


# 获取参与任务的所有无人机id
def get_uav_id(db, sim_id):
    conn = db.connection()
    cursor = conn.cursor()
    sql = 'select uav_id from plan_route where sim_id=%s and task_order=%s'
    data = [sim_id, 1]
    cursor.execute(sql, data)
    results = cursor.fetchall()
    uav_id = []
    for result in results:
        uav_id.append(result[0])
    return uav_id


# 获取所有无人机的路径和对应的任务id（通过task_order保证了路径的顺序）
#  生成路径形式:  '2;0;1,0,1,10;1,0,2,10;1,0,3,10;1,0,4,10;2,5,0,0;1,0,4,12;1,0,3,12;1,0,2,12;1,0,1,12;4,0,0,0',
def get_task_route(db_pool, sim_id, uav_id, uav_id_to_ip):
    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = 'select task_route, task_id from plan_route where sim_id=%s and uav_id= %s order by task_order'
    data = [sim_id, uav_id]
    cursor.execute(sql, data)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    route_code = ''
    order_code = '2;'
    uav_source_code = uav_id_to_ip.get(uav_id)
    uav_id_code = str(uav_source_code) + ';'
    route_code += order_code
    route_code += uav_id_code
    task_num = len(results)
    i = 0
    for result in results:
        i += 1
        route = result[0]
        task_id = result[1]
        route = route.split(';')
        route_tmp = ''
        for s in route:
            tmp = '1,'
            tmp_s = s.strip('(').strip(')')
            tmp = tmp + tmp_s + ';'
            route_tmp += tmp
        #     获取在每一个任务点的执行时间        TODO
        work_time = get_workTime_by_task_id(db_pool, sim_id, task_id)
        work_time_code = str(work_time) + ',0,0;'
        route_tmp += '2,'
        route_tmp += work_time_code
        route_code += route_tmp
        # 最后一个任务点,执行完之后直接停留在原地
        if i == task_num:
            route_code += '4,0,0,0'
    return route_code

def save_plan_route(db_pool, route):

    conn = db_pool.connection()
    cursor = conn.cursor()
    # s = "delete from plan_route;"
    # cursor.execute(s)
    # conn.commit()

    for r in route:
        sql = "INSERT INTO plan_route  VALUES ('" + \
            str(r[0]) + "', '" + str(r[1]) + "', '" + str(r[2]).strip('[]') + "', '" + str(r[3]) + "', '" + str(r[4]) +"', '" + str(r[5]) + "');"
        cursor.execute(sql)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    config = {
        'host': '58.45.191.73',
        'port': 9123,
        'database': 'drone',
        'user': 'drone',
        'password': 'abc123.',
        'charset': 'utf8mb4'
    }
    db = PersistentDB(pymysql, **config)
    # sim_id = 37
    # uav_id = 1
    # route_code = get_task_route(db, sim_id, uav_id)
    # print(route_code)
