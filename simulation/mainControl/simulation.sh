#!/bin/bash
cd ~/XTDrone/coordination/launch_generator
python3 generator_project.py 1
cp ~/XTDrone/coordination/launch_generator/multi_vehicle.launch ~/PX4_Firmware/launch/
cd ~/PX4_Firmware/
roslaunch px4 multi_vehicle.launch
