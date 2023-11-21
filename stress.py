import json
from calculate import *
from graphs import *


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
data = generate_envelop(-0.172, 0.172, 50, loads, 1000)


plot_sympy(
    data[1],
    data[0],
    (0, 1.2),
    x_axis_label="Length (m)",
    y_axis_label="Shear Force (N)",
    save_path="img\\SFD_envelop.png",
    show=False,
    multiple_graphs=True
)

plot_sympy(
    data[2],
    data[0],
    (0, 1.2),
    x_axis_label="Length (m)",
    y_axis_label="Bending Moment (Nm)",
    save_path="img\\BMD_envelop.png",
    show=False,
    invert_y = True,
    multiple_graphs=True
)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data[3], f, ensure_ascii=False, indent=4)