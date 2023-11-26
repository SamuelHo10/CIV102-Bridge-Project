import json
from calculate import *
from graphs import *

### Load Case 2 ###

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

plot_expr(
    data[1],
    data[0],
    x_axis_label="Length (m)",
    y_axis_label="Shear Force (N)",
    save_path="img\\load_case_2\\SFD_envelop.png",
    show=False,
    fill = True
)

plot_expr(
    data[2],
    data[0],
    x_axis_label="Length (m)",
    y_axis_label="Bending Moment (Nm)",
    save_path="img\\load_case_2\\BMD_envelop.png",
    show=False,
    invert_y = True,
    fill = True
)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data[3], f, ensure_ascii=False, indent=4)

### Load Case 1 ###

loads2 = [
    ["reaction", 0],
    ["point", 0.172, 200 / 3],
    ["point", 0.348, 200 / 3],
    ["point", 0.512, 200 / 3],
    ["point", 0.688, 200 / 3],
    ["point", 0.852, 200 / 3],
    ["point", 1.028, 200 / 3],
    ["reaction", 1.200],
]

data2 = generate_envelop(-0.172, 0.172, 50, loads2, 1000)

plot_expr(
    data2[1],
    data2[0],
    x_axis_label="Length (m)",
    y_axis_label="Shear Force (N)",
    save_path="img\\load_case_1\\SFD_envelop.png",
    show=False,
    fill = True
)

plot_expr(
    data2[2],
    data2[0],
    x_axis_label="Length (m)",
    y_axis_label="Bending Moment (Nm)",
    save_path="img\\load_case_1\\BMD_envelop.png",
    show=False,
    invert_y = True,
    fill = True
)

with open('data2.json', 'w', encoding='utf-8') as f:
    json.dump(data2[3], f, ensure_ascii=False, indent=4)

