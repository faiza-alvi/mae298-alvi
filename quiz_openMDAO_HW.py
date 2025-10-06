# Quiz: OpenMDAO Hello World 
# Code from OpenMDAO Tutorial
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-50, 50, 100)
y = np.linspace(-50, 50, 100)
XX, YY = np.meshgrid(x, y)
ZZ = (XX - 3)**2 + XX * YY + (YY + 4)**2 - 3

# Figure: Shows the contours of the parabloid
# plt.figure(figsize=(8, 6))
# plt.contour(XX, YY, ZZ, levels=np.linspace(np.min(ZZ), np.max(ZZ), 50))
# plt.xlabel('x')
# plt.ylabel('y')
# plt.colorbar(label='f')
# plt.suptitle('Contour of the paraboloid', fontsize=18)
# plt.show()

import openmdao.api as om

# build the model
prob = om.Problem()

prob.model.add_subsystem('paraboloid', om.ExecComp('f = (x-4)**2 + x*y + (y+3)**2 - 3'))

# setup the optimization
prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'Nelder-Mead'

prob.model.add_design_var('paraboloid.x', lower=-50, upper=50)
prob.model.add_design_var('paraboloid.y', lower=-50, upper=50)
prob.model.add_objective('paraboloid.f')

prob.setup()

# Set initial values.
prob.set_val('paraboloid.x', 3.0)
prob.set_val('paraboloid.y', -4.0)

# run the optimization
prob.run_driver()


# Prints the optimal values
print('Optimal x value: ', prob.get_val('paraboloid.x'))
print('Optimal y value: ', prob.get_val('paraboloid.y'))
print('Objective value: ', prob.get_val('paraboloid.f'))