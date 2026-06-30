# Wilbur Mujoco Config

Mujoco configuration for launching Wilbur in a simulated Mujoco environment.


That is probably coming from this script. And that script gets run from this launch file. The first part of that launch file makes a directory mjcf_data/ in the directory you run the launch file from, and the post_process_mjcf.py node uses that directory. I recommend running the conversion script from the src/ directory inside the docker so that the directory ends up in src/mjcf_data/ which is available both inside and outside the docker