# main python file for the project
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import dm4bem as dm4

# overall dimensions
H = 4 # m
B = 4 # m
La = 10 # m 
Lp = 6 # m

# windows in east/west walls
N_windows_animal = 4
N_windows_people = 2

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

# width dictionary
width = {}
width["outer_stone"] = 0.2
width["inner_stone"] = 0.2
width["ground"] = 3
width["roof"] = 0.2
width["isolation"] = 0.08
width["window"] = 0.004

# materials dictionaries
stone = {
    "Conductivity": 3.500,       # W/(m·K)
    "Density": 2800.0,           # kg/m³
    "Specific heat": 1000,        # J/(kg⋅K)"
}
isolation = {                    # in cork
    "Conductivity": 0.050,       # W/(m·K)
    "Density": 200.0,             # kg/m³
    "Specific heat": 1560,       # J/(kg⋅K)"
}
roof = {                         # in wood / oak
    "Conductivity": 0.180,       # W/(m·K)
    "Density": 2000.0,           # kg/m³
    "Specific heat": 705,        # J/(kg⋅K)"
}
glass = {                         
    "Conductivity": 1.400,       # W/(m·K)
    "Density": 2500.0,           # kg/m³
    "Specific heat": 750,        # J/(kg⋅K)"
}
ground = {                         
    "Conductivity": 1.700,       # W/(m·K)
    "Density": 1700.0,           # kg/m³
    "Specific heat": 1600,        # J/(kg⋅K)"
}
air = {
    "Density": 1.2,              # kg/m³
    "Specific heat": 1000,       # J/(kg⋅K)"
}

hi, he = 8, 25
E = 200
ACH = 1

nq , nθ = 30 , 22

Tg = 13
Tc = 20

# matrix A
A = np.zeros([nq, nθ])

A[0,0] = 1
for i in range(1,12):
    A[i,i-1],A[i,i] = -1 ,1
A[12,11] = -1

for i in range(12,15):
    A[i+1,i] = 1
    A[i+2,i] = -1
A[16,3] = 1

for i in range(15,18):
    A[i+2,i] = 1
    A[i+3,i] = -1
A[20,7] = 1

A[21,18] = 1
A[22,18],A[22,19] = -1 ,1
A[23,19],A[23,3] = -1 ,1

A[24,20] = 1
A[25,20],A[25,21] = -1 ,1
A[26,21],A[26,7] = -1 ,1

A[27,3] = 1
A[28,7] = 1
A[29,7] = 1

# Conductance matrix
G = np.zeros(nq)

G[0] = he * S["Outdoor_wall_animal"]
G[[1,2]] = 2 * stone["Conductivity"] / width["outer_stone"] * S["Outdoor_wall_animal"]
G[3] = hi * S["Outdoor_wall_animal"]

G[[4,7]] = hi * S["North_facade"]
G[[5,6]] = 2 * stone["Conductivity"] / width["inner_stone"] * S["North_facade"]

G[8] = hi * S["Outdoor_wall_people"]
G[9] = 2 * stone["Conductivity"] / width["outer_stone"] * S["Outdoor_wall_people"]
G[11] = 2 * isolation["Conductivity"] / width["isolation"] * S["Outdoor_wall_people"]
G[10] = 1/(1/G[9] + 1/G[11])
G[12] = he * S["Outdoor_wall_people"]

G[13] = he * S["Ground_animal"] #ROOF
G[[14,15]] = 2 * roof["Conductivity"] / width["roof"] * S["Ground_animal"]
G[16] = hi * S["Ground_animal"]

G[17] = he * S["Ground_people"] #ROOF
G[[18,19]] = 2 * roof["Conductivity"] / width["roof"] * S["Ground_people"]
G[20] = hi * S["Ground_people"]

G[[21,22]] = 2 * ground["Conductivity"] / width["ground"] * S["Ground_animal"]
G[23] = hi * S["Ground_animal"]

G[[24,25]] = 2 * ground["Conductivity"] / width["ground"] * S["Ground_people"]
G[26] = hi * S["Ground_people"]

G[27] = air["Specific heat"] * air["Density"] * Vol_animal * ACH/3600 + 2*S["Windows_animal"]/(1/he+width["window"]/glass["Conductivity"]+1/hi)
G[28] = air["Specific heat"] * air["Density"] * Vol_people * ACH/3600 + 2*S["Windows_people"]/(1/he+width["window"]/glass["Conductivity"]+1/hi)

G = np.diag(G)

# capacity
C = np.zeros(nθ)
C[1] = stone["Specific heat"]*      stone["Density"]*    S["Outdoor_wall_animal"]*width["outer_stone"]
C[5] = stone["Specific heat"]*      stone["Density"]*    S["North_facade"]*       width["inner_stone"]
C[9] = stone["Specific heat"]*      stone["Density"]*    S["Outdoor_wall_people"]*width["outer_stone"]
C[10] = isolation["Specific heat"]* isolation["Density"]*S["Outdoor_wall_animal"]*width["isolation"]
C[13] = roof["Specific heat"]*      roof["Density"]*     S["Ground_animal"]*      width["roof"]
C[16] = roof["Specific heat"]*      roof["Density"]*     S["Ground_people"]*      width["roof"]
C[18] = ground["Specific heat"]*    ground["Density"]*   S["Ground_animal"]*      width["ground"]
C[20] = ground["Specific heat"]*    ground["Density"]*   S["Ground_people"]*      width["ground"]

C[3] = 0#air["Specific heat"]*air["Density"]*Vol_animal
C[7] = 0#air["Specific heat"]*air["Density"]*Vol_people

C = np.diag(C)

# weather data  
filename = 'FRA_Lyon.074810_IWEC.epw'
[data, meta] = dm4.read_epw(filename, coerce_year=None)
weather_data = data[["temp_air", "dir_n_rad", "dif_h_rad"]]
weather_data.index = weather_data.index.map(lambda t: t.replace(year=2000))
start_date = '2000-06-29 12:00'
end_date = '2000-07-02'
weather_data = weather_data.loc[start_date:end_date]

lat = 45
# orientations of surfaces : 
# slope => 90° is vertical; > 90° downward
# azimuth => 0° South, positive westward 
# latitude => °, North Pole 90° positive
wall_east = {'slope': 90, 'azimuth': -90, 'latitude': lat} 
wall_west = {'slope': 90, 'azimuth': 90, 'latitude': lat} 
wall_north = {'slope': 90, 'azimuth': 180, 'latitude': lat} 
wall_south = {'slope': 90, 'azimuth': 0, 'latitude': lat} 
roof_horizontal = {'slope': 0, 'azimuth': 0, 'latitude': lat} 

albedo = 0.2

rad_surf_east = dm4.sol_rad_tilt_surf(weather_data, wall_east, albedo)
rad_surf_west = dm4.sol_rad_tilt_surf(weather_data, wall_west, albedo)
rad_surf_north = dm4.sol_rad_tilt_surf(weather_data, wall_north, albedo)
rad_surf_south = dm4.sol_rad_tilt_surf(weather_data, wall_south, albedo)
rad_surf_horizon = dm4.sol_rad_tilt_surf(weather_data, roof_horizontal, albedo)

max_dt = dm4.eigenvalues_analysis(C,A,G)
print(max_dt)