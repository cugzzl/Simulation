from enum import Enum


# 事件类型
class Event(Enum):
    UAV_ACTION = 0
    BOOM = 1
    ORIGINAL_TARGET = 2


# 无人机状态
class UavStatus(Enum):
    FLAYING = 1
    SCOUT = 2
    ATTACK = 3
    HOVER = 4


# 突发状况类型
class Sudden(Enum):
    TARGET = 2
    UAV = 1
    THREATEN = 3


#    打击目标是否被侦察到
class IsDetected(Enum):
    YES = 1
    No = 0


class TaskType(Enum):
    SCOUT = 1
    ATTACK = 2


class AlgorithmTypeId(Enum):
    VNS = 2
    ACO_TASK = 3
    PSO_TASK = 5
    CC = 6
    GA_TASK = 7
    A_STAR = 8
    APF = 9
    ACO_PATH = 10
    GA_PATH = 11
    PSO_PATH = 12
