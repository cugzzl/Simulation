

def get_position_by_scenario_id(db, scenario_id):

    conn = db.connection()
    cursor = conn.cursor()
    sql = 'select longitude, latitude from scen_scene where scene_id=%s' % scenario_id
    cursor.execute(sql)
    result = cursor.fetchall()[0]
    x = result[0]
    y = result[1]
    return x, y