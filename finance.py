from gurobipy import Model, GRB, quicksum

# Initialize Model
model = Model("Personal Finance Optimization")

# Parameters
C = 30000  # Total consulting payment
D = 7000   # Initial credit card debt
r1 = 0.1595  # APR of Card 1
r2 = 0.029   # APR of Card 2
r3 = 0.002   # Transfer fee rate
B = 70000  # Annual base salary
alpha = 80000  # Tax threshold parameter

# OPTIGUIDE DATA CODE GOES HERE

# Decision Variables for 6 months (3 months each in two years)
P = model.addVars(6, name="P")  # Payments towards credit card
T = model.addVars(6, name="T")  # Debt transfer amounts
S = model.addVars(6, name="S")  # Consulting payments
d1 = model.addVar(name="d1")    # Auxiliary variable for tax calculation in Year 1
d2 = model.addVar(name="d2")    # Auxiliary variable for tax calculation in Year 2

# Objective Function
wealth = quicksum(S[t] - P[t] for t in range(6)) - (0.1 * d1 + 0.28 * d2)
model.setObjective(wealth, GRB.MAXIMIZE)

# Constraints
# Total consulting payment distribution
model.addConstr(quicksum(S[t] for t in range(6)) == C)

# Monthly consulting payment limit
for t in range(6):
    model.addConstr(S[t] <= (4/3) * (C/6))

# Credit Card Payment
model.addConstr(D - quicksum(P[t] for t in range(6)) == 0)

# Transfer Limits
for t in range(6):
    model.addConstr(T[t] <= D - quicksum(P[k] for k in range(t)))

# Tax Calculation
# Year 1 (Last 3 months)
model.addConstr(d1 >= quicksum(S[t] for t in range(3)) + B/4 - alpha)
model.addConstr(d1 >= 0)
# Year 2 (First 3 months)
model.addConstr(d2 >= quicksum(S[t] for t in range(3, 6)) + B/4 - alpha)
model.addConstr(d2 >= 0)

# Solve
model.optimize()
# OPTIGUIDE CONSTRAINT CODE GOES HERE

# Print Solution
if model.status == GRB.OPTIMAL:
    print("Optimal Wealth:", model.objVal)
    for t in range(6):
        print(f"Month {t+1}: Payment {P[t].x}, Transfer {T[t].x}, Salary {S[t].x}")
