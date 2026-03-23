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
N_windows_animal = 2
N_windows_people = 1

# Surfaces dictionary 
S = {}
S["Window"] = 1*2
S["Windows_animal"] = N_windows_animal*S["Window"]  # for 1 wall
S["Windows_people"] = N_windows_people*S["Window"]  # for 1 wall
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
    "Specific heat": 1000,       # J/(kg⋅K)"
    "Absoptance":0.6,            # NaN
}
isolation = {                    # in cork
    "Conductivity": 0.050,       # W/(m·K)
    "Density": 200.0,            # kg/m³
    "Specific heat": 1560,       # J/(kg⋅K)"
	"Absoptance":0.6,            # NaN
}
roof = {                         # in wood / oak
    "Conductivity": 0.180,       # W/(m·K)
    "Density": 2000.0,           # kg/m³
    "Specific heat": 705,        # J/(kg⋅K)"
    "Absoptance":0.7,            # NaN
}
glass = {                         
    "Conductivity": 1.400,       # W/(m·K)
    "Density": 2500.0,           # kg/m³
    "Specific heat": 750,        # J/(kg⋅K)"
	"Transmitance":0.8,			 # NaN
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
ACH = 1
Qa = 200

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

#C[3] = air["Specific heat"]*air["Density"]*Vol_animal
#C[7] = air["Specific heat"]*air["Density"]*Vol_people

C = np.diag(C)

# weather data  
filename = 'FRA_Lyon.074810_IWEC.epw'
[data, meta] = dm4.read_epw(filename, coerce_year=None)
weather_data = data[["temp_air", "dir_n_rad", "dif_h_rad"]]
weather_data.index = weather_data.index.map(lambda t: t.replace(year=2000))
start_date = '2000-06-29 12:00'
end_date = '2000-07-02'
weather_data = weather_data.loc[start_date:end_date]
calendar = weather_data.index

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

max_dt,zero,nonzero = dm4.eigenvalues_analysis(C,A,G)
dt = 3600
if max_dt<dt:
	print("System is chaotic")
	quit()

dt_H = dt/3600

Ntps = len(weather_data)

θ = np.zeros((nθ,Ntps))
q = np.zeros((nq,Ntps))
b = np.zeros((nq,Ntps)) 
f = np.zeros((nθ,Ntps))


for i in range(Ntps):
	Etot = {}
	Etot["N"] = rad_surf_north.at[calendar[i],"total"]
	Etot["S"] = rad_surf_south.at[calendar[i],"total"]
	Etot["W"] = rad_surf_west.at[calendar[i],"total"]
	Etot["E"] = rad_surf_east.at[calendar[i],"total"]
	Etot["H"] = rad_surf_horizon.at[calendar[i],"total"]
	Ew_animal = glass["Transmitance"]*S["Windows_animal"]*(Etot["W"] + Etot["E"])
	Ew_people = glass["Transmitance"]*S["Windows_animal"]*(Etot["W"] + Etot["E"])

	f[3,i] = Qa

	f[0,i] = 	stone["Absoptance"]*	(S["North_facade"]*Etot["N"] + S["Facade_animal"]*Etot["W"] + S["Facade_animal"]*Etot["E"])
	f[11,i] = 	isolation["Absoptance"]*(S["North_facade"]*Etot["N"] + S["Facade_people"]*Etot["W"] + S["Facade_people"]*Etot["E"])
	f[12,i] = 	roof["Absoptance"]*		S["Ground_animal"]*Etot["H"]
	f[15,i] = 	roof["Absoptance"]*		S["Ground_people"]*Etot["H"]

	f[2,i] = Ew_animal*S["Outdoor_wall_animal"]/S["Total_animal"]
	f[4,i] = Ew_animal*S["North_facade"]/S["Total_animal"]
	f[14,i] = Ew_animal*S["Ground_animal"]/S["Total_animal"]
	f[19,i] = f[14,i]
	f[8,i] = Ew_people*S["Outdoor_wall_people"]/S["Total_people"]
	f[6,i] = Ew_people*S["North_facade"]/S["Total_people"]
	f[17,i] = Ew_people*S["Ground_people"]/S["Total_people"]
	f[21,i] = f[17,i]

	Te = weather_data.at[calendar[i],'temp_air']
	b[:,i] = dm4.temperature(Tg,Tc,Te,nq)

# thermal circuit

K = -A.T @ G @ A
K11 = K[zero,:]
K11 = K11[:,zero]
K12 = K[zero,:]
K12 = K12[:,nonzero]
K21 = K[nonzero,:]
K21 = K21[:,zero]
K22 = K[nonzero,:]
K22 = K22[:,nonzero]
Cc = C[nonzero,:]
Cc = Cc[:,nonzero]
K11_inv = np.linalg.inv(K11)
As = np.linalg.inv(Cc) @ (-K21 @ K11_inv @ K12 + K22)

for i in range(Ntps-1):
	J = A.T @ G @ b[:,i]

	if i == 0:
		θ[:,i] = np.linalg.inv(-K) @ (J+f[:,i])
	Bs_u = np.linalg.inv(Cc) @ (-K21 @ K11_inv @ J[zero] +J[nonzero] -K21 @ K11_inv @ f[zero,i] +f[nonzero,i])
	θ[nonzero,i+1] = (np.eye(len(nonzero)) + As*dt) @ θ[nonzero,i] + Bs_u
	θ[zero,i+1] = -K11_inv @ (K12 @ θ[nonzero,i+1] + J[zero]) + f[zero,i]
	
