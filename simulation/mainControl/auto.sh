#!/bin/bash

FILE0="simulation.sh"
FILE1="posture.sh"
FILE2="start.sh"
iris_nu=$1

sed -i "s/pyth.*$/python3 generator_project.py $iris_nu/" $FILE0
sed -i "s/pyth.*$/python get_local_pose_project.py iris $iris_nu/" $FILE1
sed -i "s/pyth.*$/python3 simulation_project.py iris $iris_nu vel/" $FILE2
	
cd ~/XTDrone/communication
FILE3="multi_vehicle_communication.sh"
sed -i "s/iris_num=.*$/iris_num=$iris_nu/" $FILE3

cd ~/version/5.7/uav/
gnome-terminal --geometry 60*20+10+10 -- bash simulation.sh & sleep 15
gnome-terminal --geometry 60*20+10+20 -- bash communication.sh & sleep 5
gnome-terminal --geometry 60*20+10+30 -- bash posture.sh & sleep 5
gnome-terminal --geometry 60*20+10+40 -- bash start.sh & sleep 5

