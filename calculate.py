import numpy as np
import sympy as sy

x = sy.Symbol("x", real=True)

matboard_tensile_strength = 30  # MPa
matboard_compressive_strength = 6  # MPa
matboard_shear_strength = 4  # MPa
matboard_youngs_modulus = 4000  # MPa
matboard_poissons_ratio = 0.2
cement_shear_strength = 2  # MPa
bridge_length = 1200  # mm
matboard_density = 625 / 826008 * 1e3 * 9.81  # kN / m^3

### Add functions to calculate values here ###


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


def highest_bending_moment(critical_lengths, bending_moment_expr):
    """
    Find the highest point in a bending moment function.

    Args:
        critical_lengths (list): a list containing all lengths to be checked.
        bending_moment_expr (Any): The bending moment sympy expression.

    Returns:
        tuple: (length, highest_bending_moment)
    """
    critical_lengths = list(set(critical_lengths))
    highest_moment = 0
    highest_index = None
    for i in range(len(critical_lengths)):
        moment = bending_moment_expr.subs(x, critical_lengths[i])

        if abs(moment) > highest_moment:
            highest_moment = moment
            highest_index = i
    return critical_lengths[highest_index], highest_moment


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
        shear_forces.append((load[1] - (x - load[0]) * load[2], load[0] < x))

        if load[2] != 0:
            critical_lengths.append(load[1] / load[2] + load[0])

    shear_forces = shear_forces[::-1]

    # Define all other values
    shear_forces.append((0, True))

    return sy.Piecewise(*shear_forces), critical_lengths


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.nodes = []
    
    def __repr__(self):
        return f"[{self.x},{self.y}]"


class Member:
    def __init__(self, n1, n2):
        self.nodes = (n1, n2)


def connect_nodes(a, b):
    member = Member(a, b)
    a.nodes.append(member)
    b.nodes.append(member)


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
    length_top = len(top_nodes)
    length_bottom = len(bottom_nodes)

    # Connect top nodes
    for i in range(length_top - 1):
        connect_nodes(top_nodes[i], top_nodes[i + 1])

    # Connect bottom nodes
    for i in range(length_bottom - 1):
        connect_nodes(bottom_nodes[i], bottom_nodes[i + 1])

    for i in range(length_top):
        connect_nodes(top_nodes[i], bottom_nodes[i + 1])

    for i in range((length_top + 1) / 2):
        connect_nodes(bottom_nodes[i], top_nodes[i])
        connect_nodes(
            bottom_nodes[length_bottom - 1 - i], top_nodes[length_top - 1 - i]
        )
