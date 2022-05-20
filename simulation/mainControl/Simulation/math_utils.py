import math


def check_arrive(position, real_position):
    """

    :param real_position: gazebo中真实的无人机位置
    :param position: 算法中的无人机位置
    :return:
    """
    position = position.split(',')
    interval_distance = 3
    return abs(real_position[0] - int(position[0])) <= interval_distance & \
           abs(real_position[1] - int(position[1])) <= interval_distance & \
           abs(real_position[2] - int(position[2])) <= interval_distance


def calculate_distance(position, pre_position):
    x = position[0] - pre_position[0]
    y = position[1] - pre_position[1]
    z = position[2] - pre_position[2]
    return math.sqrt(x * x + y * y + z * z)
