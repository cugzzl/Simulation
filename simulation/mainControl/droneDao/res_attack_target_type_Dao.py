
def get_attack_target_type(db_pool):
    my = db_pool.connection()
    cursor = my.cursor()
    cursor.execute("SELECT * FROM res_attack_target_type")
    results = cursor.fetchall()
    my.commit()
    my.close()
    return results