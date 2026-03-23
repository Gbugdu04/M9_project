# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 14:45:36 2026

@author: Marthe
"""
import numpy as np

np.set_printoptions(precision=1)

# Data
# ====
# overall dimensions
H = 4 # m
B = 4 # m
La = 10 # m 
Lp = 6 # m

# windows in east/west walls
N_windows_animal = 2
N_windows_people = 1

# Surfaces dictionary 
S = {}
S["Window"] = 1*2
S["Windows_animal"] = 2*N_windows_animal*S["Window"]  # for 1 wall
S["Windows_people"] = 2*N_windows_people*S["Window"]  # for 1 wall
S["North_facade"] = B*H 
S["Facade_animal"] = La*H - S["Windows_animal"]       # for 1 wall
S["Facade_people"] = Lp*H - S["Windows_people"]       # for 1 wall
S["Ground_animal"] = La*B
S["Ground_people"] = Lp*B
S["Outdoor_wall_animal"] = 2*S["Facade_animal"] + S["North_facade"]
S["Outdoor_wall_people"] = 2*S["Facade_people"] + S["North_facade"]
S["Total_animal"] = 2*S["North_facade"] + 2*S["Ground_animal"] + 2*La*H
S["Total_people"] = 2*S["North_facade"] + 2*S["Ground_people"] + 2*Lp*H

Vol_animal = H*La*B
Vol_people = H*Lp*B

# surfaces Négi
Sroof = Sground = (La + Lp) * B



Sroof_a = La *B                   # roof above animals
Sroof_h = Lp *B                   # roof above humans
Swall_a = (2* La + B) * H           # total exterior wall surface for animals 
Swall_h = (2* Lp + B) * H           # total exterior wall surface for humans



Swall_animals_east = Swall_animals_west = La * H
Swall_humans_east = Swall_humans_west = Lp * H
Swall_B = B* H

Sroom_animal = Swall_a + 2*(Sroof_a + Swall_B)  # all surfaces of the room
Sroom_humans = Swall_h + 2*(Sroof_h + Swall_B) 

Swindows_animals = 8
Swindows_humans = Swindows_animals / 2

# width dictionary
width = {}
width["outer_stone"] = 0.5
width["inner_stone"] = 0.2
width["ground"] = 3
width["roof"] = 0.2
width["isolation"] = 0.4
width["window"] = 0.04

# materials dictionaries
stone = {
    "Conductivity": 1.400,       # W/(m·K)
    "Density": 2300.0,           # kg/m³
    "Specific heat": 880,        # J/(kg⋅K)"
}
isolation = {                    # in cork
    "Conductivity": 0.040,       # W/(m·K)
    "Density": 16.0,             # kg/m³
    "Specific heat": 1210,       # J/(kg⋅K)"
}
roof = {                         # in wood
    "Conductivity": 1.400,       # W/(m·K)
    "Density": 2300.0,           # kg/m³
    "Specific heat": 880,        # J/(kg⋅K)"
}
glass = {                         
    "Conductivity": 1.400,       # W/(m·K)
    "Density": 2300.0,           # kg/m³
    "Specific heat": 880,        # J/(kg⋅K)"
}
ground = {                         
    "Conductivity": 1.400,       # W/(m·K)
    "Density": 2300.0,           # kg/m³
    "Specific heat": 880,        # J/(kg⋅K)"
}
air = {
    "Density": 1.2,              # kg/m³
    "Specific heat": 1000,       # J/(kg⋅K)"
}

hi, he = 8, 25 # W/(m2 K) convection coefficients in, out
Tau = 0.7 #transmission coefficient

# short-wave solar radiation absorbed by each wall
E = 200  # W/m2
ACH = 1  #ventilation rate (air-changes per hour)

To = -5  # °C
Tg = 13  # °C
Tsp = 20  # °C

# outdoor temperature

# ventilation rate (air-changes per hour)
ACH = 1             # volume/h

#V_dot =B*B* H * ACH / 3600  # volumetric air flow rate
#m_dot = ρ * V_dot               # mass air flow rate

nq, nθ = 22, 14  # number of flow-rates branches and of temperature nodes

# Incidence matrix
# ================
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

# Conductance matrix
# ==================
G = np.zeros(A.shape[0])

# G0: outdoor convection wall animal
G[0] = he * S["Outdoor_wall_animal"]

# G1,G7: conduction outdoor walls
G[1] = stone["Conductivity"] / width["outer_stone"] * S["Outdoor_wall_animal"]
G[7] = stone["Conductivity"] / width["outer_stone"] * S["Outdoor_wall_people"]

# G2,G6: Indoor convection walls
G[2] = hi * S["Outdoor_wall_animal"]
G[6] = hi * S["Outdoor_wall_people"]

# G3,G5 : indoor walls indoor convection
G[[3,5]] = hi * S["North_facade"]

# G4 : indoor walls conduction
G[4] = stone["Conductivity"] / width["inner_stone"] * S["North_facade"]

# G8: outdoor convection wall people
G[8] = he * S["Outdoor_wall_people"]

#ROOF animal G13:G15
G[13] = he * S["Ground_animal"] #Convection
G[14] = roof["Conductivity"] / width["roof"] * S["Ground_animal"] #conduction
G[15] = hi * S["Ground_animal"] #convection

#ROOF people G16:G18

G = np.diag(G)

# Vector of temperature sources
# =============================
G[16] = hi * S["Ground_people"] #indoor convection
G[17] = roof["Conductivity"] / width["roof"] * S["Ground_people"] #indoor conduction
G[18] = he * S["Ground_people"] #outdoor convection

#GROUND animal G9:G10
G[9] =  ground["Conductivity"] / width["ground"] * S["Ground_animal"] #conduction
G[10] = hi * S["Ground_animal"]

# G20,G21: advection by ventilation
G[20] = air["Specific heat"] * air["Density"] * Vol_animal * ACH/3600 + 2*S["Windows_animal"]/(1/he+width["window"]/glass["Conductivity"]+1/hi)
G[21] = air["Specific heat"] * air["Density"] * Vol_people * ACH/3600 + 2*S["Windows_people"]/(1/he+width["window"]/glass["Conductivity"]+1/hi)

# G22: gains of proportional controllers
b = np.zeros(A.shape[0])
b[[0, 13, 18, 20, 21]] = To          #outdoor temperature for walls and advection  
b[[8]] = -To #Direction of arrow 
b[[9, 12]] = Tg #ground temperature, still needs to be defined
b[[19]] = Tsp   # setpoint temperature, stills needs to be defined 

# Vector of flow-rate sources
# =============================
f = np.zeros(A.shape[1])

# Solar radiation W/m²
En = 113                # walls oriented North, South, East, and West
Es = 150
Ee = 140
Ew = 170
Er = 270  # roof

exterior_wall_animals = [0]
f[exterior_wall_animals] = Swall_animals_east * Ee + Swall_animals_west * Ew +Swall_B* En

exterior_wall_humans = [7]
f[exterior_wall_humans] = Swall_humans_east * Ee + Swall_humans_west * Ew +Swall_B* En

roof_animals = [10]
f[roof_animals] = Sroof_a * Er

roof_humans = [13]
f[roof_humans] = Sroof_h * Er

indoor_wall_animals = [1]
f[indoor_wall_animals] = (Swindows_animals/2 * Ee + Swindows_animals/2 * Ew) * Tau * Swall_a/(Sroom_animal)

indoor_wall_humans = [6]
f[indoor_wall_animals] = (Swindows_humans/2 * Ee + Swindows_humans/2 * Ew) * Tau * Swall_h/(Sroom_humans)

partition_wall_animals = [3]
f[partition_wall_animals] = (Swindows_animals/2 * Ee + Swindows_animals/2 * Ew) * Tau * Swall_B/(Sroom_animal)

partition_wall_humans = [4]
f[partition_wall_animals] = (Swindows_humans/2 * Ee + Swindows_humans/2 * Ew) * Tau * Swall_B/(Sroom_humans)

ceiling_animals = [11]
f[ceiling_animals] = (Swindows_animals/2 * Ee + Swindows_animals/2 * Ew) * Tau * Sroof_a/(Sroom_animal)

ceiling_humans = [12]
f[ceiling_humans] = (Swindows_humans/2 * Ee + Swindows_humans/2 * Ew) * Tau * Sroof_h/(Sroom_humans)

ground_animals = [8]
f[ground_animals] = (Swindows_animals/2 * Ee + Swindows_animals/2 * Ew) * Tau * Sroof_a/(Sroom_animal)

ground_humans = [9]
f[ground_humans] = (Swindows_humans/2 * Ee + Swindows_humans/2 * Ew) * Tau * Sroof_h/(Sroom_humans)


