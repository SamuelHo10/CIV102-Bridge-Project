import numpy as np
import matplotlib.pyplot as plt
import sympy as sy


def plot_bridge(nodes, x_bounds=None, y_bounds=None, margin=5):
    nodes_x = [n.x for n in nodes]
    nodes_y = [n.y for n in nodes]
    plt.plot(nodes_x, nodes_y, "o")

    ax = plt.gca()
    ax.set_aspect("equal", adjustable="box")
    if x_bounds != None:
        plt.xlim([x_bounds[0] - margin, x_bounds[1] + margin])
    if y_bounds != None:
        plt.ylim([y_bounds[0] - margin, y_bounds[1] + margin])
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
):
    x_axis = np.linspace(interval[0], interval[1], spacing)
    y_axis = sy.lambdify(symbol, sympy_expr)(x_axis)
    (line,) = plt.plot(x_axis, y_axis)
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    ax = plt.gca()
    ax.set_xlim(left=interval[0], right=interval[1])
    if invert_y:
        ax.invert_yaxis()
    if fill:
        ax.fill_between(x_axis, y_axis, facecolor=line.get_color())
    plt.savefig(save_path)
    if show:
        plt.show()
    else:
        plt.clf()
