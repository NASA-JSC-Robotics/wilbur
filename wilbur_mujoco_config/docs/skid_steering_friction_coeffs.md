# Skid-Steering Friction Coefficients
Skid-steering platforms rely entirely on lateral tire slip to turn, meaning standard rolling friction models are insufficient. For physics engines like Gazebo (ODE/Bullet) or custom tire-soil terramechanics equations, the friction model splits into longitudinal ($\mu_x$) and lateral ($\mu_y$) components. [3, 4] 
The default simulation coefficients calibrated for the 24" Argo Turf/Traction Tires are:

| Surface Type | Longitudinal Friction ($\mu_x$) | Lateral Friction ($\mu_y$) | Notes / Dynamics Impact |
|---|---|---|---|
| Asphalt / Concrete | 0.8 to 1.0 | 0.5 to 0.6 | Extreme turning resistance; high current draw. |
| Hard Soil / Dirt | 0.6 to 0.7 | 0.4 | Ideal balanced skid-steering environment. |
| Grass / Mud | 0.4 to 0.5 | 0.25 to 0.3 | High wheel-slip rates (μ < 0.4 reduces turning authority). |
| Gazebo Default (<mu>, <mu2>) | 1.0 | 0.5 | Clearpath's standard template for generic ground elements. |

## Implementing the Slip Dynamics
Because a turning Warthog must break lateral traction to pivot, your dynamic model must satisfy the friction threshold equation:
$$
T_{\text{turning}} > \mu_y \cdot m_w \cdot g \cdot \left(\frac{L}{2}\right)
$$
Where $m_w$ is the normal load on the wheels and L is the longitudinal wheelbase. If your simulated motor torque (adjusted via the 40:1 gear ratio) cannot overcome $\mu_y$, the simulated robot will lock up and fail to pivot in place.
Would you like the exact wheelbase dimensions (L and W) or the motor torque-speed curves to calculate the precise slip-ratio threshold for your simulation?
