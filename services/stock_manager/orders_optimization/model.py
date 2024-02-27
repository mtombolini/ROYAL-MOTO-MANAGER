import numpy as np
from pyomo.environ import (
    ConcreteModel, Var, Objective, Constraint, NonNegativeIntegers, maximize, RangeSet, Param, sum_product, Binary,
    NonNegativeIntegers, SolverFactory, value, SolverManagerFactory
)
from services.stock_manager.parameters_service import DAYS_TO_LAST, OBJECTIVE_COEFFICIENTS
from services.stock_manager.data_extractor import data_extractor
from services.stock_manager.distribution_estimator import get_sales_current_distribution
from typing import Dict, Tuple
from random import expovariate, randint
import time

class Optimizer:
    
    def __init__(self, kardexs: Dict[int, Dict]) -> None:
        self.opt_prob = SolverFactory('bonmin', solver_io='minlp')
        self.solver_manager = SolverManagerFactory('neos')
        self.start = time.time()
        self.model = ConcreteModel()
        
        self.products_data: Dict[int, Dict] = kardexs
        
        self.L = len(self.products_data)  # Number of suppliers
        self.M = [len(supplier) for supplier in self.products_data.values()] # Number of products per supplier
        self.T = 90  # Planning horizon
        self.BIG_M = 10**50  # Large constant
        
        # Initialize parameters and sets
        self.model.L = RangeSet(1, self.L)
        self.model.T = RangeSet(1, self.T)
        self.model.M = RangeSet(1, max(self.M))
        self.model.DELTA_T = RangeSet(1, DAYS_TO_LAST)
        
        self.model.sales = Param(self.model.L, self.model.M, self.model.T, initialize=0, within=NonNegativeIntegers, mutable=True)
        self.model.costs = Param(self.model.L, self.model.M, initialize=0, within=NonNegativeIntegers, mutable=True)
        self.model.prices = Param(self.model.L, self.model.M, initialize=0, within=NonNegativeIntegers, mutable=True)
        self.model.initial_stocks = Param(self.model.L, self.model.M, initialize=0, within=NonNegativeIntegers, mutable=True)
        self.model.emergency_stock = Param(self.model.L, self.model.M, initialize=0, within=NonNegativeIntegers, mutable=True)
        self.model.last_order = Param(self.model.L, self.model.M, initialize=0, within=NonNegativeIntegers, mutable=True)
        self.model.packing_factor = Param(self.model.L, self.model.M, initialize=1, within=NonNegativeIntegers, mutable=True)

        # For single-dimensional parameters like credit_terms and delivery_periods, which depend only on the supplier
        self.model.credit_terms = Param(self.model.L, initialize=30, within=NonNegativeIntegers, mutable=True)
        self.model.delivery_periods = Param(self.model.L, initialize=0, within=NonNegativeIntegers, mutable=True)
        
        self.supplier_id_to_index: Dict[int, int] = {}
        self.product_id_to_index: Dict[int, Tuple[int]] = {}
        self.init_end = time.time()
        print(self.init_end - self.start)


    def preprocess(self):
        i = 1
        for supplier_id, supplier_products in self.products_data.items():
            self.model.delivery_periods[i] = list(supplier_products.values())[0]['supplier']['delivery_period']
            
            j = 1
            self.supplier_id_to_index[supplier_id] = i
            for product_id, product_data in supplier_products.items():
                self.product_id_to_index[product_id] = (i, j)
                self.generate_future_sales_data(product_data, i, j)
                self.model.costs[i, j] = int(product_data['last_net_cost']['costo_neto']) if product_data['last_net_cost']['costo_neto'] else 1
                self.model.prices[i, j] = int(product_data['price_list'][0]['valor']) if product_data['price_list'][0]['valor'] else 1
                self.model.initial_stocks[i, j] = max(int(product_data['df_kardex'].iloc[-1]['stock_actual']), 0)
                self.model.emergency_stock[i, j] = 10
                self.model.packing_factor[i, j] = 1
                j += 1
            i += 1
        self.preprocess_end = time.time()
        print(self.preprocess_end - self.start)
        print(self.product_id_to_index)
            
    
    def setup_variables(self):
        # Define variables like w, v, x, stock using self.model.addVariable
        self.model.w = Var(self.model.L, self.model.T, within=Binary) # Do we place an order for supplier i at day t?
        self.model.v = Var(((l, m, t) for l in self.model.L for m in self.model.M for t in self.model.T), within=Binary) # Do we place an order for product j of supplier i at day t?
        self.model.x = Var(((l, m, t) for l in self.model.L for m in self.model.M for t in self.model.T), within=NonNegativeIntegers) # How many units of product j of supplier i do we order at day t?
        self.model.stock = Var(((l, m, t) for l in self.model.L for m in self.model.M for t in self.model.T), within=NonNegativeIntegers) # How much stock is left of product j of supplier i at day t?
        self.setup_variables_end = time.time()
        print(self.setup_variables_end - self.start)


    def setup_constraints(self):
        # Add constraints to the model

                # self.model += 0 <= self.w[i, t] <= 1 # w is binary

                    # self.model += self.v[i, j, t] == 0 # the 2nd dimension of v is the size of the maximum amount of products for all suppliers. For suppliers with less products, the remaining spaces must be 0s.
                    
                # self.model += self.stock[i, j, 0] == self.initial_stocks[i, j] # Set stock for day 0 to corresponding initial_stock value for each product.
                    # self.model += 0 <= self.v[i, j, t] <= 1 # v is binary
                    # self.model += self.v[i, j, t] <= self.w[i, t] # if w is 0, v is 0 => We don't place an order for a product if we don't place one for its supplier.
                    # self.model += self.v[i, j, t] <= self.x[i, j, t] <= self.BIG_M * self.v[i, j, t] # if v is 0, x is 0; and if v is 1, x is 1+ => We order 0 units of a product if we don't place an order for that product. Else, we order at least a unit.

                #for t in range(self.T-self.delivery_periods[1]):
                    # self.model += self.stock[i, j, t+self.delivery_periods[i]] == self.stock[i, j, t+self.delivery_periods[i]-1] + self.x[i, j, t] # Orders result in an increase in stock with a delay corresponding to the delivery period of the supplier.
                        # self.model += self.stock[i, j, t+delta_t] >= self.emergency_stock[i, j] - (1 - self.v[i, j, t]) * self.BIG_M # Stock can't run out for DAYS_TO_LAST after an order for it is placed.

                    # self.model += self.v[i, j, t] <= sum([self.sales[i, j, t+time_since_sale] for time_since_sale in range(self.last_order[i, j])]) # New orders for a product won't be placed before at least one sale.


        def w_bounds_rule(model, i, t):
            return (0, model.w[i, t], 1)  # w is binary
        self.model.w_bounds = Constraint(self.model.L, self.model.T, rule=w_bounds_rule)
        
        def v_bounds_rule(model, i, j, t):
            return (0, model.v[i, j, t], 1)  # v is binary
        self.model.v_bounds = Constraint(self.model.L, self.model.M, self.model.T, rule=v_bounds_rule)
        
        def v_zero_rule(model, i, j, t):
            # Ensures v is zero for non-existent products within the max(M) range
            if j < self.M[i-1] + 1:
                return Constraint.Skip
            return model.v[i, j, t] == 0
        self.model.v_zero_con = Constraint(self.model.L, self.model.M, self.model.T, rule=v_zero_rule)

        def wv_relation_rule(model, i, j, t):
            # Ensures x is bounded by v, and indirectly by w
            if j < self.M[i-1] + 1:  # Only apply if product j exists for supplier i
                return model.v[i, j, t] <= model.w[i, t]
            else:
                return Constraint.Skip
        self.model.wv_relation_con = Constraint(self.model.L, self.model.M, self.model.T, rule=wv_relation_rule)
        
        def vx_relation_lower_bound_rule(model, i, j, t):
            # Ensures x is bounded by v, and indirectly by w
            if j < self.M[i-1] + 1:  # Only apply if product j exists for supplier i
                return model.v[i, j, t] <= model.x[i, j, t]
            else:
                return Constraint.Skip
        self.model.vx_relation_lower_con = Constraint(self.model.L, self.model.M, self.model.T, rule=vx_relation_lower_bound_rule)
        
        def vx_relation_upper_bound_rule(model, i, j, t):
            # Ensures x is bounded by v, and indirectly by w
            if j < self.M[i-1] + 1:  # Only apply if product j exists for supplier i
                return model.x[i, j, t] <= self.BIG_M * model.v[i, j, t]
            else:
                return Constraint.Skip
        self.model.vx_relation_upper_con = Constraint(self.model.L, self.model.M, self.model.T, rule=vx_relation_upper_bound_rule)
        
        def initial_stock_rule(model, i, j):
            if j < self.M[i-1] + 1:  # Ensure j is within the range of products defined by max(M)
                return model.stock[i, j, 1] == model.initial_stocks[i, j]  # Initial stock levels
            else:
                return Constraint.Skip  # Skip if j is out of bounds   
        self.model.initial_stock_con = Constraint(self.model.L, self.model.M, rule=initial_stock_rule)
        
        def stock_update_rule(model, i, j, t):
            # Stock update considering delivery periods; assumes delivery_periods and sales are defined
            if t >= model.delivery_periods[i].value + 1 and t >= 2 and j < self.M[i-1] + 1:  # Skip t=0 (initial condition handled separately) and ensure j is valid
                return model.stock[i, j, t] == model.stock[i, j, t-1] + model.x[i, j, t-value(model.delivery_periods[i])] - model.sales[i, j, t]
            else:
                return Constraint.Skip
        self.model.stock_update_con = Constraint(self.model.L, self.model.M, self.model.T, rule=stock_update_rule)

        def emergency_stock_rule(model, i, j, t):
            # Maintaining emergency stock levels
            if j < self.M[i-1] + 1:  # Ensure j is within the valid range
                return model.stock[i, j, t] >= model.emergency_stock[i, j]
            else:
                return Constraint.Skip
        self.model.emergency_stock_con = Constraint(self.model.L, self.model.M, self.model.T, rule=emergency_stock_rule)
        
        def stock_duration_rule(model, i, j, t, delta_t):
            # Stock can't run out for DAYS_TO_LAST after an order for it is placed.
            if j < self.M[i-1] + 1 and t + delta_t < self.T + 1:
                return model.stock[i, j, t+delta_t] >= value(model.emergency_stock[i, j]) - (1 - model.v[i, j, t]) * self.BIG_M
            else:
                return Constraint.Skip
        self.model.stock_duration_con = Constraint(self.model.L, self.model.M, self.model.T, self.model.DELTA_T, rule=stock_duration_rule)
        
        self.setup_constants_end = time.time()
        print(self.setup_constants_end - self.start)


    def define_objective_function(self):
        # Objective function
        C, D, E = OBJECTIVE_COEFFICIENTS
        def objective_rule(model):
            oversupplying_penalty = sum(model.x[i, j, t] - model.sales[i, j, t]
                                        for i in model.L for j in model.M for t in model.T)  # Ensure j is within valid range for supplier i
            supplier_orders_alignment = sum(model.w[i, t] * sum(model.v[i, j, t]**2 for j in model.M)
                                            for i in model.L for t in model.T)
            utilities = sum(model.x[i, j, t] * (model.prices[i, j] - model.costs[i, j])
                            for i in model.L for j in model.M for t in model.T)  # Ensure j is within valid range for supplier i
            
            return C * utilities + D * supplier_orders_alignment - E * oversupplying_penalty
        self.model.objective = Objective(rule=objective_rule, sense=maximize)
        
        self.define_objective_function_end = time.time()
        print(self.define_objective_function_end - self.start)


    def optimize(self):
        # Solve the model
        result = self.solver_manager.solve(self.model, keepfiles=True, tee=True, opt=self.opt_prob)

        # Check solver status
        if (result.solver.status == 'ok') and (result.solver.termination_condition == 'optimal'):
            print("Solution is optimal!")
        elif result.solver.termination_condition == 'infeasible':
            print("No feasible solution found!")
        else:
            print("Solver Status:", result.solver.status)

        # Optionally, print the values of decision variables
        for v in self.model.component_objects(Var, active=True):
            print("Variable",v)
            varobject = getattr(self.model, str(v))
            for index in varobject:
                print(" ", index, varobject[index].value)
        
        self.optimization_end = time.time()        
        print(self.optimization_end - self.start)
    
    
    def generate_future_sales_data(self, product_data: Dict, i: int, j: int) -> None:
        mean, std, historic_mean, historic_std, lower_bound_ci, upper_bound_ci, days_considered = (
            get_sales_current_distribution(data_extractor(product_data['df_kardex']))
        )
        print(product_data['variant_id'], historic_mean, historic_std)
        for t in self.model.T:
            if std != 0:
                self.model.sales[i, j, t] = int(expovariate(std**(-1/2)))
            else:
                if days_considered > 1:
                    self.model.sales[i, j, t] = int(expovariate(historic_std**(-1/2)))
                else:
                    self.model.sales[i, j, t] = randint(0, 1)
                
                
    def run(self):
        self.preprocess()
        self.setup_variables()
        self.setup_constraints()
        self.define_objective_function()
        self.optimize()
