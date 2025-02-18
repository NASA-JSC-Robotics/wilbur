To run:

ros2 launch wilbur_deploy simulate.launch.py 

ros2 launch wilbur_deploy moveit.launch.py use_sim_time:=true

ros2 run rviz2 rviz2 use_sim_time:=true -d install/wilbur_deploy/share/wilbur_deploy/rviz/config.rviz

