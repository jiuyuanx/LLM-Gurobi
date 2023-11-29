from gurobipy import Model, GRB, quicksum
# Parameters
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

# Decision Variables for 6 months (3 months each in two years)
P1 = model.addVars(6, name="P1")        # Payments towards credit card 1
P2 = model.addVars(6, name="P2")        # Payments towards credit card 2
T = model.addVars(6, name="T")        # Debt transfer amounts
S = model.addVars(6, name="S")        # Consulting payments
d1 = model.addVar(name="d1")          # Auxiliary variable for tax calculation in Year 1
d2 = model.addVar(name="d2")          # Auxiliary variable for tax calculation in Year 2
balance1 = model.addVars(6, name="balance1")  # Outstanding balance on Card 1
balance2 = model.addVars(6, name="balance2")  # Outstanding balance on Card 2

# Objective Function
wealth = quicksum(S[t] - P1[t] - P2[t]  for t in range(6)) - (0.1 * d1 + 0.28 * d2)
model.setObjective(wealth, GRB.MAXIMIZE)

# Constraints
# Total consulting payment distribution
model.addConstr(quicksum(S[t] for t in range(6)) == C)

# Monthly consulting payment limit
for t in range(6):
    model.addConstr(S[t] <= (4/3) * (C/6))

# Credit Card Payment
# model.addConstr(D - quicksum(P[t] for t in range(6)) == 0)


#Pay constraint: Don't use more money than you have to pay. Pay off all balance at the end
#quicksum to find money in hand in the last period 
[model.addConstr(P1[t] + P2[t] - (S[t]+quicksum([S[i]-P1[i]-P2[i] for i in range(t)])) <= 0) for t in range(6)]
model.addConstr(balance1[5]<= 0)
model.addConstr(balance2[5]<= 0)

# Transfer Limits
for t in range(6):
    model.addConstr(T[t] <= D - quicksum(P1[k] for k in range(t)))


# at the beginning of each month, you are paid the chosen amount, and immediately you decide how much of each credit
# card to pay off, and transfer any debt from card 1 to card 2. Any
# outstanding debt accumulates interest at the end of the current
# month.


# Balance Dynamics for Card 1 and Card 2
for t in range(6):
    if t == 0:
        model.addConstr(balance1[t] == (D - P1[t] - T[t]) * (1 + r1) )
        model.addConstr(balance2[t] == T[t] * (1 + r2))
    else:
        model.addConstr(balance1[t] == (balance1[t-1] - P1[t] - T[t]) * (1 + r1))
        model.addConstr(balance2[t] == (balance2[t-1] - P2[t] + T[t]*(1-r3)) * (1 + r2) )

# Tax Calculation
# Year 1 (Last 3 months)
model.addConstr(d1 >= quicksum(S[t] for t in range(3)) + B - alpha)
model.addConstr(d1 >= 0)
# Year 2 (First 3 months)
model.addConstr(d2 >= quicksum(S[t] for t in range(3, 6)) + B - alpha)
model.addConstr(d2 >= 0)

# Solve
model.optimize()
# OPTIGUIDE CONSTRAINT CODE GOES HERE

# Print Solution
if model.status == GRB.OPTIMAL:
    print("Optimal Wealth:", model.objVal)
    for t in range(6):
        print(f"Month {t+1}: Payment {round(P1[t].x, 2)}, Payment2 {round(P2[t].x, 2)} Transfer {round(T[t].x,2)}, Salary {round(S[t].x,2)}, Balance1 {round(balance1[t].x,2)}, Balance2 {round(balance2[t].x,2)}")
