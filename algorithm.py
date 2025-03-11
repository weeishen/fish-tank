import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

class FishTankEvent:
    def __init__(self, num_participants=50, rounds=4, initial_budget=20000):
        self.num_participants = num_participants
        self.rounds = rounds
        self.initial_budget = initial_budget
        
        # Define products with their initial prices
        self.products = {
            'watch': {'cost_price': 1500, 'selling_price': 2000, 'quantity_sold': 0, 'profit_margin': 33.33},
            'headphones': {'cost_price': 500, 'selling_price': 600, 'quantity_sold': 0, 'profit_margin': 20.00},
            'bottle': {'cost_price': 200, 'selling_price': 250, 'quantity_sold': 0, 'profit_margin': 25.00},
            'chocolates': {'cost_price': 100, 'selling_price': 120, 'quantity_sold': 0, 'profit_margin': 20.00}
        }
        
        # Initialize participants and their investments
        self.participants = {i: {'name': f'P{i}', 'budget': initial_budget, 'inventory': {}, 'profit': 0} 
                           for i in range(1, num_participants+1)}
        
        # Track market history
        self.market_history = []
        self.eliminated_participants = set()
        
    def update_market_prices(self):
        """Update product selling prices based on market demand"""
        # Calculate total quantity sold for each product
        total_products_sold = sum(product['quantity_sold'] for product in self.products.values())
        
        # Reset quantities for next round
        for product_name in self.products:
            # Store previous selling price for reference
            previous_price = self.products[product_name]['selling_price']
            
            # Calculate demand ratio (what percentage of total sales was this product)
            if total_products_sold > 0:
                demand_ratio = self.products[product_name]['quantity_sold'] / total_products_sold
            else:
                demand_ratio = 0.25  # Equal distribution if no sales
            
            # Adjust selling price based on demand
            # High demand (higher ratio) -> price increases
            # Low demand (lower ratio) -> price decreases
            
            # Base adjustment factor - ranging from -15% to +15%
            # 0.25 represents equal distribution (25% each for 4 products)
            price_adjustment = (demand_ratio - 0.25) * 60  # percentage points
            
            # Get the cost price
            cost = self.products[product_name]['cost_price']
            
            # Calculate new selling price with adjustment
            new_price = previous_price * (1 + price_adjustment/100)
            
            # Ensure price doesn't go below cost price + 5% minimum profit
            min_price = cost * 1.05
            # Ensure price doesn't go above cost price + 50% maximum profit
            max_price = cost * 1.5
            
            # Apply constraints
            new_price = max(min_price, min(max_price, new_price))
            
            # Round to nearest 10
            new_price = round(new_price / 10) * 10
            
            # Update selling price
            self.products[product_name]['selling_price'] = new_price
            
            # Update profit margin
            self.products[product_name]['profit_margin'] = ((new_price - cost) / cost) * 100
            
            # Reset quantity sold for next round
            self.products[product_name]['quantity_sold'] = 0
        
        # Save market state for history
        market_state = {product: {
            'selling_price': self.products[product]['selling_price'],
            'profit_margin': self.products[product]['profit_margin']
        } for product in self.products}
        
        self.market_history.append(market_state)
    
    def process_participant_investments(self, p_id):
        """Process investment decisions for a participant"""
        if p_id in self.eliminated_participants:
            return
            
        participant = self.participants[p_id]
        print(f"\nParticipant {participant['name']}'s turn (Budget: ₹{participant['budget']:,})")
        
        # Display current inventory
        if participant['inventory']:
            print("Current inventory:")
            for product, quantity in participant['inventory'].items():
                print(f"  - {product.capitalize()}: {quantity} units")
        
        # Display available products
        print("\nAvailable products:")
        for product, details in self.products.items():
            print(f"  - {product.capitalize()}: Cost ₹{details['cost_price']:,}, "
                  f"Selling Price ₹{details['selling_price']:,}, "
                  f"Profit Margin {details['profit_margin']:.2f}%")
        
        # Reset investment for this round
        round_investment = 0
        
        # Get investment decisions
        while True:
            print(f"\nRemaining budget: ₹{participant['budget']:,}")
            print(f"Current round investment: ₹{round_investment:,}")
            print("Enter product to purchase (or 'done' to finish):")
            product_choice = input().lower()
            
            if product_choice == 'done':
                break
                
            if product_choice not in self.products:
                print("Invalid product. Please choose from the available options.")
                continue
                
            print(f"Enter quantity of {product_choice} to purchase:")
            try:
                quantity = int(input())
                if quantity <= 0:
                    print("Quantity must be positive.")
                    continue
                    
                cost = self.products[product_choice]['cost_price'] * quantity
                
                # Check if this would exceed the round budget
                if round_investment + cost > self.initial_budget:
                    print(f"This purchase would exceed your round budget of ₹{self.initial_budget:,}.")
                    continue
                    
                if cost > participant['budget']:
                    print(f"Not enough budget. You have ₹{participant['budget']:,}")
                    continue
                    
                # Add to inventory
                if product_choice in participant['inventory']:
                    participant['inventory'][product_choice] += quantity
                else:
                    participant['inventory'][product_choice] = quantity
                    
                participant['budget'] -= cost
                round_investment += cost
                
                # Update market demand
                self.products[product_choice]['quantity_sold'] += quantity
                
                print(f"Purchased {quantity} {product_choice}(s) for ₹{cost:,}.")
                print(f"Remaining budget: ₹{participant['budget']:,}")
                print(f"Round investment: ₹{round_investment:,}")
                
            except ValueError:
                print("Please enter a valid quantity.")
        
        # Check if participant spent more than allowed
        if round_investment > self.initial_budget:
            print(f"WARNING: You've invested ₹{round_investment:,}, which exceeds the ₹{self.initial_budget:,} limit.")
            print("You have been eliminated from the competition!")
            self.eliminated_participants.add(p_id)
    
    def random_investment_decision(self, p_id):
        """Generate random investment decisions for automated simulation"""
        if p_id in self.eliminated_participants:
            return
            
        participant = self.participants[p_id]
        round_investment = 0
        
        # Randomly distribute budget
        product_keys = list(self.products.keys())
        
        # Randomly decide how many products to invest in (1-4)
        num_products = np.random.randint(1, len(product_keys) + 1)
        selected_products = np.random.choice(product_keys, size=num_products, replace=False)
        
        # Allocate budget proportions for each product
        proportions = np.random.dirichlet(np.ones(len(selected_products)))
        
        for i, product in enumerate(selected_products):
            # Calculate budget for this product
            product_budget = min(int(proportions[i] * self.initial_budget), 
                               participant['budget'])
            
            # Calculate quantity that can be purchased
            cost_price = self.products[product]['cost_price']
            quantity = int(product_budget / cost_price)
            
            if quantity > 0:
                # Calculate actual cost
                actual_cost = quantity * cost_price
                
                # Update participant inventory and budget
                if product in participant['inventory']:
                    participant['inventory'][product] += quantity
                else:
                    participant['inventory'][product] = quantity
                    
                participant['budget'] -= actual_cost
                round_investment += actual_cost
                
                # Update market demand
                self.products[product]['quantity_sold'] += quantity
        
        # Check if participant spent more than allowed
        if round_investment > self.initial_budget:
            self.eliminated_participants.add(p_id)
    
    def calculate_profits(self):
        """Calculate profits for all participants based on their inventory and current market prices"""
        for p_id, participant in self.participants.items():
            if p_id in self.eliminated_participants:
                continue
                
            round_profit = 0
            for product, quantity in participant['inventory'].items():
                # Calculate potential selling value at current prices
                selling_value = quantity * self.products[product]['selling_price']
                cost_value = quantity * self.products[product]['cost_price']
                profit = selling_value - cost_value
                round_profit += profit
            
            participant['profit'] += round_profit
    
    def display_market_conditions(self):
        """Display current market conditions"""
        print("\nCURRENT MARKET CONDITIONS:")
        print(f"{'Product':<12} {'Cost Price':<12} {'Selling Price':<15} {'Profit Margin':<15} {'Units Sold':<10}")
        print("-" * 70)
        
        for product, details in self.products.items():
            print(f"{product.capitalize():<12} ₹{details['cost_price']:<12,} "
                  f"₹{details['selling_price']:<15,} "
                  f"{details['profit_margin']:<15.2f}% "
                  f"{details['quantity_sold']:<10}")
    
    def display_round_summary(self, round_num):
        """Display summary of participant standings"""
        print(f"\nROUND {round_num} SUMMARY:")
        print(f"{'Rank':<6} {'Participant':<12} {'Budget':<15} {'Profit':<15} {'Status':<10}")
        print("-" * 60)
        
        # Calculate ranking
        active_participants = [p for p_id, p in self.participants.items() 
                              if p_id not in self.eliminated_participants]
        
        # Sort by profit
        active_participants.sort(key=lambda x: x['profit'], reverse=True)
        
        # Display rankings
        rank = 1
        for p in active_participants:
            print(f"{rank:<6} {p['name']:<12} ₹{p['budget']:,} {' ':<3} ₹{p['profit']:,} {' ':<5} Active")
            rank += 1
        
        # Display eliminated participants
        for p_id in self.eliminated_participants:
            p = self.participants[p_id]
            print(f"{'-':<6} {p['name']:<12} ₹{p['budget']:,} {' ':<3} ₹{p['profit']:,} {' ':<5} Eliminated")
            
    def plot_price_trends(self):
        """Plot price trends over all rounds"""
        rounds = list(range(1, len(self.market_history) + 1))
        
        # Plot selling price trends
        plt.figure(figsize=(12, 6))
        for product in self.products:
            price_trend = [history[product]['selling_price'] for history in self.market_history]
            plt.plot(rounds, price_trend, marker='o', label=product.capitalize())
            
        plt.title('Product Selling Price Trends')
        plt.xlabel('Round')
        plt.ylabel('Selling Price (₹)')
        plt.legend()
        plt.grid(True)
        plt.show()
        
        # Plot profit margin trends
        plt.figure(figsize=(12, 6))
        for product in self.products:
            margin_trend = [history[product]['profit_margin'] for history in self.market_history]
            plt.plot(rounds, margin_trend, marker='o', label=product.capitalize())
            
        plt.title('Product Profit Margin Trends')
        plt.xlabel('Round')
        plt.ylabel('Profit Margin (%)')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def simulate_round(self, round_num):
        """Simulate one round of investments"""
        print(f"\n===== ROUND {round_num} =====")
        
        # Display current market conditions
        self.display_market_conditions()
        
        # Each participant makes investment decisions
        for p_id in self.participants:
            self.process_participant_investments(p_id)
            
        # Update market based on investment patterns
        self.update_market_prices()
        
        # Calculate profits for all participants
        self.calculate_profits()
        
        # Display round summary
        self.display_round_summary(round_num)
    
    def run_simulation(self, automated=False):
        """Run the full simulation for all rounds"""
        for round_num in range(1, self.rounds + 1):
            if automated:
                # Automated simulation
                print(f"\n===== ROUND {round_num} (AUTOMATED) =====")
                self.display_market_conditions()
                
                for p_id in self.participants:
                    self.random_investment_decision(p_id)
                    
                self.update_market_prices()
                self.calculate_profits()
                self.display_round_summary(round_num)
            else:
                # Interactive simulation
                self.simulate_round(round_num)
        
        print("\n===== FINAL RESULTS =====")
        self.display_round_summary(self.rounds)
        self.plot_price_trends()


# Example usage
if __name__ == "__main__":
    # Ask for simulation mode
    print("Welcome to the Fish Tank Event Simulator!")
    print("Choose simulation mode:")
    print("1. Interactive (manually input decisions for each participant)")
    print("2. Automated (randomly generate decisions)")
    
    mode = input("Enter choice (1/2): ")
    
    if mode == "1":
        # For testing, you might want to use fewer participants
        participants = int(input("Enter number of participants (default 50): ") or "50")
        rounds = int(input("Enter number of rounds (default 4): ") or "4")
        
        game = FishTankEvent(num_participants=participants, rounds=rounds)
        game.run_simulation(automated=False)
    else:
        participants = int(input("Enter number of participants (default 50): ") or "50")
        rounds = int(input("Enter number of rounds (default 4): ") or "4")
        
        game = FishTankEvent(num_participants=participants, rounds=rounds)
        game.run_simulation(automated=True)
