from gurobipy import Model, GRB, quicksum
# Example data
C = 30000  # Total consulting payment
D = 7000   # Initial credit card debt
r1 = 0.1595 / 12  # Monthly APR of Card 1
r2 = 0.029 / 12   # Monthly APR of Card 2
r3 = 0.002        # Transfer fee rate
B = 70000     # Annual base salary
alpha = 80000     # Tax threshold parameter

# Create a new model
model = Model("Personal Finance Optimization")

# OPTIGUIDE DATA CODE GOES HERE

# Create variables
P1 = model.addVars(6, name="P1")        # Payments towards credit card 1
P2 = model.addVars(6, name="P2")        # Payments towards credit card 2
T = model.addVars(6, name="T")        # Debt transfer amounts
S = model.addVars(6, name="S")        # Consulting payments
# First fiscal year
d1_1 = model.addVar(name="d1_1")  # Portion of income taxed at 10% in the first year
d2_1 = model.addVar(name="d2_1")  # Portion of income taxed at 28% in the first year
# Second fiscal year
d1_2 = model.addVar(name="d1_2")  # Portion of income taxed at 10% in the second year
d2_2 = model.addVar(name="d2_2")  # Portion of income taxed at 28% in the second year
binary_var = model.addVar(vtype=GRB.BINARY, name="binary_var")  # Auxiliary binary variable
M = 10000000  # A large number, should be larger than any expected value of income
balance1 = model.addVars(6, name="balance1")  # Outstanding balance on Card 1
balance2 = model.addVars(6, name="balance2")  # Outstanding balance on Card 2

# Set objective
total_tax = 0.1 * d1_1 + 0.28 * d2_1 + 0.1 * d1_2 + 0.28 * d2_2
wealth = B*2 + quicksum(S[t] - P1[t] - P2[t] for t in range(6)) - total_tax
model.setObjective(wealth, GRB.MAXIMIZE)

# Consulting Payment Constraints
model.addConstr(quicksum(S[t] for t in range(6)) == C)

# Monthly Consulting Payment Constraints
for t in range(6):
    model.addConstr(S[t] <= (4/3) * (C/6))

#Credit Card Payment constraint: Don't use more money than you have to pay. Pay off all balance at the end
[model.addConstr(P1[t] + P2[t] - (S[t]+quicksum([S[i]-P1[i]-P2[i] for i in range(t)])) <= 0) for t in range(6)]
model.addConstr(balance1[5]<= 0)
model.addConstr(balance2[5]<= 0)

# Transfer Constraint
for t in range(6):
    model.addConstr(T[t] <= D - quicksum(P1[k] for k in range(t)))


# Balance Dynamics for Card 1 and Card 2
for t in range(6):
    if t == 0:
        model.addConstr(balance1[t] == (D - P1[t] - T[t]) * (1 + r1) )
        model.addConstr(balance2[t] == T[t] * (1 + r2))
    else:
        model.addConstr(balance1[t] == (balance1[t-1] - P1[t] - T[t]) * (1 + r1))
        model.addConstr(balance2[t] == (balance2[t-1] - P2[t] + T[t] * (1 - r3)) * (1 + r2) )

# Tax Calculation
# Constraints for the first fiscal year
G1 = B + quicksum(S[t] for t in range(3))
G2 = B + quicksum(S[t] for t in range(3, 6))

model.addConstr(d1_1 <= G1)
model.addConstr(d1_1 <= alpha)
model.addConstr(d1_1 >= G1 - M*(1 - binary_var))
model.addConstr(d1_1 >= alpha - M*binary_var)
model.addConstr(d2_1 == G1 - d1_1)

# Constraints for the second fiscal year
model.addConstr(d1_2 <= G2)
model.addConstr(d1_2 <= alpha)
model.addConstr(d1_2 >= G2 - M*(1 - binary_var))
model.addConstr(d1_2 >= alpha - M*binary_var)
model.addConstr(d2_2 == G2 - d1_2)

# Optimize model
model.optimize()
m = model

# OPTIGUIDE CONSTRAINT CODE GOES HERE

# Solve
m.update()
model.optimize()

# Print Solution
if model.status == GRB.OPTIMAL:
    print("Optimal Wealth:", model.objVal)
    for t in range(6):
        print(f"Month {t+1}: Payment {round(P1[t].x, 2)}, Payment2 {round(P2[t].x, 2)} Transfer {round(T[t].x,2)}, Salary {round(S[t].x,2)}, Balance1 {round(balance1[t].x,2)}, Balance2 {round(balance2[t].x,2)}")

if m.status == GRB.OPTIMAL:
    print(f'Optimal cost: {m.objVal}')
else:
    print("Not solved to optimality. Optimization status:", m.status)
