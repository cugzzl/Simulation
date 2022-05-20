# -*- coding=utf-8 -*-

from mainControl.Simulation.start_simulation_process import start_simulation, attack_simulation

if __name__ == '__main__':
    # 从唐总获得试验id
    # experiment_id = sys.argv[0]
    experiment_id = 202
    start_simulation(experiment_id)
    # attack_simulation(experiment_id)

