import numpy as np
from stock_manager.parameters_service import DAYS_OF_ANTICIPATION, DAYS_TO_LAST
from cylp.cy import CyClpSimplex
from cylp.py.modeling.CyLPModel import CyLPModel, CyLPArray, CyLPConstraint
import random

# Model
model = CyLPModel()

# Dimensions and indices
L = 10 # i in {0, ..., L}
M = [random.randint(1, 6) for _ in range(L)] # j in {0, ..., M(i)}
N = 90 # t in {0, ..., N}

BIG_M = 10**50

# Variables
w = model.addVariable('w', (L, N), isInt=True) # Do we place an order for supplier i at day t?
v = model.addVariable('v', (L, max(M), N), isInt=True) # Do we place an order for product j of supplier i at day t?
x = model.addVariable('x', (L, max(M), N), isInt=True) # How many units of product j of supplier i do we order at day t?

stock = model.addVariable('stock', (L, max(M), N), isInt=True) # How much stock is left of product j of supplier i at day t?

# Constants
# TODO: INTEGRATE CONSTANTS WITH APPLICATION DATABASE.
sales = np.matrix() # INTEGRATE WITH DATABASE. DIMS = (L, max(M), N)
prices = np.matrix() # INTEGRATE WITH DATABASE. DIMS = (L, max(M))
initial_stocks = np.matrix([]) # INTEGRATE WITH DATABASE. DIMS = (L, max(M))
emergency_stock = np.matrix([]) # INTEGRATE WITH DATABASE. DIMS = (L, max(M))
last_order = np.matrix([]) # INTEGRATE WITH DATABASE. DIMS = (L, max(M))
packing_factor = np.matrix([]) # INTEGRATE WITH DATABASE, DIMS(L, max(M))
credit_terms = CyLPArray() # INTEGRATE WITH DATABASE. DIMS = (1, L)
delivery_periods = CyLPArray() # INTEGRATE WITH DATABASE. DIMS (1, L)

# Constraints
for i in range(L):
    for t in range(N):
        model += 0 <= w[i, t] <= 1 # w is binary

for i in range(L):
    for j in range(M[i], max(M) - 1):
        for t in range(N):
            model += v[i, j, t] == 0 # the 2nd dimension of v is the size of the maximum amount of products for all suppliers. For suppliers with less products, the remaining spaces must be 0s.
            
for i in range(L):
    for j in range(M[i]):
        model += stock[i, j, 0] == initial_stocks[i, j] # Set stock for day 0 to corresponding initial_stock value for each product.
        for t in range(N):
            model += 0 <= v[i, j, t] <= 1 # v is binary
            model += v[i, j, t] <= w[i, t] # if w is 0, v is 0 => We don't place an order for a product if we don't place one for its supplier.
            model += v[i, j, t] <= x[i, j, t] <= BIG_M * v[i, j, t] # if v is 0, x is 0; and if v is 1, x is 1+ => We order 0 units of a product if we don't place an order for that product. Else, we order at least a unit.

for i in range(L):
    for j in range(M[i]):
        for t in range(N-delivery_periods[1]):
            model += stock[i, j, t+delivery_periods[i]] == stock[i, j, t+delivery_periods[i]-1] + x[i, j, t] # Orders result in an increase in stock with a delay corresponding to the delivery period of the supplier.

for i in range(L):
    for j in range(M[i]):
        for t in range(N):
            for delta_t in range(DAYS_TO_LAST):
                model += stock[i, j, t+delta_t] >= 1 - (1 - v[i, j, t]) * BIG_M # Stock can't run out for DAYS_TO_LAST after an order for it is placed.

for i in range(L):
    for j in range(M[i]):
        for t in range(N):
            model += v[i, j, t] <= sum([sales[i, j, t+time_since_sale] for time_since_sale in range(last_order[i, j])]) # New orders for a product won't be placed before at least one sale.
            
            
# TODO: PURCHASES SHOULD BE JUST BIG ENOUGH TO FIT THE DEMAND.
# TODO: ORDERS SHOULD BE TIMED SO THAT THE AMOUNT OF DELIVERIES FROM EACH SUPPLIER IS MINIMIZED.
            
# Objective function
oversupplying_penalty = sum([sum([sum([x[i, j, t] - sales[i, j, t] for t in range(N)]) for j in range(M[i])]) for i in range(L)])
supplier_orders_alignment = sum([sum([w[i, t] * sum(v[i, j, t]**2 for j in range(M[i])) for t in range(N)]) for i in range(L)])


#model.objective = 
