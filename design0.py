import calculate
import graphs
import sympy as sy

hmm = calculate.generate_cross_section(100, 80, 75-calculate.th)
print(hmm)
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
    # ["distributed", 0, calculate.area(rectangles) / 1e6 * calculate.matboard_density],
    ["point", 0.172, 200 / 3],
    ["point", 0.348, 200 / 3],
    ["point", 0.512, 200 / 3],
    ["point", 0.688, 200 / 3],
    ["point", 0.852, 90],
    ["point", 1.028, 90],
    # ["distributed", 1.200, 0],
    ["reaction", 1.200],
]

shear_force_expr, critical_lengths = calculate.get_shear_force_func(loads)

graphs.plot_sympy(
    shear_force_expr,
    calculate.x,
    (0, 1.2),
    x_axis_label="Length (m)",
    y_axis_label="Shear Force (N)",
    fill=True,
    save_path="img\\design0_SFD.png",
    show=False,
)

bending_moment_expr = sy.integrate(shear_force_expr)

graphs.plot_sympy(
    bending_moment_expr,
    calculate.x,
    (0, 1.2),
    x_axis_label="Length (m)",
    y_axis_label="Bending Moment (Nm)",
    fill=True,
    save_path="img\\design0_BMD.png",
    invert_y=True,
    show=False,
)

max_x, max_y = calculate.max_expression(critical_lengths, abs(bending_moment_expr))

axis = calculate.centroidal_axis(rectangles)

second_moment_area = calculate.second_moment_area(rectangles, axis)

bounds = [axis, max([r[0] + r[2] / 2 for r in rectangles]) - axis]

stresses = [b * max_y / second_moment_area * 1e3 for b in bounds]

print("Loads:")
for load in loads:
    print(load)
print(f"Centroidal Axis: {axis}")
print(f"Second Moment of Area: {second_moment_area}")
print(f"Bounds: {bounds}")
print(f"Maximum Bending Moment: {max_y}")
print(f"Tension Safety Factor: {calculate.matboard_tensile_strength / stresses[0]}")
print(
    f"Compression Safety Factor: {calculate.matboard_compressive_strength / stresses[1]}"
)
