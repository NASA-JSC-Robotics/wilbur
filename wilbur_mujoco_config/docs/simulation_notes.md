# Notes on simulation choices

## 30 July 2026

### Base Simulation State

The hardest thing to get right here is to get just the right amount of wheel slip so that the robot will turn -- lateral and even longitudinal slip is required for the robot to turn -- and still have good traction.

In this configuration, there is about 1% wheel slip on straight driving and about 10% error on turning.  This is probably not too far from reality, although the 1% on the straight-away is, I think, a little high.  Turning is always error prone for differential and skid steer vehicles.

Error was measured using comparing the  */velocity_controller/odom* topic to */simulator/floating_base_state*.

#### Wheel Geom

Wheels are modeled as meshes.  I have tried cylinders and capsules, but have not gotten any better action.  I think the best model is a cylinder with carefully tuned friction constants and this is a work in progress.  It would be helpful to have real robot data to match.  The values here are from some testing and a lot of googling for constants for rubber tires.  In theory, capsules should work the best, but still trying.

##### friction="1.0 0.005 0.0001"

- Sliding (1st component, default: 1.0): For differential drive wheels, a reasonable value is 1.0 to 1.5 to prevent unwanted side-slipping when turning.
- Torsional (2nd component, default: 0.005): Resistance to spinning the wheel or contact patch around the contact normal axis. Keeping this small or near default allows smooth rotation-in-place (pivot turns).
- Rolling (3rd component, default: 0.0001): Resistance to rolling motion. Keep this very small (e.g., 0.0001 to 0.001) so the robot can roll freely without excessive passive drag.

I've tried a bunch of different values here, but need to do a set of individual controlled tests to get better values.  First try would be to increase the rolling friction to reduce longitudinal slip.  My gut instinct is that the robot should have no slip on the straight-away.  Ideally, we'd be modeling wheel deflection and surface patch, but that is for the future.

> Testing: 
>
> Sliding = 1.0     -- 0.35 radians of error after 1 radian turn
> 
> Sliding = 2.0     -- 0.36 radians of error after 1 radian turn

##### condim=6

Setting condim="6" enables rolling friction explicitly, helping the wheel "grip" and stop rolling when no driving torque is applied.

##### priority=1

Ensures that the wheel friction and solimp values are used for contacts.  Makes the "floor" values irrelevant.

Ideally, we would set up contact pairs with the floor and each of the wheels -- would allow us to have different values on pavement, indoor floor and gravel.  In order to do that, the wheel geoms would have to have names.

##### solimp="0.015 1.0 0.9 0.95 2"

- dmin (Minimum Impedance: e.g., 0.015 – 0.025)Determines the softness/compliance at zero or minimal penetration (\(r=0\)).Lower values make the initial touch point of the rubber feel softer and more compliant, helping absorb minor surface irregularities.
- dmax (Maximum Impedance: e.g., 0.95 – 1.0)Determines the maximum hardness/resistance when the tire reaches its structural limit under heavy load or deep penetration.
- width (Transition Width: e.g., 0.9)The transition range of penetration over which the impedance scales from dmin to dmax. A wider transition yields a progressive, spongy feel characteristic of air-filled rubber walls.
- midpoint (Midpoint: e.g., 0.95 or 0.5)Where the transition curve reaches the halfway point between dmin and dmax. A higher midpoint (0.95) means the tire stays relatively soft through most of its compliance range and firms up sharply near full deflection.
- power (Curve Exponent: e.g., 2)Controls the shape (curvature) of the transition. A power of 2 provides a smooth, non-linear quadratic increase in stiffness as the tire deforms.

##### solref="0.02 1.0"

 Time constant and damping ratio to govern the actual contact spring-damper dynamics. For rubber tires, pair your solimp with a critically damped or slightly overdamped. 0.02 s is the time constant for response recovery and 1.0 is critical damping to prevent bouncing/oscillation.

 > Testing:
 >
 > Adding these values for solimp and solref reduced straight-away error by about 0.6 %  or about 3 cm over 5 meters.

#### Other Parameters


##### wheel_joint_force_limit" value="100000"

##### wheel_kv" value="400"

Velocity gain on the wheel controller.

> Testing:
>
> value = 100 -- vehicle would not turn
>
> value = 300 -- vehicle turns, but cannot achieve desired rate (1 rad/sec)
>
> value = 400 -- vehicle turns , but cannot achieve desired rate (1 rad/sec)
>
> value = 600 -- vehicle turns and can achieve near 1m/s with 1% error
> value = 1000 -- vehicle achieves desired rate, but the turning error goes way up (nearly 1 radian / radian)

##### wheel_ctrl_rng" value="5"

#### Options

##### integrator="implicitfast" (default "Euler")
 
 > Testing:
 >
 > integrator="implicitfast"  This is recommended, but it makes the robot "twitchy". Works if the timestep is also set to 0.001
 >

## Systematic Tuning Steps

[Low Forcerange] ──> Robot stalls / Cannot turn laterally
       │
       ▼ (Increase forcerange or decrease lateral friction)
[High Friction]  ──> Robot shakes, hops, or flips over
       │
       ▼ (Soften solref/solimp & lower torsional friction)
[Balanced Tune]  ──> Smooth forward drive & stable skidding turns


   1. Test Forward Drive: Command all wheels to move forward. Adjust kv until the robot reaches target speed quickly without oscillating.
   2. Test Pivot Turn: Command the left wheels forward and right wheels backward.
   3. Fix Stalling: If the wheels lock up and refuse to rotate, gradually increase the actuator forcerange or lower the second value in the wheel's friction attribute.
   4. Fix Hopping: If the robot chatters or bounces up and down while turning, increase the damping term in solref or decrease the wheel mass.



## Other things...

Probably want to us intvelocity rather than velocity for control.  intvelocity doesn't seem to be supported by mujoco_ros2_control

To tune a skid-steer robot in MuJoCo, you must balance the friction coefficients of the wheels against the torque limits and velocity gains of your actuators. Because skid-steering relies entirely on slipping during turns, default simulator parameters often cause the robot to get stuck or bounce violently.
## 1. Actuator Configuration
Use velocity actuators with explicit torque limits to prevent the motors from exerting infinite force.

* 
* Set kv (Velocity Gain): Start with a modest gain ($k_v = 10$ to 50) to ensure a snappy response without introducing high-frequency chatter.
* Define forcerange: Limit the maximum torque. If the torque is too low, the wheels cannot overcome static friction to slide. If it is too high, the robot will violently jerk or flip.
* Match Left/Right Sides: Group your left wheels and right wheels into synchronized control signals via your controller script.
* 
