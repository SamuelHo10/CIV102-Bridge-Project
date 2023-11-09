import calculate
import graphs
import sympy.plotting as plt
import sympy as sy
import scipy

# [distance from base, width, height]
rectangles = [
    [75 + 1.27 / 2, 100, 1.27],
    [75 - 1.27 / 2, 5, 1.27],
    [75 - 1.27 / 2, 5, 1.27],
    [75 / 2, 1.27, 75],
    [75 / 2, 1.27, 75],
    [1.27 / 2, 80 - 2 * 1.27, 1.27],
]



# ['point' ,length (m), force (kN)]
# ['distributed' , length (m), uniform load (kNm)]
# ['reaction' , length (m)]
loads = [
    ["reaction", 0],
    ["distributed", 0, calculate.area(rectangles) / 1e6 * calculate.matboard_density],
    ["point", 0.172, 200 / 3],
    ["point", 0.348, 200 / 3],
    ["point", 0.512, 200 / 3],
    ["point", 0.688, 200 / 3],
    ["point", 0.852, 90],
    ["point", 1.028, 90],
    ["distributed", 1.200, 0],
    ["reaction", 1.200],
]

shear_force_expr, critical_lengths = calculate.get_shear_force_func(loads)

plt.plot(shear_force_expr, (calculate.x, 0, 1.2))

bending_moment_expr = sy.integrate(shear_force_expr)

plt.plot(bending_moment_expr, (calculate.x, 0, 1.2))

max_x, max_y = calculate.highest_bending_moment(critical_lengths, bending_moment_expr)

axis = calculate.centroidal_axis(rectangles)

second_moment_area = calculate.second_moment_area(rectangles, axis)

bounds = [axis, max([r[0] + r[2] / 2 for r in rectangles]) - axis]
print(loads)
print(axis)
print(bounds, max_y, second_moment_area)

stresses = [b * max_y / second_moment_area *1e3 for b in bounds]
print( calculate.matboard_tensile_strength / stresses[0])
print(  calculate.matboard_compressive_strength / stresses[1])