#!/bin/bash
cd ~/XTDrone/communication
bash multi_vehicle_communication.sh
cd ~/XTDrone/sensing/pose_ground_truth
python get_local_pose_project.py iris 1

