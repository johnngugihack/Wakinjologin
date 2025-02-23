from flask import Flask, request, jsonify
import pymysql
from pymysql import Error
from flask_cors import CORS  # Import CORS
import bcrypt  # Import bcrypt for password hashing
import smtplib
from dotenv import load_dotenv
import os
load_dotenv()
# Your Flask app code here
wakinjologin = Flask(__name__)
CORS(wakinjologin, resources={r"/*": {"origins": "https://inventory-j107.onrender.com"}})

# MySQL connection details using PyMySQL
def get_db_connection():
    try:

        # Establish connection using PyMySQL with utf8mb4 charset
        connection = pymysql.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database"),
            
            charset='utf8mb4',      # Charset set to utf8mb4 for better support
            cursorclass=pymysql.cursors.DictCursor  # Optional, returns results as dictionaries
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to hash the password using bcrypt
def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')
@wakinjologin.route("/")
def home():
    return "Hello, John!"


# Define the route that accepts a POST request for registration

@wakinjologin.route('/register', methods=['POST'])
def register_user():
    # Get 'worker_id', 'username', 'phone_number', 'password' and 'confirm_password' from form data
    worker_id = request.form.get('worker_id')
    username = request.form.get('username')
    phone_number = request.form.get('phone_number')
    password = request.form.get('passwd')
    confirm_password = request.form.get('confirm_passwd')

    # Validate if all fields are present
    if not worker_id or not username or not phone_number or not password or not confirm_password:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    # Validate if the passwords match
    if password != confirm_password:
        return jsonify({
            "status": "error",
            "message": "Passwords do not match"
        }), 400

    # Hash the password before saving it
    hashed_password = hash_password(password)

    # Save data to MySQL database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Insert data into the 'employees' table (with hashed password)
            cursor.execute("INSERT INTO employees (worker_id, username, phone_number, passwd) VALUES (%s, %s, %s, %s)", 
                           (worker_id, username, phone_number, hashed_password))
            connection.commit()  # Commit the transaction

            # Close the connection
            cursor.close()
            connection.close()

            return jsonify({
                "status": "success",
                "message": "User registered successfully"
            }), 200

        except Error as e:
            return jsonify({
                "status": "error",
                "message": f"Error saving data to MySQL: {e}"
            }), 500

    else:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500


@wakinjologin.route('/delete_employee', methods=['POST'])
def delete_employee():
    # Get 'username' from the form data
    username = request.form.get('username')
    
    # Validate if the 'username' is provided
    if not username:
        return jsonify({
            "status": "error",
            "message": "Missing username"
        }), 400

    # Retrieve the user from the database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Check if the username exists in the database
            cursor.execute("SELECT * FROM employees WHERE username = %s", (username,))
            user = cursor.fetchone()

            # If the user does not exist
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Username not found"
                }), 404

            # Delete the user if exists
            cursor.execute("DELETE FROM employees WHERE username = %s", (username,))
            connection.commit()

            cursor.close()
            connection.close()

            return jsonify({
                "status": "success",
                "message": "Deleted successfully"
            }), 200

        except Error as e:
            # Handle database errors
            return jsonify({
                "status": "error",
                "message": f"Error accessing database: {e}"
            }), 500

    else:
        # If the database connection fails
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500



@wakinjologin.route('/admin_register', methods=['POST'])
def admin_register():
    # Get 'admin_id', 'username', 'phone_number', 'password' and 'confirm_password' from form data
    admin_id = request.form.get('admin_id')
    username = request.form.get('username')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_passwd')

    # Validate if all fields are present
    if not admin_id or not username or not phone_number or not password or not confirm_password:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    # Validate if the passwords match
    if password != confirm_password:
        return jsonify({
            "status": "error",
            "message": "Passwords do not match"
        }), 400

    # Hash the password before saving it
    hashed_password = hash_password(password)

    # Save data to MySQL database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Insert data into the 'employees' table (with hashed password)
            cursor.execute("INSERT INTO admins (admin_id, username, phone_number, password) VALUES (%s, %s, %s, %s)", 
                           (admin_id, username, phone_number, hashed_password))
            connection.commit()  # Commit the transaction

            # Close the connection
            cursor.close()
            connection.close()

            return jsonify({
                "status": "success",
                "message": "Admin registered successfully"
            }), 200

        except Error as e:
            return jsonify({
                "status": "error",
                "message": f"Error saving data to MySQL: {e}"
            }), 500

    else:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500
@wakinjologin.route('/item_register', methods=['POST'])
def item_register():
    # Get 'item_name', 'quantity', 'company_name', 'price_per_item'
    item_name = request.form.get('item_name')
    quantity = request.form.get('quantity')
    company_name = request.form.get('company_name')
    price_per_item = request.form.get('price_per_item')
    
    # Validate if all fields are present
    if not item_name or not quantity or not company_name or not price_per_item:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400
    
    # Connect to the database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Check if item already exists for the given company
            cursor.execute("SELECT * FROM items WHERE item_name = %s AND company_name = %s", (item_name, company_name))
            existing_item = cursor.fetchone()
            
            if existing_item:
                return jsonify({
                    "status": "error",
                    "message": "Item already exists. Please go to the update panel."
                }), 400
            
            # Insert data into the 'items' table if item does not exist
            cursor.execute("INSERT INTO items (item_name, quantity, company_name, price_per_item) VALUES (%s, %s, %s, %s)", 
                           (item_name, quantity, company_name, price_per_item))
            connection.commit()  # Commit the transaction
            
            # Close the connection
            cursor.close()
            connection.close()
            
            return jsonify({
                "status": "success",
                "message": "Product registered successfully"
            }), 200
        
        except Error as e:
            return jsonify({
                "status": "error",
                "message": f"Error saving data to MySQL: {e}"
            }), 500
    
    else:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500


# Define the route that accepts a POST request for login
@wakinjologin.route('/login', methods=['POST'])
def login_user():
    # Get 'username' and 'password' from form data
    username = request.form.get('username')
    password = request.form.get('passwd')

    # Validate if both fields are present
    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Missing username or password"
        }), 400

    # Retrieve the user from the database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Check if the username exists
            cursor.execute("SELECT * FROM employees WHERE username = %s", (username,))
            user = cursor.fetchone()

            # If the user does not exist
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Username not found"
                }), 404

            # Compare the entered password with the stored hash
            if bcrypt.checkpw(password.encode('utf-8'), user['passwd'].encode('utf-8')):  # Password match check
                return jsonify({
                    "status": "success",
                    "message": "Login successful"
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Invalid password"
                }), 400

        except Error as e:
            return jsonify({
                "status": "error",
                "message": f"Error accessing database: {e}"
            }), 500

    else:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500

@wakinjologin.route('/admin_login', methods=['POST'])
def admin_login_user():
    # Get 'username' and 'password' from form data
    username = request.form.get('username')
    password = request.form.get('password')

    # Validate if both fields are present
    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Missing username or password"
        }), 400

    # Retrieve the user from the database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Check if the username exists
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            user = cursor.fetchone()

            # If the user does not exist
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Username not found"
                }), 404

            # Compare the entered password with the stored hash
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):  # Password match check
                return jsonify({
                    "status": "success",
                    "message": "Admin-login successful"
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Invalid password"
                }), 400

        except Error as e:
            return jsonify({
                "status": "error",
                "message": f"Error accessing database: {e}"
            }), 500

    else:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500

import traceback  # Add this to log errors
@wakinjologin.route('/update_inventory', methods=['POST'])
def update_inventory():
    try:
        data = request.json
        # Validate input structure
        if not data or 'items' not in data or not isinstance(data['items'], list):
            return jsonify({"status": "error", "message": "Invalid input, expecting a list of items."}), 400

        # Get DB connection
        connection = get_db_connection()
        if not connection:
            return jsonify({"status": "error", "message": "Database connection failed"}), 500

        # Use DictCursor (make sure your get_db_connection() sets this)
        cursor = connection.cursor()  # Assuming get_db_connection() uses DictCursor
        responses = []
        missing_items = []

        # --- Pre-check: Verify ALL items exist ---
        for item in data['items']:
            item_name = item.get('item_name')
            company_name = item.get('company_name')
            if not item_name or not company_name:
                missing_items.append({
                    "item_name": item_name,
                    "company_name": company_name,
                    "error": "Missing item_name or company_name"
                })
                continue

            cursor.execute(
                "SELECT quantity FROM items WHERE item_name = %s AND company_name = %s",
                (item_name, company_name)
            )
            item_record = cursor.fetchone()
            if not item_record:
                missing_items.append({
                    "item_name": item_name,
                    "company_name": company_name,
                    "error": "Item not found"
                })

        if missing_items:
            cursor.close()
            connection.close()
            return jsonify({
                "status": "error",
                "message": "Register this item first!",
                "details": missing_items
            }), 404

        # --- All items exist. Proceed with update ---
        for item in data['items']:
            item_name = item.get('item_name')
            company_name = item.get('company_name')
            quantity = item.get('quantity')
            update_type = item.get('type')

            # Basic validations
            if not all([item_name, company_name, quantity, update_type]):
                responses.append({"item_name": item_name, "status": "error", "message": "Missing data"})
                continue

            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError("Quantity must be a positive integer")
            except (TypeError, ValueError):
                responses.append({"item_name": item_name, "status": "error", "message": "Invalid quantity"})
                continue

            # Retrieve current quantity (we already confirmed the item exists)
            cursor.execute(
                "SELECT quantity FROM items WHERE item_name = %s AND company_name = %s",
                (item_name, company_name)
            )
            item_record = cursor.fetchone()
            current_quantity = item_record["quantity"]

            # Update logic based on update_type
            if update_type == 'add':
                new_quantity = current_quantity + quantity
                cursor.execute(
                    "UPDATE items SET quantity = %s WHERE item_name = %s AND company_name = %s",
                    (new_quantity, item_name, company_name)
                )
            elif update_type == 'subtract':
                if current_quantity < quantity:
                    responses.append({"item_name": item_name, "status": "error", "message": "Not enough stock"})
                    continue
                new_quantity = current_quantity - quantity
                cursor.execute(
                    "UPDATE items SET quantity = %s WHERE item_name = %s AND company_name = %s",
                    (new_quantity, item_name, company_name)
                )
            else:
                responses.append({"item_name": item_name, "status": "error", "message": "Invalid update type"})
                continue

            responses.append({
                "item_name": item_name,
                "status": "✅ Success",
                "message": f"🎉 Inventory updated! New quantity: {new_quantity}"
            })

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"updates": responses}), 200

    except Error as db_err:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Database error: {str(db_err)}"}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

# Define the route that accepts a GET request to check if the username and password exist
@wakinjologin.route('/check_user_exists', methods=['GET'])
def check_user_exists():
    # Get 'username' and 'password' from query parameters
    username = request.args.get('username')
    password = request.args.get('passwd')

    # Validate if the username and password are provided
    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Username and password are required"
        }), 400

    # Retrieve the user from the database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Check if the username exists
            cursor.execute("SELECT * FROM employees WHERE username = %s", (username,))
            user = cursor.fetchone()

            # If the user does not exist
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Username not found"
                }), 404

            # Compare the entered password with the stored hash
            if bcrypt.checkpw(password.encode('utf-8'), user['passwd'].encode('utf-8')):
                return jsonify({
                    "status": "success",
                    "message": "User exists and password matches"
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "Invalid password"
                }), 400

        except Error as e:
            return jsonify({
                "status": "error",
                "message": f"Error accessing database: {e}"
            }), 500

    else:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500

@wakinjologin.route('/get_employees', methods=['GET'])
def get_employees():
    # Retrieve the employees from the database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Retrieve all employees from the database
            cursor.execute("SELECT worker_id, username, phone_number FROM employees")
            employees = cursor.fetchall()

            # If no employees exist
            if not employees:
                return jsonify({
                    "status": "error",
                    "message": "No employees found"
                }), 404

            # Return the list of employees
            return jsonify({
                "status": "success",
                "message": "Employees retrieved successfully",
                "data": employees
            }), 200

        except Error as e:
            return jsonify({
                "status": "error",
                "message": f"Error accessing database: {e}"
            }), 500

    else:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500
@wakinjologin.route('/get_items', methods=['GET'])
def get_items():
    # Retrieve the employees from the database
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Retrieve all items from the database
            cursor.execute("SELECT id, item_name, quantity, company_name, price_per_item FROM items")
            items = cursor.fetchall()

            # If no items exist
            if not items:
                return jsonify({
                    "status": "error",
                    "message": "No items found"
                }), 404

            # Return the list of items
            return jsonify({
                "status": "success",
                "message": "items retrieved successfully",
                "data": items
            }), 200

        except Error as e:
            return jsonify({
                "status": "error",
                "message": f"Error accessing database: {e}"
            }), 500

    else:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500


# Run the application
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use Render's allowed port  
    wakinjologin.run(host="0.0.0.0", port=port)  