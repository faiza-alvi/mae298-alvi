# Quiz: OpenMDAO Components use 
# 10/8/2025 
# Code based on OpenMDAO Tutorial

import openmdao.api as om


class Paraboloid(om.ExplicitComponent):
    """
    Evaluates the equation f(x,y) = (x-4)^2 + xy + (y+3)^2 - 3.
    """

    def setup(self):
        self.add_input('x', val=0.0)
        self.add_input('y', val=0.0)

        self.add_output('f_xy', val=0.0)

    def setup_partials(self):
        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        """
        f(x,y) = (x-4)^2 + xy + (y+3)^2 - 3

        Minimum at: x = 6.6667; y = -7.3333
        """
        x = inputs['x']
        y = inputs['y']

        outputs['f_xy'] = (x - 4.0)**2 + x * y + (y + 3.0)**2 - 3.0


if __name__ == "__main__":

    # Code to find value of the parabloid when x = -1 and y = 7
    model = om.Group()
    model.add_subsystem('parab_comp', Paraboloid())

    prob = om.Problem(model)
    prob.setup()

    prob.set_val('parab_comp.x', -1.0)
    prob.set_val('parab_comp.y', 7.0)

    prob.run_model()
    print("The problem value when x = -1 and y = 7 is: ")
    print(prob['parab_comp.f_xy'])

    # Code to find minimum of parabloid with constraint
    # 1 < x^2 + y < 8
    # build the model
    prob = om.Problem()
    prob.model.add_subsystem('parab', Paraboloid(), promotes_inputs=['x', 'y'])

    # define the component whose output will be constrained
    prob.model.add_subsystem('const', om.ExecComp('g = x**2 + y'), promotes_inputs=['x', 'y'])

    # Design variables 'x' and 'y' span components, so we need to provide a common initial
    # value for them.
    prob.model.set_input_defaults('x', 4.0)
    prob.model.set_input_defaults('y', -3.0)

    # setup the optimization
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'COBYLA'

    prob.model.add_design_var('x', lower=-50, upper=50)
    prob.model.add_design_var('y', lower=-50, upper=50)
    prob.model.add_objective('parab.f_xy')

    # to add the constraint to the model
    prob.model.add_constraint('const.g', lower=1.0, upper=8.0)

    prob.setup()
    prob.run_driver()
    
    # Prints the optimal values
    print('Optimal x value: ', prob.get_val('parab.x'))
    print('Optimal y value: ', prob.get_val('parab.y'))
    print('Objective value: ', prob.get_val('parab.f_xy'))



