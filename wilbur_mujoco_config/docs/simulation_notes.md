# Notes on simulation choices

> [!NOTE]
> # **Important Notes**
> -  Match control and simulation rates. The mujoco timestep -- set in *wilbur_mujoco_config/urdf/wilbur_mujoco_raw_inputs.xacro* under *options* need to match the rate used for the ROS controller -- set in *wilbur_deploy/config/controllers_common.yaml*.  The sim will not behave correctly if these do not match.
> - If you are using a GPU add **MUJOCO_GL="egl"** to your .env file

# Base Simulation State - 12 Aug, 2026

The simulated robot can achieve desired maximum speeds for straight driving and for turning.  There the contact parameters and effective track width have been tuned.

On a straight drive, the translational error is $\approx 2\%$ and the rotational error is $\approx 1\%$ at maximum speeds -- 4 m/s translation and 4  rad/sec rotation.

![x_dot_plot](./final_translation.png)
$\hspace{10mm}$
![theta_dot_plot](./final_rotation.png)]

Error was measured using comparing the  */velocity_controller/odom* topic to */simulator/floating_base_state*.

# Tuning

Monitor */joint_states* and */controller_manager/introspection_data/full* to tune kv.  Start with a low-ish value (like 1000) and send a velocity command to the vehicle.  

Compute the expected wheel speed for that command:

$$
\omega_{w_{left/right}} = \frac{v_{b}}{radius} \pm \frac{\omega_b \times sep}{2 \times radius}
$$


where:

$\omega_w$ is wheel velocity in radians/sec

$\omega_b$ is rotational velocity of the body (vehicle) in radians/sec

$v_b$ is linear velocity of the body in meters/sec

$sep$  is the track width of the robot (i.e. wheel separation) in meters

$radius$ is the radius of the wheel in meters

You can use *wilbur_testing check_odometry.launch.py* to send a constant command for this testing.

for pure rotational velocity: 
```
ros2 launch wilbur_testing check_odometry.launch.py theta_dot:=4.0 time_ms:=100000
```
for pure translational velocity
```
ros2 launch wilbur_testing check_odometry.launch.py x_dot:=4.0 time_ms:=100000
```

## Verify controller parameters
Look at */controller_manager/introspection_data/full* -- if the velocity values being sent do not match your expected values, double check $radius$ and $sep$ values using *ros2 param get*  for
- wheel_radius
- wheel_separation
- wheel_separation_multiplier
- left_wheel_radius_multiplier
- right_wheel_radius_multiplier

To start with all multipiers should all be 1.0.

Also verify that the commands are within the limits for the velocity controller.

## Tuning kv

With the controller commanding the correct wheel velocities, monitor */joint_states* while sending a maximum velocity command.  If the velocities for the wheels (from */joint_states*) match the expected velcities, lower kv until to the lowest value that returns the expected values, then add a bit for margin.

If the wheel velocities are too low, raise kv until the velocities are the expected values.  You will have to re-adjust kv, using this same process, when you change the contact properties.

## Tuning contact parameters

Start the sim and in another window cd ws/src and run 
```
ros2 launch wilbur_testing check_odometry.launch.py x_dot:=4.0 time_ms:=100000
```
This will create a .csv file in the src directory -- so you can look at it from the host computer (not in the docker).  I use LibreCalc to look at these, but any spreadsheet app will work.
Plot the gt_x_rate and od_x_rate.  If the od_x_rate matches the commanded values, but the gt_x_rate doesn't, that means the wheels are slipping and we need to increase the traction.  Some wheel slippage is to be expected, but the goal for staight driving should be around 1%.  The percent of x error is printed when check_odometry finishes.

Currently, we can't adjust the wheel contact properties directly, so we'll have to adjust the properties of the floor in *wilbur_mujoco_scene.xacro*.  

I have tried using a mesh that is a plain cylinder for the wheel, but still a mesh.  There is slightly less slipping with the plain cylinder wheel, but not enough to switch to it, now that the contact parameters are tuned.

### Starting with friction = "0.8 0.005 0.0001" solimp="0.9 0.95 0.001 0.5 2.0"  solref = "0.02 1.0"  (defaults)

We'll start with this as an estimate for friction of a dry rubber tire on dry asphalt (according to google) and the default solimp and solref.  Very high rotational error (> 500 %) and the turns look jerky.

Try these same parameters with maximum $\dot{x}$ (4 m/s) and, in a separate run, maximum $\dot{\Theta}$ (4 rad/sec).

![x_dot_plot](./x_dot_v1.png)
$\hspace{10mm}$
![theta_dot_plot](./theta_dot_v1.png)]

$\dot{x}_{err} \approx 10\%$ and $\dot{\Theta}_{err} > 500\%$ -- clearly unuseable.  The velocity controller thinks the robot is spinning at the correct speed but wheels are slipping, making the ground truth rotational rate too low.


### friction = "0.4 0.005 0.0001" solimp="0.9 0.95 0.001 0.5 2.0  solref = "0.02 1.0" 

This is better -- $\dot{x}_{err} \approx 5\%$ but $\dot{\Theta}_{err} \approx 240 \%$ -- but the robot is bouncy.  The wheels are too stiff, and they still slip too much on the turns.

![x_dot_plot](./x_dot_v2.png)
$\hspace{10mm}$
![theta_dot_plot](./theta_dot_v2.png)]


### friction = "0.4 0.005 0.0001" solimp="0.015 .7 0.5 0.95 1" solref="0.003 0.3"
                  
Soften up the tires.  These values for solimp and solref came with a lot of trial and error.  It helps simulate not only the softness of the rubber, but the compiance of the pneumatic wheel.  The raw error numbers don't look better, but the robot behavior looks more realistic -- less bouncing and chatter.

$\dot{x}_{err} \approx 2\%$ but $\dot{\Theta}_{err} \approx 60\%$

![x_dot_plot](./x_dot_v3.png)
$\hspace{10mm}$
![theta_dot_plot](./theta_dot_v3.png)]

We're at the point of diminishing returns I tried reducing the torsional and rolling friction, but it did not change the outcomes appreciably.

## Compensating for normal slip during turning

We still have an approximately 60% error during turning.  Some slippage is normal for a skid steer vehicle.  To compensate for this from a control perspective, we'll change the *effective* track width by changing the *wheel_separation_multiplier* in the velocity controller.  This is now available through the launch file chain.

There is some translation during point turns.  This is expected. If it is significantly different than the real vehicle, the contact parameters will need to be re-tuned.  I would start with the second friction parameter.

$\dot{x}_{err} \approx 2\%$ but $\dot{\Theta}_{err} \approx 1\%$

![x_dot_plot](./x_dot_v4.png)
$\hspace{10mm}$
![theta_dot_plot](./theta_dot_v4.png)]



## Parameter Descriptions

### Contact parameters

#### condim=6

Setting condim="6" enables rolling friction explicitly, helping the wheel "grip" and stop rolling when no driving torque is applied.

#### priority=1 

Ensures that the floor friction and solimp values are used for contacts.  Makes the wheel values irrelevant.

Ideally, we would set up contact pairs with the floor and each of the wheels -- would allow us to have different values on pavement, indoor floor and gravel.  In order to do that, the wheel geoms would have to have names.

#### friction = "sliding torsional rolling")

Each geom accepts three values in its friction attribute:

- sliding friction (1st value, default: 1.0) Standard tangential friction coefficient $(F_{t} \le \mu_{slide} F_{n})$ acting along the contact tangent plane. Can be anisotropic (two values) if defined in an explicit contact pair
- torsional friction (2nd value, default: 0.005): Torsional resistance around the contact normal axis $(T_{n} \le \mu_{spin} F_{n})$ preventing spin.
- rolling friction (3rd value, default: 0.0001): Rolling resistance torque $(T_{t} \le \mu_{roll} F_{n})$ opposing rolling motion.

#### solimp="dmin dmax width midpoint power"

- dmin (Minimum Impedance: e.g., 0.015 – 0.025) Determines the softness/compliance at zero or minimal penetration (\(r=0\)).Lower values make the initial touch point of the rubber feel softer and more compliant, helping absorb minor surface irregularities.
- dmax (Maximum Impedance: e.g., 0.95 – 1.0) Determines the maximum hardness/resistance when the tire reaches its structural limit under heavy load or deep penetration.
- width (Transition Width: e.g., 0.9) The transition range of penetration over which the impedance scales from dmin to dmax. A wider transition yields a progressive, spongy feel characteristic of air-filled rubber walls.
- midpoint (Midpoint: e.g., 0.95 or 0.5) Where the transition curve reaches the halfway point between dmin and dmax. A higher midpoint (0.95) means the tire stays relatively soft through most of its compliance range and firms up sharply near full deflection.
- power (Curve Exponent: e.g., 2) Controls the shape (curvature) of the transition. A power of 2 provides a smooth, non-linear quadratic increase in stiffness as the tire deforms.

#### solref="time_constant critical_damping"

 Time constant and damping ratio to govern the actual contact spring-damper dynamics. For rubber tires, pair your solimp with a critically damped or slightly overdamped. 0.02 s is the time constant for response recovery and 1.0 is critical damping to prevent bouncing/oscillation.

 Increasing the second value  over-damps the contact constraint. This acts as a physical shock absorber for the contact forces, soaking up the energy that was previously causing the high-frequency vehicle shaking.


### Other Parameters


#### wheel_joint_force_limit" value="100000"

#### wheel_kv" value="60000"

This needs to be high enough so that the robot will turn at the correct speed, but low enough that it doesn't get twitchy.  This has to be re-tuned as the contact parameters change.

#### wheel_ctrl_rng" value="30"

This just needs to be high enough to achieve the maximum desired velocity.

### Mujoco Options

#### integrator="implicitfast" (default "Euler")
 
 This is the recommended integrator for wheeled vehicles.

#### impratio = 1.0

Many guides recommend that you increase impratio to reduce slip.  My experience was that that was not helpful -- no difference between impratio = 1 (default) and impratio = 100
