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


# ['point' ,length (m), force (N)]
# ['distributed' , length (m), uniform load (Nm)]
# ['reaction' , length (m)]
loads = [
    ["reaction", 0],
    # ["distributed", 0, 100],
    ["point", 0.172, 200 / 3],
    ["point", 0.348, 200 / 3],
    ["point", 0.512, 200 / 3],
    ["point", 0.688, 200 / 3],
    ["point", 0.852, 90],
    ["point", 1.082, 90],
    # ["distributed", 1.200, 0],
    ["reaction", 1.200],
]

loads2 = [
    ["reaction", 0],
    ["distributed", 0, 1.096],
    ["reaction", 12],
    ["distributed", 16, 0],
]

shear_force_expr, critical_lengths = calculate.get_shear_force_func(loads)

plt.plot(shear_force_expr, (calculate.x, 0, 1.2))

bending_moment_expr = sy.integrate(shear_force_expr)

plt.plot(bending_moment_expr, (calculate.x, 0, 1.2))

# bending_moment_func = sy.lambdify(calculate.x, bending_moment_expr)(x_array)

max_x, max_y = calculate.highest_bending_moment(critical_lengths, bending_moment_expr)

axis = calculate.centroidal_axis(rectangles)

second_moment_area = calculate.second_moment_area(rectangles, axis)

bounds = [axis, max([r[0] + r[2] / 2 for r in rectangles]) - axis]
print(loads)
print(bounds, max_y, second_moment_area)

stresses = [b * max_y / second_moment_area *1e3 for b in bounds]
print( calculate.matboard_tensile_strength / stresses[0])
print(  calculate.matboard_compressive_strength / stresses[1])

# x_axis, y_axis = calculate.shear_force_data(loads)

# graphs.line_graph(
#     x_axis, y_axis, "Length (m)", "Shear (N)", save_path="img\\design0_SFD"
# )

# x_axis, y_axis = calculate.bending_moment_data(loads)

# graphs.line_graph(x_axis, y_axis, "Length (m)", "Bending Moment (Nm)", invert_y=True, save_path="img\\design0_BMD")

# compression, tension = calculate.flexural_stress(rectangles, y_axis)
# print(f"FOS Compression: {calculate.matboard_compressive_strength/compression}, FOS Tension: {calculate.matboard_tensile_strength/tension}")
