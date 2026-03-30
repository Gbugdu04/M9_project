# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 10:57:55 2026

@author: User
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 14:45:36 2026

@author: Marthe
"""
import numpy as np

np.set_printoptions(precision=1)

# Input data
# ====
# overall dimensions
H = 4 # m
B = 4 # m
La = 10 # m length animals
Lh = 6 # m length human

# number of windows on east/west walls
N_windows_animal = 2
N_windows_people = 1

# Surfaces dictionary 
S = {}
S["Window"] = 1*2
S["Windows_animal"] = N_windows_animal*S["Window"]  # for 1 wall
S["Windows_people"] = N_windows_people*S["Window"]  # for 1 wall
S["North_facade"] = B*H 
S["Facade_animal"] = La*H - S["Windows_animal"]       # for 1 wall
S["Facade_people"] = Lh*H - S["Windows_people"]       # for 1 wall
S["Ground_animal"] = La*B
S["Ground_people"] = Lh*B
S["Outdoor_wall_animal"] = 2*S["Facade_animal"] + S["North_facade"]
S["Outdoor_wall_people"] = 2*S["Facade_people"] + S["North_facade"]
S["Total_animal"] = 2*S["North_facade"] + 2*S["Ground_animal"] + 2*La*H
S["Total_people"] = 2*S["North_facade"] + 2*S["Ground_people"] + 2*Lh*H

# width dictionary
width = {}
width["outer_stone"] = 0.5
width["inner_stone"] = 0.2 # width of wall separating people and animal space
width["ground"] = 3
width["roof"] = 0.2
width["isolation"] = 0.4
width["window"] = 0.04

#Volumes 
Vol_animal = H*La*B
Vol_people = H*Lh*B

# materials dictionaries
stone = {
    "Conductivity": 3.5,            # W/(m·K)
    "Density": 2300.0,              # kg/m³
    "Specific heat": 1000,          # J/(kg⋅K)"
}
isolation = {                       # in some material
    "Conductivity": 0.05,           # W/(m·K)
    "Density": 200,                 # kg/m³
    "Specific heat": 1560,          # J/(kg⋅K)"
}
roof = {                         # in wood
    "Conductivity": 0.18,       # W/(m·K)
    "Density": 2000,           # kg/m³
    "Specific heat": 705,        # J/(kg⋅K)"
}
glass = {                        
    "Conductivity": 1.400,       # W/(m·K)
    "Density": 2500.0,           # kg/m³
    "Specific heat": 750,        # J/(kg⋅K)"
}
ground = {                        
    "Conductivity": 1.700,       # W/(m·K)
    "Density": 1600,           # kg/m³
    "Specific heat": 1700,        # J/(kg⋅K)"
}
air = {
    "Density": 1.2,              # kg/m³
    "Specific heat": 1000,       # J/(kg⋅K)"
}

# coefficients 
hi, he = 8, 25 # W/(m2 K) convection coefficients in, out
Tau = 0.7 #transmission coefficient of the windows


# pre-defined temperatures 
Tg = 13  # °C #ground temperature
Tsp = 20  # °C #setpoint temperature 

# proportional gain 
Kp = 10**9  # Conductance controller  

# properties of cows 
Cow_Power = 700 # W  per cow                  
Cow_number = 0   #number of cows                  

# =========================
# Thermal model 
# =========================

# number of flow-rates branches and of temperature node
nq, nθ = 22, 14  

# --- Incidence matrix A ---
# ==================
A = np.zeros([nq, nθ])

# node by node from 0 to 13
A[0, 0] = 1    # node 0 
A[1, 0] = -1

A[1, 1] = 1    # node 1
A[2, 1] = -1

A[2, 2] = 1    # node 2 ...
A[3, 2] = -1
A[20, 2] = 1
A[15, 2] = 1
A[10, 2] = 1

A[3, 3] = 1
A[4, 3] = -1

A[4, 4] = 1
A[5, 4] = -1

A[5, 5] = 1
A[6, 5] = -1
A[21, 5] = 1
A[19, 5] = 1  
A[16, 5] = 1
A[11, 5] = 1

A[6, 6] = 1
A[7, 6] = -1

A[7, 7] = 1
A[8, 7] = -1

A[9, 8] = 1
A[10, 8] = -1

A[12, 9] = 1
A[11, 9] = -1

A[13, 10] = 1
A[14, 10] = -1

A[14, 11] = 1
A[15, 11] = -1

A[17, 12] = 1
A[16, 12] = -1

A[18, 13] = 1
A[17, 13] = -1


# =========================
# Climate data
# =========================

# Outdoor temperature, irradiance for different wall orientations and ventilation rates in summer and winter
climate = {
    "January": {"To": 3.13, "En": 21.96, "Es": 38.08, "Ee": 22.79, "Ew": 28.81, "Er": 39.26, "ACH": 1},
    "July":    {"To": 21.56, "En": 113.40, "Es": 151.39, "Ee": 137.83, "Ew": 173.50, "Er": 271.54, "ACH": 25}
}

# =========================
# Loop over months
# =========================
for month, data in climate.items():

    # --- outdoor and solar conditions ---
    To = data["To"]    # outdoor temperature in °C, calculated with weather data 
    En = data["En"]    # solar irradiance W/m² (calculated with weather data) for walls oriented North, South, East, and West
    Es = data["Es"]
    Ee = data["Ee"]
    Ew = data["Ew"]
    Er = data["Er"]    # solar irradiance W/m² (calculated with weather data) for roof
    ACH = data["ACH"]  # ventilation rate (air-changes per hour) 
    
   
    
    # --- Conductance matrix ---
    # ==================
    G = np.zeros(A.shape[0])

    # G0: outdoor convection wall animal
    G[0] = he * S["Outdoor_wall_animal"]

    # G1,G7: conduction outdoor walls
    G[1] = stone["Conductivity"] / width["outer_stone"] * S["Outdoor_wall_animal"]
    G[7]=  S["Outdoor_wall_people"]/ (width["outer_stone"] / stone["Conductivity"] + width["isolation"]/isolation["Conductivity"])

    # G2,G6: Indoor convection walls
    G[2] = hi * S["Outdoor_wall_animal"]
    G[6] = hi * S["Outdoor_wall_people"]

    # G3,G5 : indoor walls indoor convection
    G[[3,5]] = hi * S["North_facade"]

    # G4 : indoor walls conduction
    G[4] = stone["Conductivity"] / width["inner_stone"] * S["North_facade"]

    # G8: outdoor convection wall people
    G[8] = he * S["Outdoor_wall_people"]

    #G13:G15 : ROOF animal 
    G[13] = he * S["Ground_animal"] #Convection
    G[14] = roof["Conductivity"] / width["roof"] * S["Ground_animal"] #conduction
    G[15] = hi * S["Ground_animal"] #convection

    #G16:G18 : ROOF people 
    G[16] = hi * S["Ground_people"] #indoor convection
    G[17] = roof["Conductivity"] / width["roof"] * S["Ground_people"] #indoor conduction
    G[18] = he * S["Ground_people"] #outdoor convection

    #G9:G10 : GROUND animal 
    G[9] =  ground["Conductivity"] / width["ground"] * S["Ground_animal"] #conduction
    G[10] = hi * S["Ground_animal"]#indoor convection

    #G11,G12 : GROUND people 
    G[12] =  ground["Conductivity"] / width["ground"] * S["Ground_people"] #conduction
    G[11] = hi * S["Ground_people"]

    #CONTROLLER
    G[19]= Kp

    # G20,G21: advection by ventilation
    G[20] = air["Specific heat"] * air["Density"] * Vol_animal * ACH/3600 + 2*S["Windows_animal"]/(1/he+width["window"]/glass["Conductivity"]+1/hi)
    G[21] = air["Specific heat"] * air["Density"] * Vol_people * ACH/3600 + 2*S["Windows_people"]/(1/he+width["window"]/glass["Conductivity"]+1/hi)

    G = np.diag(G)

    # --- temperature source vector ---
    # ==================
    b = np.zeros(A.shape[0])
    
    b[[0, 13, 18, 20, 21]] = To           # outdoor walls and advection
    b[[8]] = -To                           # negative because of direction of arrow
    b[[9, 12]] = Tg                        # ground temperature
    b[[19]] = Tsp                          # controller setpoint

    # --- Vector of flow rate sources ---
    # ==================
    f = np.zeros(A.shape[1])

    # outdoor walls
    f[0] = S["Facade_animal"] * Ee + S["Facade_animal"] * Ew + S["North_facade"] * En
    f[7] = S["Facade_people"] * Ee + S["Facade_people"] * Ew + S["North_facade"] * Es

    # roof
    f[10] = S["Ground_animal"] * Er
    f[13] = S["Ground_people"] * Er

    # indoor walls solar gains
    f[1] = (S["Windows_animal"] * Ee + S["Windows_animal"] * Ew) * Tau * S["Outdoor_wall_animal"] / S["Total_animal"]
    f[6] = (S["Windows_people"] * Ee + S["Windows_people"] * Ew) * Tau * S["Outdoor_wall_people"] / S["Total_people"]

    # partition walls
    f[3] = (S["Windows_animal"] * Ee + S["Windows_animal"] * Ew) * Tau * S["North_facade"] / S["Total_animal"]
    f[4] = (S["Windows_people"] * Ee + S["Windows_people"] * Ew) * Tau * S["North_facade"] / S["Total_people"]

    # ceilings
    f[11] = (S["Windows_animal"] * Ee + S["Windows_animal"] * Ew) * Tau * S["Ground_animal"] / S["Total_animal"]
    f[12] = (S["Windows_people"] * Ee + S["Windows_people"] * Ew) * Tau * S["Ground_people"] / S["Total_people"]

    # floors
    f[8] = (S["Windows_animal"] * Ee + S["Windows_animal"] * Ew) * Tau * S["Ground_animal"] / S["Total_animal"]
    f[9] = (S["Windows_people"] * Ee + S["Windows_people"] * Ew) * Tau * S["Ground_people"] / S["Total_people"]

    # animal heater
    f[2] = Cow_number * Cow_Power

    # --- solve system ---
    θ = np.linalg.inv(A.T @ G @ A) @ (A.T @ G @ b + f)
    q = G @ (-A @ θ + b)

    # --- output ---
    print("\n====", month, "====")
    print("Temperature in barn:", round(θ[2], 2), "°C")
    print("Temperature in room:", round(θ[5], 2), "°C")
    print("Controller heat flow:", round(q[19], 2), "W")

