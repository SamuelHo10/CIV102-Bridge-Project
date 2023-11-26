import numpy as np
import matplotlib.pyplot as plt
import sympy as sy

color_wheel = plt.rcParams["axes.prop_cycle"].by_key()["color"]


def plot_expr(
    expr,
    symbol,
    interval = (0,1.2),
    x_axis_label="x",
    y_axis_label="y",
    invert_y=False,
    save_path="graph.png",
    spacing=1000,
    fill=False,
    show=True,
    multiple_graphs=False,
    color_1=color_wheel[0],
    color_2=color_wheel[1],
    labels = None
):
    if multiple_graphs:
        for i in range(len(expr)):
            plt.plot(symbol, expr[i], color=(color_1 if i == 0 else color_2),label=labels[i])
    else:
        if type(expr) == np.ndarray:
            y_axis = expr
            x_axis = symbol
        else:
            x_axis = np.linspace(interval[0], interval[1], spacing)
            y_axis = sy.lambdify(symbol, expr)(x_axis)
        plt.plot(x_axis, y_axis, color=color_1)
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    if labels != None:
        plt.legend(loc="upper right")
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
