from mainControl.droneDao.plan_route_dao import get_uav_id, get_task_route, get_task_id_by_uav_id
from mainControl.droneDao.plan_single_task_dao import get_position_and_workTime_by_task_id
from mainControl.Simulation.simulation_utils import get_uav_source

# 对任务规划结果进行处理，得到：
#       1. 每一架无人机的路径
#       2. 每一架无人机的多目标位置
#       3. 每一架无人机在多个目标位置上的工作时间
#       4. 无人机数量
from mainControl.droneDao.scen_algo_template_dao import get_algo_param
from mainControl.droneDao.scen_scenario_dao import get_strategy_id
from mainControl.droneDao.sim_strategy_dao import get_re_plan_algorithm_id


def pre_handler_uav_simulation(db, sim_id, uav_speed):
    """

    :param uav_speed:
    :param db:
    :param sim_id:
    :return:
    """

    # 获取所有参与有飞行任务的无人机id
    all_uav_id = get_uav_id(db, sim_id)
    uav_id_to_ip, uav_ip_to_id = get_uav_source(all_uav_id)
    uav_route = []
    all_task_position = {}
    all_task_work_time = {}
    all_task_id = {}
    all_task_start_flag = {}
    all_task_profit = {}

    for uav_id in all_uav_id:
        #   根据id获取每一架无人机的路径
        route_code = get_task_route(db, sim_id, uav_id, uav_id_to_ip)
        uav_route.append(route_code)
        #    获取每一架无人机的所有待执行任务编号
        all_uav_task_id = get_task_id_by_uav_id(db, uav_id, sim_id)
        #     根据任务编号获取每个任务的位置和工作时间
        uav_task_position = []
        uav_task_work_time = []
        uav_task_start_flag = []
        for task_id in all_uav_task_id:
            task_position, task_work_time, task_profit = get_position_and_workTime_by_task_id(db, sim_id, task_id)
            uav_task_start_flag.append(False)
            uav_task_position.append(task_position)
            uav_task_work_time.append(task_work_time)
            all_task_profit.update({task_id: task_profit})

        all_task_start_flag.update({uav_id: uav_task_start_flag})
        all_task_position.update({uav_id: uav_task_position})
        all_task_work_time.update({uav_id: uav_task_work_time})
        all_task_id.update({uav_id: all_uav_task_id})

    # 拼接起飞指令
    ros_code_three = get_ros_code_three(all_uav_id, uav_id_to_ip, uav_speed)

    return uav_route, all_task_id, all_task_start_flag, all_task_position, \
           all_task_work_time, ros_code_three, uav_ip_to_id, all_task_profit


def get_ros_code_three(all_uav_id, uav_id_to_ip, uav_speed):
    """
    ['3;1','3;2']
    :param uav_speed:
    :param all_uav_id: 所有无人机的id
    :param uav_id_to_ip: 所有无人机id所对应的ip
    :return:
    """
    ros_code_three = []
    for uav_id in all_uav_id:
        uav_speed_ = uav_speed.get(uav_id)
        uav_ip = uav_id_to_ip.get(uav_id)
        string = str(3) + ';'
        string = string + str(uav_ip) + ';'
        string += str(uav_speed_)
        ros_code_three.append(string)
    return ros_code_three


# 对无人机数量和位置进行初始化
# cs='1;6;33.22,44.11;'
def get_ros_code_one(uav_num, longitude, latitude):
    """
    指令格式1
    :param uav_num:  无人机数量
    :param longitude: 基地经度
    :param latitude: 基地维度
    :return:
    """
    ans = '1;'
    ans += str(uav_num) + ';'
    ans += str(longitude) + ','
    ans += str(latitude)

    return ans


# 获取重规划算法参数
def get_re_plan_algorithm_param(db, scenario_id):
    strategy_id = get_strategy_id(db, scenario_id)
    re_task_algo_id, re_path_algo_id = get_re_plan_algorithm_id(db, strategy_id)

    re_plan_task_algo_param = {}
    re_plan_path_algo_param = {}
    re_plan_algorithm_param = []

    # 获取算法类型编号和对应的参数
    re_plan_task_algo_type_id, re_plan_task_algorithm_param = get_algo_param(db, re_task_algo_id)
    re_plan_path_algo_type_id, re_plan_path_algorithm_param = get_algo_param(db, re_path_algo_id)

    re_plan_task_algo_param.update({re_plan_task_algo_type_id: re_plan_task_algorithm_param})
    re_plan_path_algo_param.update({re_plan_path_algo_type_id: re_plan_path_algorithm_param})

    re_plan_algorithm_param.append(re_plan_task_algo_param)
    re_plan_algorithm_param.append(re_plan_path_algo_param)

    return re_plan_algorithm_param
