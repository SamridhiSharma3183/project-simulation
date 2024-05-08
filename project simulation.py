import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Material properties
cp_electronics = 890  # J/kg⋅K (specific heat capacity of electronics)
rho_electronics = 8960  # kg/m^3 (density of electronics)
k_electronics = 400  # W/m⋅K (thermal conductivity of electronics)
m_electronics = 0.1  # kg (mass of electronics)

cp_pcm = 2000  # J/kg⋅K (specific heat capacity of PCM)
rho_pcm = 800  # kg/m^3 (density of PCM)
latent_heat = 200000  # J/kg (latent heat of fusion of PCM)
melting_point = 70  # °C

# Heat sink properties
A_hs_base = 0.01  # m^2 (base heat sink surface area)
fin_height = 0.005  # m (fin height)
fin_thickness = 0.001  # m (fin thickness)
fin_spacing = 0.002  # m (fin spacing)
k_hs = 200  # W/m⋅K (thermal conductivity of heat sink material)

# Simulation parameters
dt = 0.1  # s (time step)
sim_time = 30  # s (simulation duration)
power_surge_start = 5  # s (time when power surge starts)
power_surge_duration = 10  # s (duration of power surge)
power_surge_intensity = 1000  # W (additional heat generated during surge)

# Ambient temperature
np.ambient = 25  # °C

# Base convective heat transfer coefficient (replace with your actual value)
h_conv_base = 10  # W/m^2⋅K

# Fin efficiency calculation (assuming constant fin cross-section)
def fin_efficiency(L, k_fin, h):
    m = np.sqrt(h * k_fin / (k_hs * fin_thickness))
    theta = m * L
    return (1.0 - np.exp(-2.0 * m * L)) / (theta)

# Effective heat transfer area calculation
def calculate_effective_area(h):
    # Perimeter of a single fin
    fin_perimeter = 2 * (fin_height + fin_thickness)

    # Number of fins
    n_fins = int(A_hs_base / (fin_spacing + fin_thickness))

    # Effective fin area per unit base area
    A_f_A_b = fin_efficiency(fin_height, k_hs, h) * fin_perimeter

    # Total effective heat transfer area
    A_eff = A_hs_base + n_fins * A_f_A_b

    return A_eff

# Fan speed control model (example: temperature-dependent fan speed)
def fan_speed_control(T):
    fan_speed_multiplier = 1 + (T - melting_point) / 20  # Adjust function for desired behavior
    return h_conv_base * fan_speed_multiplier  # Adjust h_conv_base with your base value

# System of differential equations for temperature
def dTdt(T, t):
    T_electronics = T[0]
    T_pcm = T[1]

    # Heat generation due to power surge
    Q_surge = 0
    if power_surge_start <= t < power_surge_start + power_surge_duration:
        Q_surge = power_surge_intensity

    # Heat transfer coefficient based on fan speed and fin efficiency
    h_conv = fan_speed_control(T_electronics)
    A_eff = calculate_effective_area(h_conv)

    # Heat transfer rates
    dQ_cond_elec_pcm = -k_electronics * A_eff * (T_electronics - T_pcm) / m_electronics * dt
    dQ_conv = h_conv * A_eff * (T_electronics - np.ambient)
    # Heat transfer rates (continued)
    dQ_fusion = 0  # Initially no fusion

    # Check for PCM phase change (latent heat transfer during melting)
    if T_pcm >= melting_point:
        dQ_fusion = latent_heat * T_pcm / cp_pcm  # Heat absorbed during PCM melting

    # Differential equations
    dT_electronics_dt = (dQ_cond_elec_pcm + dQ_conv + Q_surge) / (cp_electronics * m_electronics)
    dT_pcm_dt = (dQ_cond_elec_pcm - dQ_fusion) / (cp_pcm * T_pcm)

    return [dT_electronics_dt, dT_pcm_dt]

# Initial conditions
T0 = [np.ambient, np.ambient]  # Initial temperatures of electronics and PCM

# Solve differential equations
t = np.arange(0, sim_time + dt, dt)
T = odeint(dTdt, T0, t)

# Extract temperatures
T_electronics = T[:, 0]
T_pcm = T[:, 1]

# Plot results
plt.plot(t, T_electronics, label="Electronics Temperature")
plt.plot(t, T_pcm, label="PCM Temperature")
plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Response During Power Surge (Fan Speed Control)")
plt.legend()
plt.show()