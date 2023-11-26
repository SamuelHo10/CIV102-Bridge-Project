import calculate as calc
from graphs import *
import json

f = open("data.json")
data = json.load(f)
f2 = open("data2.json")
data2 = json.load(f2)

max_shear_force = float(data["shear"])
max_bending_moment = float(data["moment"])


def get_FOS(
    top_flange_width,
    web_height,
    top_flange_layers=1,
    diaphragm_num=1,
    max_shear_force=max_shear_force,
    max_bending_moment=max_bending_moment,
    glue_width=calc.glue_width,
    print_FOS=False,
    return_min=True,
):
    cross_section = calc.generate_cross_section(top_flange_width, web_height, top_flange_layers)

    components = [
        [rectangle[1], rectangle[2], rectangle[3]] for rectangle in cross_section
    ]

    axis = calc.centroidal_axis(components)

    second_moment_area = calc.second_moment_area(components, axis)

    bottom = axis
    top = max([r[0] + r[2] / 2 for r in components]) - axis

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
        4, calc.th * top_flange_layers, calc.bottom_flange_width - calc.th
    )
    
    buckling_flange_tips = calc.thin_plate_buckling(
        0.425,
        calc.th * top_flange_layers,
        (top_flange_width - calc.bottom_flange_width + calc.th) / 2,
    )

    buckling_webs = calc.thin_plate_buckling(6, calc.th, calc.th + web_height - axis)
    
    buckling_shear = calc.thin_plate_buckling_shear(
        calc.th * 2, web_height - calc.th, calc.bridge_length / (diaphragm_num + 1)
    )

    FOS_buckling_flange_between_webs = buckling_flange_between_webs / max_compression
    FOS_buckling_flange_tips = buckling_flange_tips / max_compression
    FOS_buckling_webs = buckling_webs / max_compression
    FOS_buckling_shear = buckling_shear / max_shear

    # Approximate volume of bridge (Not exact)
    area = calc.area(components)
    diaphragm_thickness = calc.th * (
        diaphragm_num + 3
    )  # Must add 3 to include double diaphragms in the middle and on both ends of the bridge
    cross_section_thickness = (
        calc.bridge_length + 60
    )  # Add 60 for both ends of the bridge
    diaphragm_area = (2 * calc.glue_width + web_height) * (
        calc.bottom_flange_width - 2 * calc.th + calc.glue_width * 2
    )
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
        print("Dimensions: ")
        print(f"Bottom Flange Width: {calc.bottom_flange_width}")
        print(f"Top Flange Width: {top_flange_width}")
        print(f"Web Height: {web_height}")
        print(f"Number of Diaphragms: {diaphragm_num}")
        print(f"Top Flange Layers: {top_flange_layers}")
        print(f"Glue Width: {glue_width}")

        print("\nFOS:")
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

        print(f"\nVolume: {volume}")
        print(f"Percent of Matboard: {volume/1049030.16*100}")

        print(f"\nMaximum Load: {final_FOS * 446.66}")

    if return_min:
        # Volume must be less than 90% of total matboard
        if volume / 1049030.16 < 0.9:
            return final_FOS
        return -1

    return (
        FOS_wall_tension,
        FOS_wall_compression,
        FOS_wall_shear,
        FOS_glue_shear,
        FOS_buckling_flange_between_webs,
        FOS_buckling_flange_tips,
        FOS_buckling_webs,
        FOS_buckling_shear,
    )


### Code For Optimization ###

fos = 0
oheight = None
othickness = None
owidth = None
odiaphragm = None

# Loop through range of values to try to find the optimal dimensions
# for height in range(20, 121, 20):
#     for thickness in range(1, 6):
#         for width in range(100, 150):
#             for diaphragm in range(1,4):
#                 new_fos =  get_FOS(width, height - calc.th-thickness*calc.th, thickness, diaphragm, print_FOS=False)

#                 if new_fos > fos:
#                     oheight = height
#                     fos = new_fos
#                     othickness = thickness
#                     odiaphragm = diaphragm
#                     owidth = width

# Changed width to 125, so we can fit it on matboard

### Final Bridge Dimensions ###

owidth = 125
othickness = 2
odiaphragm = 3
oheight = 100

print("Load Case 1:")
factors_1 = get_FOS(
    owidth,
    oheight - calc.th - othickness * calc.th,
    othickness,
    odiaphragm,
    print_FOS=True,
    return_min=False,
    max_shear_force=float(data2["shear"]),
    max_bending_moment=float(data2["moment"]),
)



print("Load Case 2:")
factors_2 = get_FOS(
    owidth,
    oheight - calc.th - othickness * calc.th,
    othickness,
    odiaphragm,
    print_FOS=True,
    return_min=False,
)

### Generate Graphs ###
def generate_graphs(data, factors, folder_name):
    max_shear_force = float(data["shear"])
    max_bending_moment = float(data["moment"])
    x_vals = [float(d) for d in data["x"]]
    shear_force_envelope = [float(d) for d in data["shear_force_envelope"]]
    bending_moment_envelop = [float(d) for d in data["bending_moment_envelope"]]

    names = (
        "tension_failiure",
        "compression_failiure",
        "shear_failiure",
        "glue_shear_failiure",
        "buckling_flange_between_webs_failiure",
        "buckling_flange_tips_failiure",
        "buckling_webs_failiure",
        "buckling_shear_webs_failiure",
    )
    is_shear = (False, False, True, True, False, False, False, True)

    for i in range(len(factors)):
        formatted_name = names[i].replace("_", " ").title()
        if is_shear[i]:
            values = [factors[i] * max_shear_force] * len(x_vals)
            plot_expr(
                [shear_force_envelope, values, np.array(values) * -1],
                x_vals,
                x_axis_label="Length (m)",
                y_axis_label="Shear Force (N)",
                save_path="img\\" + folder_name +"\\" + names[i] + ".png",
                show=False,
                multiple_graphs=True,
                labels=("Applied Shear Force", formatted_name, ""),
            )
        else:
            values = [factors[i] * max_bending_moment] * len(x_vals)
            plot_expr(
                [bending_moment_envelop, values],
                x_vals,
                x_axis_label="Length (m)",
                y_axis_label="Bending Moment (Nm)",
                save_path="img\\" + folder_name +"\\" + names[i] + ".png",
                show=False,
                invert_y=True,
                multiple_graphs=True,
                labels=("Applied Bending Moment", formatted_name),
            )

generate_graphs(data2, factors_1, "load_case_1")
generate_graphs(data, factors_2, "load_case_2")