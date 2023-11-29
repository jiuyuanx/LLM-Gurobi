import gurobipy as gp
from gurobipy import GRB

# Model Parameters
C = 30000   # Total consulting payment
D = 7000    # Initial credit card debt
r1 = 0.1595 # APR of Card 1
r2 = 0.029  # APR of Card 2
r3 = 0.002  # Transfer fee rate
B = 70000   # Annual base salary
alpha = 80000 # Tax threshold parameter

# Create a new model
model = gp.Model("wealth_maximization")

# Decision Variables
P = model.addVars(2, 6, name="P", vtype=GRB.CONTINUOUS)
T = model.addVars(2, 6, name="T", vtype=GRB.CONTINUOUS)
S = model.addVars(2, 6, name="S", vtype=GRB.CONTINUOUS)
d1 = model.addVars(2, name="d1", vtype=GRB.CONTINUOUS)
d2 = model.addVars(2, name="d2", vtype=GRB.CONTINUOUS)

# Objective Function
wealth_expr = gp.quicksum(S[i,t] - P[i,t] - (0.1*d1[i] + 0.28*d2[i]) for i in range(1,3) for t in range(1,7)) - (D * (1 + r1)**12)
model.setObjective(wealth_expr, GRB.MAXIMIZE)

# Constraints
# 1. Credit Card Payment
model.addConstr(gp.quicksum(P[i,t] for i in range(1,3) for t in range(1,7)) == D)

# 2. Transfer Limits
for i in range(1, 3):
    for t in range(1, 7):
        model.addConstr(T[i,t] <= D - gp.quicksum(P[i,k] for k in range(1, t)))

# 3. Total Consulting Payment Distribution
model.addConstr(gp.quicksum(S[i,t] for i in range(1,3) for t in range(1,7)) == C)

# 4. Monthly Consulting Payment Limit
for i in range(1, 3):
    for t in range(1, 7):
        model.addConstr(S[i,t] <= (4/3) * (C/6))

# 5. Tax Calculation
for i in range(1, 3):
    G = B/4 + gp.quicksum(S[1,t] for t in range(1, 4)) if i == 1 else B/4 + gp.quicksum(S[2,t] for t in range(4, 7))
    model.addConstr(d2[i] >= G - alpha)
    model.addConstr(d2[i] >= 0)
    model.addConstr(d1[i] >= G - d2[i])
    model.addConstr(d1[i] >= d2[i] - alpha)

# 6. Gross Income Calculation is embedded in the tax constraints

# 7. Debt and Payment Dynamics
# These are handled by the Credit Card Payment and Transfer Limits constraints

# 8. Non-Negativity
# Automatically handled by decision variable definitions

# Optimize the model
model.optimize()

# Output the solution
if model.status == GRB.OPTIMAL:
    for v in model.getVars():
        print(f'{v.varName}: {v.x}')

else:
    print('No optimal solution found')
