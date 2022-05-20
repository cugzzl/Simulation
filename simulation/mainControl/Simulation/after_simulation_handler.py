from mainControl.droneDao.sim_scout_meta_tasks_dao import save_sim_unit_task
from mainControl.droneDao.sim_scout_target_situation_dao import save_sim_target_situation, get_current_status_of_zone
from mainControl.droneDao.sim_threaten_instance_state_dao import save_threat_instance_state
from mainControl.droneDao.sim_uav_instance_state_dao import save_sim_uav_state
from mainControl.droneDao.sim_event_dao import save_sim_event
from mainControl.droneDao.sim_attack_target_situation import save_sim_attack_target_situation
from mainControl.Simulation.simulation_status_enum import TaskType


# 将仿真结果数据存入数据库中
def save_database(db, shared_uav_status, shared_original_target,
                  shared_event, shard_original_attack_target, shared_threat):
    save_sim_uav_state(db, shared_uav_status)
    save_sim_target_situation(db, shared_original_target)
    save_sim_event(db, shared_event)
    save_threat_instance_state(db, shared_threat)
    save_sim_attack_target_situation(db, shard_original_attack_target, TaskType.SCOUT.value)

    # save_sim_unit_task(db, shared_unit_task)


def save_attack_database(db, shared_uav_status, shared_attack_target_situation,
                         shared_event,shared_threat, task_type):
    save_sim_uav_state(db, shared_uav_status)
    save_sim_attack_target_situation(db, shared_attack_target_situation, task_type)
    save_sim_event(db, shared_event)
    save_threat_instance_state(db, shared_threat)


def evaluate(current_step, sim_id, original_target_work_time, db_pool):
    """

    :param current_step:
    :param sim_id:
    :param original_target_work_time: 每一个原始目标所需要的侦察/打击次数
    :param db_pool:
    :return: success_rate为float，为总的成功率
             all_profit为总收益
             zone_completion_rate为每一个原始任务的完成度
    """
    current_zone_status = get_current_status_of_zone(sim_id, current_step, db_pool)
    all_success_rate, all_profit = 0, 0
    zone_completion_rate = {}
    for zone_id in current_zone_status:
        current_entropy = current_zone_status.get(zone_id).get('current_entropy')
        if current_entropy == 0:
            all_success_rate += 1
            current_profit = current_zone_status.get(zone_id).get('current_profit')
            all_profit += current_profit
        original_entropy = original_target_work_time.get(zone_id)
        zone_completion_rate.update({zone_id: (original_entropy - current_entropy) / original_entropy})

    success_rate = all_success_rate / len(current_zone_status)
    return success_rate, all_profit, zone_completion_rate
