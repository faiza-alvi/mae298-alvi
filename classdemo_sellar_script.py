import openmdao.api as om
import classdemo_sellar_components as dsc

# Set up the problem
prob = om.Problem()
prob.model = dsc.SellarMDAConnect()

# Does the setup 
prob.setup()

# Can set independent variables, be careful you keep same types
prob.set_val('indvar.x', val=2.0)
prob.set_val('indvar.z', val=[-1.0, -1.0])

# Run the model
prob.run_model()

print(f"y1 = {prob.get_val('cycle.d1.y1')} and y2 = {prob.get_val('cycle.d1.y2')}")
# Note: we have not run the optimizer and we do not have an optimal solution
# This has just solved the two disciplines in the cycle.
