from spb import plot_piecewise
import sympy as sy
import numpy as np
import sympy.plotting as plt 

x = sy.Symbol("x", real=True)
n = x**2 + 1
f = sy.Piecewise(*[(n +x-10.000000666 , x >= 1), (n ,  x > -5)])
x_array = np.linspace(-5, 5, 1000)
f_array = sy.lambdify(x, f)(x_array)
print(f) # fill ={"x": x_array, "y1": f_array,'color': 'green'}
plt.plot( f)
