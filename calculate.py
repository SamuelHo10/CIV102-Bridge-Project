import numpy
import numpy as np
import sympy as sy
from copy import deepcopy

x = sy.Symbol("x", real=True)

matboard_tensile_strength = 30  # MPa
matboard_compressive_strength = 6  # MPa
matboard_shear_strength = 4  # MPa
matboard_youngs_modulus = 4000  # MPa
matboard_poissons_ratio = 0.2
cement_shear_strength = 2  # MPa
bridge_length = 1200  # mm
matboard_density = 625 / 826008 * 1e3 * 9.81  # kN / m^3
th = 1.27  # mm
glue_width = 10  # mm
### Add functions to calculate values here ###


def generate_cross_section(top_flange_width, bottom_flange_width, web_height):
    # (x, y, w ,h)
    return [
        (0, th / 2, bottom_flange_width, th),  # bottom flange
        (
            (bottom_flange_width  - th)/ 2,
            th + web_height / 2,
            th,
            web_height,
        ),  # right web
        (
            -bottom_flange_width / 2 + th / 2,
            th + web_height / 2,
            th,
            web_height,
        ),  # left web
        (
            (bottom_flange_width - th - glue_width) / 2,
            th / 2 + web_height,
            glue_width - th,
            th,
        ),  # glue top right
        (
            -web_spacing + glue_width / 2,
            th / 2 + web_height,
            glue_width - th,
            th,
        ),  # glue top left
        (
            web_spacing - glue_width / 2,
            3 * th / 2,
            glue_width - th,
            th,
        ),  # glue bottom right
        (
            -web_spacing + glue_width / 2,
            3 * th / 2,
            glue_width - th,
            th,
        ),  # glue bottom left
        (0, 3 * th / 2 + web_height, top_flange_width, th),  # top flange
    ]


def area(components):
    """Calculates the cross-sectional area of the components.

    Args:
        components (list): Contains rectangles with postion, width, and height.

    Returns:
        float: The area.
    """
    sum1 = 0
    for component in components:
        sum1 += component[2] * component[2]
    return sum1


def centroidal_axis(components):
    """Calculates the location of the centroidal axis relative to the lowest point.

    Args:
        components (list): Contains rectangles with postion, width, and height.

    Returns:
        float: The location of the centroidal axis.
    """
    sum1 = sum2 = 0
    for component in components:
        component_area = component[1] * component[2]
        sum1 += component[0] * component_area
        sum2 += component_area
    return sum1 / sum2


def second_moment_area(components, axis):
    """Calculates the second moment of area of all the components.

    Args:
        components (list): Contains rectangles with postion, width, and height.
        axis (float): Location of the centroidal axis relative to the lowest point.

    Returns:
        float: The second moment of area.
    """
    sum1 = 0
    for c in components:
        sum1 += (c[1] * c[2] ** 3) / 12 + c[1] * c[2] * (axis - c[0]) ** 2
    return sum1


def max_expression(critical_values, expr):
    """
    Find the highest point in a function given the critical values.

    Args:
        critical_values (list): a list containing all critical values to be checked.
        expr (Any): a sympy expression.

    Returns:
        tuple: (value, max_value)
    """
    critical_values = list(set(critical_values))
    max_value = 0
    max_index = None
    for i in range(len(critical_values)):
        moment = expr.subs(x, critical_values[i])

        if moment > max_value:
            max_value = moment
            max_index = i
    return critical_values[max_index], max_value


def calc_reaction_forces(loads):
    """
    Calculates reaction forces and appends it to the reaction force array within loads. Works only with point loads and distributed loads.

    Args:
        loads: (list)
        A list containing all external forces applied to the member.
    """

    # Separate the different types of forces
    point_loads = [load for load in loads if load[0] == "point"]
    distributed_loads = [load for load in loads if load[0] == "distributed"]
    reaction_forces = [load for load in loads if load[0] == "reaction"]

    if len(reaction_forces) != 2:
        print("Invalid Reaction Forces.")

    # Loop twice to calculate each reaction force.
    for j in range(2):
        reaction_length = reaction_forces[j % 2][1]
        pivot_length = reaction_forces[(j + 1) % 2][1]

        # Sum up the moments of the point loads.
        point_sum = sum([(load[2] * (load[1] - pivot_length)) for load in point_loads])

        # Sum up moments of the distributed loads
        distributed_sum = 0
        for i in range(0, len(distributed_loads) - 1):
            length = distributed_loads[i + 1][1] - distributed_loads[i][1]
            radius = (
                distributed_loads[i][1] + distributed_loads[i + 1][1]
            ) / 2 - pivot_length
            distributed_sum += length * radius * distributed_loads[i][2]

        # Divide sum of moments by distance to get reaction force.
        reaction_forces[j % 2].append(
            -(distributed_sum + point_sum) / (reaction_length - pivot_length)
        )


def merge_forces(loads):
    """
    Converts the provided loads, and solves for the coefficients for the shear force piecewise equation.

    Args:
        loads: (list)
        A list containing all external forces applied to the member with solved reaction forces.

    Returns:
        list: Values for [length, starting force, slope] at each point where the applied force changes.
    """

    current_distributed_force = 0
    point_force_sum = 0
    merged_loads = []

    # Sum up point forces, determine the value of distributed force at each point, and combine forces which are applied at the same point.
    for i in range(0, len(loads)):
        if loads[i][0] == "point" or loads[i][0] == "reaction":
            point_force_sum -= loads[i][2]

        elif loads[i][0] == "distributed":
            current_distributed_force = loads[i][2]

        if i == len(loads) - 1 or loads[i][1] != loads[i + 1][1]:
            merged_loads.append(
                [loads[i][1], point_force_sum, current_distributed_force]
            )

    previous_length = None
    distributed_force_sum = 0

    # Add distributed force sum to point force sum to get the starting value.
    for load in merged_loads:
        if previous_length != None:
            distributed_force_sum += load[2] * (load[0] - previous_length)

            load[1] -= distributed_force_sum

        previous_length = load[0]

    return merged_loads


def get_shear_force_func(loads):
    """
    Creates a function for shear force.

    Args:
        loads: (list)
        A list containing all external forces applied to the member.

    Returns:
        sympy.Piecewise: A piecewise function representing shear force.
        list: A list containing critical values of the function.
    """

    calc_reaction_forces(loads)

    loads = merge_forces(loads)

    critical_lengths = [load[0] for load in loads]

    shear_forces = []

    for load in loads:
        # print(sy.Float(load[0]) < x)
        shear_forces.append((load[1] - (x - load[0]) * load[2], sy.Float(load[0]) < x))

        if load[2] != 0:
            critical_lengths.append(load[1] / load[2] + load[0])

    shear_forces = shear_forces[::-1]

    # Define all other values
    shear_forces.append((0, True))

    return sy.Piecewise(*shear_forces), critical_lengths


def generate_envelop(start, stop, num, loads, spacing):
    load_positions = np.linspace(start, stop, num)
    shear_force_envelop = []
    bending_moment_envelop = []
    max_shear_force = 0
    max_bending_moment = 0
    x_vals = np.linspace(0, bridge_length, spacing)

    for load_position in load_positions:
        # shift positions of loads
        new_loads = deepcopy(loads)
        for load in new_loads:
            if load[0] == "point" or load[0] == "distributed":
                load[1] += load_position
        print(new_loads)
        # calculate bending moment and shear force expressions
        shear_force_expr, critical_lengths = get_shear_force_func(new_loads)
        bending_moment_expr = sy.integrate(shear_force_expr)

        shear_force_func = sy.lambdify(x, shear_force_expr)
        bending_moment_func = sy.lambdify(x, bending_moment_expr)

        shear_force_envelop.append(shear_force_func(x_vals))
        bending_moment_envelop.append(bending_moment_func(x_vals))

        max_shear_force = max(
            max_expression(critical_lengths, shear_force_expr)[1], max_shear_force
        )
        max_bending_moment = max(
            max_expression(critical_lengths, bending_moment_expr)[1], max_bending_moment
        )

        return (
            x_vals,
            shear_force_envelop,
            bending_moment_envelop,
            max_shear_force,
            max_bending_moment,
        )


def thin_plate_stress(top_base):
    return (4 * (numpy.pi ** 2) * matboard_youngs_modulus / (12 * ((1 - matboard_poissons_ratio) ** 2))) * (th / top_base) ** 2


def thin_plate_shear(top_base, diaphragm_spacing):
    return (5 * (numpy.pi ** 2) * matboard_youngs_modulus / (12 * ((1 - matboard_poissons_ratio) ** 2))) * ((th/diaphragm_spacing)**2 + (th/top_base)**2)


### CODE FOR TRUSS BRIDGES ###


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.members = []
        self.force = (0, 0)

    def __repr__(self):
        return f"[{self.x},{self.y}]"


class Member:
    def __init__(self, n1, n2, id):
        self.nodes = (n1, n2)
        self.id = id

    def __repr__(self):
        return str(self.force)


def connect_nodes(a, b, id):
    member = Member(a, b, id)
    a.members.append((member, b))
    b.members.append((member, a))
    return member


def generate_standard_truss(num_horizontal_nodes, height, length):
    top_nodes = []
    bottom_nodes = []
    nodes = []

    for n in range(num_horizontal_nodes):
        node = Node(length / (num_horizontal_nodes - 1) * n, 0)
        bottom_nodes.append(node)
        nodes.append(node)

    for n in range(1, num_horizontal_nodes - 1):
        node = Node(length / (num_horizontal_nodes - 1) * n, height)
        top_nodes.append(node)
        nodes.append(node)

    return nodes, top_nodes, bottom_nodes


def connect_nodes_pratt(top_nodes, bottom_nodes):
    id = 0
    length_top = len(top_nodes)
    length_bottom = len(bottom_nodes)
    node_pairs = []
    members = []

    node_pairs.extend([(top_nodes[i], top_nodes[i + 1]) for i in range(length_top - 1)])

    node_pairs.extend(
        [(bottom_nodes[i], bottom_nodes[i + 1]) for i in range(length_bottom - 1)]
    )

    node_pairs.extend([(top_nodes[i], bottom_nodes[i + 1]) for i in range(length_top)])

    for i in range((length_top + 1) // 2):
        node_pairs.append((bottom_nodes[i], top_nodes[i]))
        node_pairs.append(
            (bottom_nodes[length_bottom - 1 - i], top_nodes[length_top - 1 - i])
        )

    for node_pair in node_pairs:
        members.append(connect_nodes(node_pair[0], node_pair[1], id))
        id += 1

    return members


def solve_truss(nodes, members):
    num_members = len(members)
    A = []
    B = []
    for i in range(len(nodes)):
        row_x = [0] * num_members
        row_y = [0] * num_members
        node = nodes[i]
        for f in node.members:
            member = f[0]
            other_node = f[1]
            angle = np.arctan2(other_node.y - node.y, other_node.x - node.x)
            row_x[member.id] = np.cos(angle)
            row_y[member.id] = np.sin(angle)
        A.extend([row_x, row_y])
        B.extend([-node.force[0], -node.force[1]])

    member_forces = np.linalg.lstsq(A, B)[0]

    for i in range(num_members):
        members[i].force = member_forces[i]
