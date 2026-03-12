from Beam import *

points = [(0.2, 0.071507), (0.65, 0.071822), (0.65, -0.021653), (0.2, -0.034334)]
data = [(0, 15), (1, 10), (2, 5), (3, 0)] # (y, M)

beam = Beam()
beam.load_wing_box(points=points, thickness=0.00001)
beam.get_I_of_cross_section()
print(beam.Ixx, beam.Izz)

# u a bitch micah