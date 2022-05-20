import pymysql

def get_sim_result(db_pool):
    my = db_pool.connection()
    cursor = my.cursor()
    cursor.execute("SELECT * FROM sim_result")
    results = cursor.fetchall()
    my.commit()
    my.close()
    return results

def save_sim_result(db_pool, data):

    my = db_pool.connection()
    cursor = my.cursor()
    sql = "INSERT INTO sim_result VALUES ('" + str(data[0]) + "', '" + str(data[1]) + "', '" + str(data[2]) +"', '" + str(data[3]) + "', '" + str(data[4]) + "', '" + str(data[5]) +"');"
    cursor.execute(sql)
    my.commit()
    my.close()
    return True

def get_scenario_id(db_pool, sim_id):

    conn = db_pool.connection()
    cursor = conn.cursor()
    sql = "select scenario_id from sim_result where sim_id=%s" % sim_id
    cursor.execute(sql)
    scenario_id = cursor.fetchone()[0]
    return scenario_id
