def get_scen_scenario(db_pool, scenario_id):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select mission_id from scen_scenario where scenario_id=%d' % scenario_id
    cursor.execute(sql)

    result = cursor.fetchone()

    return result[0]


def get_constraint_and_mission_id(db, scenario_id):
    conn = db.connection()
    cursor = conn.cursor()

    sql = 'select constraint_id, mission_id from scen_scenario where scenario_id=%s' % scenario_id
    cursor.execute(sql)
    result = cursor.fetchone()
    constraint_id = result[0]
    mission_id = result[1]
    return constraint_id, mission_id


def get_strategy_id(db_pool, scenario_id):
    conn = db_pool.connection()
    cursor = conn.cursor()

    sql = 'select strategy_id from scen_scenario where scenario_id=%d' % scenario_id
    cursor.execute(sql)

    result = cursor.fetchone()

    return result[0]