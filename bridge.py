import calculate as calc
from graphs import *
import json
from scipy.optimize import minimize


f = open("data.json")
data = json.load(f)


def get_FOS(
    top_flange_width,
    web_height,
    folds = 1,
    diaphragm_num = 1,
    max_shear_force = float(data['shear']),
    max_bending_moment = float(data['moment']),
    glue_width = calc.glue_width,
    print_FOS=False,
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
    glue_shear = shear_at(calc.th + web_height, 2 * glue_width)

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
    # print( 0.425,
    #     calc.th * folds,
    #     (top_flange_width - calc.bottom_flange_width + calc.th) / 2)
    buckling_webs = calc.thin_plate_buckling(6, calc.th, calc.th + web_height - axis)
    buckling_shear = calc.thin_plate_buckling_shear(
        calc.th, web_height - calc.th, calc.bridge_length / (diaphragm_num + 1)
    )

    FOS_buckling_flange_between_webs = buckling_flange_between_webs / max_compression
    FOS_buckling_flange_tips = buckling_flange_tips / max_compression
    FOS_buckling_webs = buckling_webs / max_compression
    FOS_buckling_shear = buckling_shear / max_shear

    # Approximate volume of bridge
    area = calc.area(components)
    diaphragm_thickness = calc.th * (diaphragm_num + 2)
    cross_section_thickness = calc.bridge_length - diaphragm_thickness
    diaphragm_area = (2 * calc.th + web_height) * calc.bottom_flange_width
    volume = area * cross_section_thickness + diaphragm_area * diaphragm_thickness

    final_FOS = min(
        FOS_wall_tension,
        FOS_wall_compression,
        FOS_wall_shear,
        FOS_glue_shear,
        FOS_buckling_flange_between_webs,
        FOS_buckling_flange_tips,
        FOS_buckling_webs,
        FOS_buckling_shear,
    )

    if print_FOS:
        
        # print(f"Glue Width: {glue_width}")
        print(f"Bottom Flange Width: {calc.bottom_flange_width}")
        print(f"Top Flange Width: {top_flange_width}")
        print(f"Web Height: {web_height}")
        print(f"Number of Diaphragms: {diaphragm_num}")
        print(f"Top Flange Layers: {folds}")
        print(f"Glue Width: {glue_width}")
        
        print(f"Tension Safety Factor: {FOS_wall_tension}")
        print(f"Compression Safety Factor: {FOS_wall_compression}")
        print(f"Shear Safety Factor: {FOS_wall_shear}")
        print(f"Glue Shear Safety Factor: {FOS_glue_shear}")
        print(
            f"Buckling Flange Between Webs Safety Factor: {FOS_buckling_flange_between_webs}"
        )
        print(f"Buckling Flange Tips Safety Factor: {FOS_buckling_flange_tips}")
        print(f"Buckling Webs Safety Factor: {FOS_buckling_webs}")
        print(f"Buckling Shear Safety Factor: {FOS_buckling_shear}")
        print(f"Volume: {volume}")
        print(f"Percent of Matboard: {volume/1049030.16*100}")
        
        print(f"Maximum Force: {final_FOS * 446.66}")
    if volume/1049030.16 < 0.9:
        
        return final_FOS
    return -1



# get_FOS(100, 75 - calc.th, 1, 2, 236.555555555556, 75.7564444444445, print_FOS=True, glue_width=5)
fos = 0
oheight = None
othickness = None
owidth = None
odiaphragm = None

for height in range(20, 121, 20):
    for thickness in range(1, 6):
        for width in range(100, 150):
            for diaphragm in range(1,4):
                new_fos =  get_FOS(width, height - calc.th-thickness*calc.th, thickness, diaphragm, print_FOS=False)

                if new_fos > fos:
                    oheight = height
                    fos = new_fos
                    othickness = thickness
                    odiaphragm = diaphragm
                    owidth = width

get_FOS(125, oheight - calc.th-othickness*calc.th, othickness, odiaphragm, print_FOS=True)
# def objective(x):
#     top_flange_width, web_height = x
#     return get_FOS(top_flange_width, web_height, 3, 1)
# x0 = [100, 75 - calc.th]
# bnds = ((20,300),(10,200))
# print(minimize(objective, x0, method="Powell", bounds=bnds))

# get_FOS(114.3, 85.20, 3, 1, print_FOS=True)
# # get_FOS(100, 100, 50, 1, 80)
# nodes, top_nodes, bottom_nodes = generate_standard_truss(7, 3, 24)

