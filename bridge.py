import calculate as calc
from graphs import *
import json


f = open("data.json")
data = json.load(f)


def get_FOS(
    top_flange_width,
    web_height,
    diaphragm_num,
    folds,
    max_shear_force,
    max_bending_moment,
):
    cross_section = calc.generate_cross_section(top_flange_width, web_height, folds)

    components = [
        [rectangle[1], rectangle[2], rectangle[3]] for rectangle in cross_section
    ]

    axis = calc.centroidal_axis(components)

    second_moment_area = calc.second_moment_area(components, axis)

    bottom = axis
    top = max([r[0] + r[2] / 2 for r in components]) - axis

    # Tension, Compression

    flexural_stress_at = lambda y: y * max_bending_moment / second_moment_area * 1e3

    max_compression = flexural_stress_at(top)
    max_tension = flexural_stress_at(bottom)

    FOS_wall_tension = calc.matboard_tensile_strength / max_tension
    FOS_wall_compression = calc.matboard_compressive_strength / max_compression

    shear_at = (
        lambda y, b: max_shear_force
        * calc.first_moment_area(components, axis, y)
        / (second_moment_area * b)
    )

    max_shear = shear_at(axis, 2 * calc.th)
    glue_shear = shear_at(calc.th + web_height, 2 * calc.glue_width)

    FOS_wall_shear = calc.matboard_shear_strength / max_shear
    FOS_glue_shear = calc.cement_shear_strength / glue_shear

    buckling_flange_between_webs = calc.thin_plate_buckling(
        4, calc.th * folds, calc.bottom_flange_width - calc.th
    )
    buckling_flange_tips = calc.thin_plate_buckling(
        0.425,
        calc.th * folds,
        (top_flange_width - calc.bottom_flange_width + calc.th) / 2,
    )
    buckling_webs = calc.thin_plate_buckling(6, calc.th, calc.th + web_height - axis)
    buckling_shear = calc.thin_plate_buckling_shear(
        calc.th, web_height - calc.th, calc.bridge_length / (diaphragm_num + 1)
    )

    FOS_buckling_flange_between_webs = buckling_flange_between_webs / max_compression
    FOS_buckling_flange_tips = buckling_flange_tips / max_compression
    FOS_buckling_webs = buckling_webs / max_compression
    FOS_buckling_shear = buckling_shear / max_shear

    print(f"Tension Safety Factor: {FOS_wall_tension}")
    print(f"Compression Safety Factor: {FOS_wall_compression}")
    print(f"Shear Safety Factor: {FOS_wall_shear}")
    print(f"Glue Shear Safety Factor: {FOS_glue_shear}")
    print(f"Buckling Flange Between Webs Safety Factor: {FOS_buckling_flange_between_webs}")
    print(f"Buckling Flange Tips Safety Factor: {FOS_buckling_flange_tips}")
    print(f"Buckling Webs Safety Factor: {FOS_buckling_webs}")
    print(f"Buckling Shear Safety Factor: {FOS_buckling_shear}")


get_FOS(100, 75 - calc.th, 2, 1, 236.555555555556, 75.7564444444445)

# get_FOS(100, 100, 50, 1, 80)
# nodes, top_nodes, bottom_nodes = generate_standard_truss(7, 3, 24)

# bottom_nodes[0].force = (0, 150)
# bottom_nodes[1].force = (0, -60)
# bottom_nodes[2].force = (0, -60)
# bottom_nodes[3].force = (0, -60)
# bottom_nodes[4].force = (0, -60)
# bottom_nodes[5].force = (0, -60)
# bottom_nodes[6].force = (0, 150)


# members = connect_nodes_pratt(top_nodes, bottom_nodes)

# solve_truss(nodes, members)

# print(members)

# plot_bridge(nodes, members, y_bounds=[bottom_nodes[0].y, top_nodes[0].y])
