class SupplyChainEnv:
    
    def __init__(self, suppliers, products, initial_stock, demand):
        # Initialize parameters
        self.suppliers = suppliers  # List of suppliers
        self.products = products  # List of products
        self.stock = initial_stock  # Dictionary mapping products to initial stock levels
        self.demand = demand  # Simulated demand over time for each product
    
    def reset(self):
        # Reset the environment to the initial state
        self.stock = self.initial_stock.copy()
        # Return initial state
    
    def step(self, action):
        # Apply an action (ordering decision), update the environment state, and return feedback
        # Action is a dict mapping products to order quantities
        # Update stock levels based on action and demand
        # Calculate reward based on costs, sales, and stockouts
        # Return new state, reward, and done flag (True if the planning horizon is reached)
        pass
