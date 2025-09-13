 from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
     import json
     import os

     app = Flask(__name__)
     app.secret_key = 'bob_cafe_secret_key'

     class CafeInventory:
         def __init__(self):
             # Use in-memory storage for Railway deployment
             self.inventory = {
                 "coffee_beans": {"quantity": 50, "unit": "kg", "price_per_unit": 15.0},
                 "milk": {"quantity": 20, "unit": "liters", "price_per_unit": 2.5},
                 "sugar": {"quantity": 10, "unit": "kg", "price_per_unit": 3.0},
                 "cups": {"quantity": 200, "unit": "pieces", "price_per_unit": 0.5},
                 "pastries": {"quantity": 30, "unit": "pieces", "price_per_unit": 4.0},
                 "tea_bags": {"quantity": 100, "unit": "pieces", "price_per_unit": 0.3}
             }

         def add_stock(self, item, quantity):
             if item in self.inventory:
                 self.inventory[item]["quantity"] += quantity
                 return True, f"Added {quantity} {self.inventory[item]['unit']} of {item.replace('_', ' ')}"
             return False, f"Item '{item}' not found in inventory"

         def use_stock(self, item, quantity):
             if item in self.inventory:
                 if self.inventory[item]["quantity"] >= quantity:
                     self.inventory[item]["quantity"] -= quantity
                     return True, f"Used {quantity} {self.inventory[item]['unit']} of {item.replace('_', ' ')}"
                 else:
                     return False, f"Insufficient stock! Only {self.inventory[item]['quantity']} {self.inventory[item]['unit']} available"
             return False, f"Item '{item}' not found in inventory"

         def get_low_stock(self, threshold=10):
             low_stock = []
             for item, details in self.inventory.items():
                 if details["quantity"] <= threshold:
                     low_stock.append({
                         'name': item.replace('_', ' ').title(),
                         'quantity': details['quantity'],
                         'unit': details['unit']
                     })
             return low_stock

         def calculate_inventory_value(self):
             total_value = 0
             for item, details in self.inventory.items():
                 total_value += details["quantity"] * details["price_per_unit"]
             return total_value

     # Initialize inventory
     inventory = CafeInventory()

     @app.route('/')
     def index():
         try:
             total_value = inventory.calculate_inventory_value()
             low_stock = inventory.get_low_stock()
             return render_template('index.html',
                                  inventory=inventory.inventory,
                                  total_value=total_value,
                                  low_stock=low_stock)
         except Exception as e:
             return f"Error: {str(e)}", 500

     @app.route('/add_stock', methods=['POST'])
     def add_stock():
         try:
             item = request.form.get('item')
             quantity = int(request.form.get('quantity'))
             success, message = inventory.add_stock(item, quantity)
             if success:
                 flash(message, 'success')
             else:
                 flash(message, 'error')
         except ValueError:
             flash('Please enter a valid quantity', 'error')
         except Exception as e:
             flash(f'Error: {str(e)}', 'error')
         return redirect(url_for('index'))

     @app.route('/use_stock', methods=['POST'])
     def use_stock():
         try:
             item = request.form.get('item')
             quantity = int(request.form.get('quantity'))
             success, message = inventory.use_stock(item, quantity)
             if success:
                 flash(message, 'success')
             else:
                 flash(message, 'error')
         except ValueError:
             flash('Please enter a valid quantity', 'error')
         except Exception as e:
             flash(f'Error: {str(e)}', 'error')
         return redirect(url_for('index'))

     @app.route('/api/inventory')
     def api_inventory():
         try:
             return jsonify(inventory.inventory)
         except Exception as e:
             return jsonify({"error": str(e)}), 500

     @app.route('/health')
     def health():
         return "OK", 200

     if __name__ == '__main__':
         import os
         port = int(os.environ.get('PORT', 5000))
         app.run(debug=False, host='0.0.0.0', port=port)
