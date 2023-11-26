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
th = 1.27  # mm
glue_width = 10  # mm
bottom_flange_width = th + 65

# # Comment out if not using design 0
# glue_width = th + 5  # mm
# bottom_flange_width = 80
### Add functions to calculate values here ###


def generate_cross_section(top_flange_width, web_height, top_flange_layers):
    # (x, y, w ,h)
    return [
        (0, th / 2, bottom_flange_width, th),  # bottom flange
        (
            (bottom_flange_width - th) / 2,
            th + web_height / 2,
            th,
            web_height,
        ),  # right web
        (
            (-bottom_flange_width + th) / 2,
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
            (-bottom_flange_width + th + glue_width) / 2,
            th / 2 + web_height,
            glue_width - th,
            th,
        ),  # glue top left
        (
            0,
            th + (th * top_flange_layers) / 2 + web_height,
            top_flange_width,
            th * top_flange_layers,
        ),  # top flange
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
        sum1 += component[1] * component[2]
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


def first_moment_area(components, axis, y):
    cropped_components = []
    for c in components:
        if c[0] - c[2] / 2 > y:
            continue
        elif c[0] + c[2] / 2 < y:
            cropped_components.append(c)
        else:
            top = y
            bottom = c[0] - c[2] / 2
            cropped_components.append([(top + bottom) / 2, c[1], top - bottom])

    sum1 = 0
    for c in cropped_components:
        sum1 += (axis - c[0]) * c[1] * c[2]
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


def generate_envelop(start, stop, num_load_positions, loads, num_length_positions):
    load_positions = np.linspace(start, stop, num_load_positions)
    shear_force_envelop = np.zeros(num_length_positions)
    bending_moment_envelop = np.zeros(num_length_positions)
    max_shear_force = 0
    max_bending_moment = 0
    x_vals = np.linspace(0, bridge_length / 1000, num_length_positions)

    for load_position in load_positions:
        # shift positions of loads
        new_loads = [[param for param in load] for load in loads]
        for load in new_loads:
            if load[0] == "point" or load[0] == "distributed":
                load[1] += load_position

        # calculate bending moment and shear force expressions
        shear_force_expr, critical_lengths = get_shear_force_func(new_loads)
        bending_moment_expr = sy.integrate(shear_force_expr)

        shear_force_func = sy.lambdify(x, shear_force_expr)
        bending_moment_func = sy.lambdify(x, bending_moment_expr)

        shear_forces = shear_force_func(x_vals)
        bending_moments = bending_moment_func(x_vals)

        # Compare bending moment and shear forces and find maximum values
        for i in range(len(x_vals)):
            if abs(shear_forces[i]) > abs(shear_force_envelop[i]):
                shear_force_envelop[i] = shear_forces[i]
            if bending_moments[i] > bending_moment_envelop[i]:
                bending_moment_envelop[i] = bending_moments[i]

        max_shear_force = max(
            max_expression(critical_lengths, abs(shear_force_expr))[1], max_shear_force
        )
        max_bending_moment = max(
            max_expression(critical_lengths, bending_moment_expr)[1], max_bending_moment
        )

    return (
        x_vals,
        shear_force_envelop,
        bending_moment_envelop,
        {"x": list(map(str,x_vals)), "shear_force_envelope": list(map(str,shear_force_envelop)), "bending_moment_envelope":list(map(str,bending_moment_envelop)), "shear": str(max_shear_force), "moment": str(max_bending_moment)},
    )


def thin_plate_buckling(k, t, b):
    return (
        k
        * (np.pi**2)
        * matboard_youngs_modulus
        / (12 * (1 - matboard_poissons_ratio**2))
        * (t / b) ** 2
    )


def thin_plate_buckling_shear(t, h, a):
    return (
        5
        * (np.pi**2)
        * matboard_youngs_modulus
        / (12 * (1 - matboard_poissons_ratio**2))
        * ((t / h) ** 2 + (t / a) ** 2)
    )