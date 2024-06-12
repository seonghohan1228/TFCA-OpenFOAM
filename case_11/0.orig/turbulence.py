NU_WATER = 0.0000008917  # at 298 K
NU_AIR = 0.00001552  # at 298 K
RHO_WATER = 998
RHO_AIR = 1.2
SIGMA = 0.072

d1 = 0.005  # m
a = 0.0001
h = 0.0025

v2 = 10

print(f"  Water diameter (m)\t: {d1}")
print(f"  Air gap (m)\t\t: {h}")

d2 = d1 + 2*a
d3 = d2 + 2*h

r1 = d1/2
r2 = d2/2
r3 = d3/2

print(f"  Air velocity (m/s)\t: {v2}")
v1 = float(input("  Water velocity (m/s)\t: "))

Re1 = v1 * d1 / NU_WATER
We1 = RHO_WATER * v1**2 * d1 / SIGMA
I1 = 0.16 * Re1**(-1/8)
k1 = 1.5*(v1*I1)**2
epsilon1 = 0.09**0.75 * k1**1.5 / d1

Re2 = v2 * (r3 - r2) / NU_AIR /2
We2 = RHO_AIR * v2**2 * (r3 - r2) / SIGMA
if Re2 != 0:
	I2 = 0.16 * Re2**(-1/8)
else:
	I2 = 0
k2 = 1.5*(v2*I2)**2
epsilon2 = 0.09**0.75 * k2**1.5 / ((d3 - d2)/2)

print("------------------------------")
print("  Water")
print(f"  Re\t\t: {Re1:.0f}")
print(f"  We\t\t: {We1:.2f}")
print(f"  I\t\t: {I1:.6f}")
print(f"  k\t\t: {k1:.6f}")
print(f"  epsilon\t: {epsilon1:.6f}")
print()
print("  Air")
print(f"  Re\t\t: {Re2:.0f}")
print(f"  We\t\t: {We2:.2f}")
print(f"  I\t\t: {I2:.6f}")
print(f"  k\t\t: {k2:.6f}")
print(f"  epsilon\t: {epsilon2:.6f}")
print("------------------------------")
print()
print("End")



