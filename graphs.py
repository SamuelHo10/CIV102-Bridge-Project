import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections
import sympy as sy

color_wheel = plt.rcParams["axes.prop_cycle"].by_key()["color"]


def plot_bridge(
    nodes,
    members,
    x_bounds=None,
    y_bounds=None,
    margin=6,
    force_length=3,
    line_width=2,
    full_screen=False,
):
    ax = plt.gca()

    # Lines
    lines = [
        [(m.nodes[0].x, m.nodes[0].y), (m.nodes[1].x, m.nodes[1].y)] for m in members
    ]
    line_collection = collections.LineCollection(lines, linewidths=line_width)
    ax.add_collection(line_collection)

    # External Forces
    for node in nodes:
        if node.force != (0, 0):
            mag = np.sqrt(node.force[0] ** 2 + node.force[1] ** 2)
            dx = node.force[0] / mag * force_length
            dy = node.force[1] / mag * force_length
            ax.annotate(
                f"{mag}N",
                ha="center",
                va="center",
                xy=(node.x, node.y),
                xytext=(node.x + dx, node.y + dy),
                arrowprops=dict(arrowstyle="<-", lw=line_width),
            )

    # Nodes
    nodes_x = [n.x for n in nodes]
    nodes_y = [n.y for n in nodes]
    plt.plot(nodes_x, nodes_y, "o")

    # Member Forces
    for member in members:
        point = (
            (member.nodes[0].x + member.nodes[1].x) / 2,
            (member.nodes[0].y + member.nodes[1].y) / 2,
        )
        angle = (
            np.arctan2(
                (member.nodes[0].y - member.nodes[1].y),
                (member.nodes[0].x - member.nodes[1].x),
            )
            * 180
            / np.pi
        )
        if angle >= 90:
            angle -= 180
        elif angle < -90:
            angle += 180
        ax.annotate(
            f"{'{:.2f}'.format(member.force)}N",
            point,
            ha="center",
            va="center",
            rotation=angle,
            size=8,
            bbox=dict(facecolor="white", edgecolor="none", pad=line_width),
        )

    ax.set_aspect("equal", adjustable="box")
    if x_bounds != None:
        plt.xlim([x_bounds[0] - margin, x_bounds[1] + margin])
    if y_bounds != None:
        plt.ylim([y_bounds[0] - margin, y_bounds[1] + margin])
    if full_screen:
        wm = plt.get_current_fig_manager()
        wm.window.state("zoomed")
    plt.show()


def plot_sympy(
    sympy_expr,
    symbol,
    interval,
    x_axis_label="x",
    y_axis_label="y",
    invert_y=False,
    save_path="graph.png",
    spacing=1000,
    fill=False,
    show=True,
    multiple_graphs=False,
    color_1=color_wheel[0],
):
    if multiple_graphs:
        for y_data in sympy_expr:
            plt.plot(symbol, y_data, color=color_1)
    else:
        if type(sympy_expr) == np.ndarray:
            y_axis = sympy_expr
            x_axis = symbol
        else:
            x_axis = np.linspace(interval[0], interval[1], spacing)
            y_axis = sy.lambdify(symbol, sympy_expr)(x_axis)
        plt.plot(x_axis, y_axis, color=color_1)
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    ax = plt.gca()
    ax.set_xlim(left=interval[0], right=interval[1])
    if invert_y:
        ax.invert_yaxis()
    if fill:
        ax.fill_between(x_axis, y_axis, facecolor=color_1)
    plt.savefig(save_path)
    if show:
        plt.show()
    else:
        plt.clf()
