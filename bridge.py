from calculate import *
from graphs import *


def get_FOS(
    top_flange_width, bottom_flange_width, webs_height, diaphragm_num, web_spacing, max_shear_force, max_bending_moment
):
    cross_section = generate_cross_section(
        top_flange_width, bottom_flange_width, webs_height, web_spacing
    )

    print(cross_section)

loads = [
    ["reaction", 0],
    ["point", 0.172, 200 / 3],
    ["point", 0.348, 200 / 3],
    ["point", 0.512, 200 / 3],
    ["point", 0.688, 200 / 3],
    ["point", 0.852, 90],
    ["point", 1.028, 90],
    ["reaction", 1.200],
]
data = generate_envelop(-0.1, 0.1, 200, loads, 1000)

print(data[1])

plot_sympy(
    data[0],
    data[1],
    (0, 1.2),
    x_axis_label="Length (m)",
    y_axis_label="Shear Force (N)",
    fill=True,
    save_path="img\\SFD_envelop.png",
    show=True,
)


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
