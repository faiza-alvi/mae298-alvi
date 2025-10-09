import numpy as np
import openmdao.api as om

# Create a class for each discipline
class SellarDis1(om.ExplicitComponent): 
    """
    Discipline 1 for Sellar example
    y1 = z1**2 + z2 + x1 -0.2*y2
    """

    # Set up for the class
    def setup(self):
        # Design Variables
        self.add_input('z', val=np.zeros(2))
        self.add_input('x', val=0.0)
        # Coupling parameter
        self.add_input('y2', val=1.0)

        # Output
        self.add_output('y1', val=1.0)

        #Either do this,, or add setup partials 
        # self.declare_partials('y1', ['z', 'x', 'y2'])

    def setup_partials(self):
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs): 
        z1 = inputs['z'][0]
        z2 = inputs['z'][1]
        x = inputs['x']
        y2 = inputs['y2']

        outputs['y1'] = z1**2 + z2 + x - 0.2*y2
        

class SellarDis2(om.ExplicitComponent): 
    """
    Discipline 1 for Sellar example
    y1 = z1**2 + z2 + x1 -0.2*y2
    """

    # Set up for the class
    def setup(self):
        # Design Variables
        self.add_input('z', val=np.zeros(2))
        # Coupling parameter
        self.add_input('y1', val=1.0)

        # Output
        self.add_output('y2', val=1.0)

        #Either do this,, or add setup partials 
        # self.declare_partials('y1', ['z', 'x', 'y2'])

    def setup_partials(self):
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs): 
        z1 = inputs['z'][0]
        z2 = inputs['z'][1]
        y1 = inputs['y1']

        if y1.real < 0.0:
            y1 *= -1
            #Could be an issue but needed bc of square root. 

        outputs['y2'] = y1**0.5 + z1 + z2

# Can use groups to better understand how the components are being coupled or used together
# building something like this: 
#                       model
#       _____________________________________________________
#       cycle       obj_cmp     constraint 1      constraint2
#   ____________
#   dis1    dis2

# now telling it how to group things together
class SellarMDAConnect(om.Group): 
    
    def setup(self): 
        indvar = self.add_subsystem('indvar', om.IndepVarComp() )
        indvar.add_output('x', val=1.0)
        indvar.add_output('z', val=np.array([5.0, 2.0]))

        # Couple the cycle with a non-linear solver: 
        cycle = self.add_subsystem('cycle', om.Group())
        cycle.add_subsystem('d1', SellarDis1())
        cycle.add_subsystem('d2', SellarDis2()) #can keep name or change name locally

        #Couple the cycle components here
        cycle.connect('d1.y1', 'd2.y1')
        cycle.connect('d2.y2', 'd1.y2') #HAS TO BE OUTPUT AND THEN INPUT
        
        # now tell it how to solve. use nonlinear Gauss-Seidel
        cycle.nonlinear_solver = om.NonlinearBlockGS()

        # now add objective and constraint
        # the two disciplines still don't know anything about each other
        self.add_subsystem('obj_cmp', om.ExecComp('obj = x**2 + z[1] + y1 + exp(-1*y2)',
                           z = np.zeros(2), x = 0.0) )
        
        self.add_subsystem('con_cmp1', om.ExecComp('con1=3.16-y1'))
        self.add_subsystem('con_cmp2', om.ExecComp('con2=y2-24.0'))

        # wire this group together
        self.connect('indvar.x', ['cycle.d1.x', 'obj_cmp.x'])
        self.connect('indvar.z', ['cycle.d1.z', 'cycle.d2.z', 'obj_cmp.z'])
        self.connect('cycle.d1.y1', ['obj_cmp.y1', 'con_cmp1.y1'])
        self.connect('cycle.d2.y2', ['obj_cmp.y2', 'con_cmp2.y2'])
        # note that line 92-93 can also be put in here, with 'cycle.d2.y1' in the line 109 
        # and cycle.d1.y2 in line 110 before obj_cmp.y