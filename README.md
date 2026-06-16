# Wilbur

Descriptions, deployments, tooling, and MoveIt configuration for the Wilbur robot system,
part of the [iMETRO Facility](https://ntrs.nasa.gov/citations/20240013956) at NASA's Johnson Space Center.
This project is intended for use in one of ER4's managed workspaces (such as the in the [wilbur_ws](https://js-er-code.jsc.nasa.gov/imetro/robots/wilbur/wilbur_ws)).

```
    .-.___.-.     _.---------._
    /         \ *`               `\    6.
   |  0      0 |      Wilbur       \    9
   |  ( ○  ○ ) |                    |  /
    '-_______.-                      |/
            |                       |
            *             ___       *
            \    / \    /   \ \   /
             *__*   *__*     *_*_*
```

## Usage

The project includes a kinematic simulation for the robot.
Launching the controllers and hardware interface is done using the provided launch files.

To launch the kinematic simulation:

```bash
ros2 launch wilbur_description view_robot.launch.py

# Or without the UR arm
ros2 launch wilbur_description view_robot.launch.py include_ur:=false 
```

A Gazebo simulation including the environment is available in wilbur_gz.

```bash
# Start the Gazebo ros2 control-based simulation
ros2 launch wilbur_gz sim_gz.launch.py

# Or launch without the UR arm.
ros2 launch wilbur_gz sim_gz.launch.py include_ur:=false
```

## Citation

This project falls under the purview of the iMETRO project.
If you use this in your own work, please cite the following paper:

```bibtex
@INPROCEEDINGS{imetro-facility-2025,
  author={Dunkelberger, Nathan and Sheetz, Emily and Rainen, Connor and Graf, Jodi and Hart, Nikki and Zemler, Emma and Azimi, Shaun},
  booktitle={2025 22nd International Conference on Ubiquitous Robots (UR)},
  title={Design of the iMETRO Facility: A Platform for Intravehicular Space Robotics Research},
  year={2025},
  volume={},
  number={},
  pages={390-397},
  keywords={NASA;Moon;Seals;Maintenance engineering;Maintenance;Robots;Standards;Open source software;Testing;Logistics},
  doi={10.1109/UR65550.2025.11077983}}
```
