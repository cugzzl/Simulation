from mainControl.Simulation.simulation_status_enum import TaskType


def save_sim_attack_target_situation(db, shared_attack_target_situation, task_type):
    conn = db.connection()
    cursor = conn.cursor()
    if task_type == TaskType.ATTACK.value:
        for tmp in shared_attack_target_situation:
            for tmp1 in tmp:
                tmp1.append(1)
    conn.begin()
    for all_original_target in shared_attack_target_situation:
        sql = "insert into `sim_attack_target_situation` (target_id, target_name, target_type_id, current_position, " \
              "current_profit, sim_id, update_time, current_hp, is_detected) values (%s, %s, %s, %s, %s,%s, %s, %s, %s) "
        cursor.executemany(sql, all_original_target)
    conn.commit()
    cursor.close()
    conn.close()