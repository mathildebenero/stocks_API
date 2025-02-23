import os  # Import operating system functions to read environment variables
import uuid  # Import UUID to generate unique IDs for stocks
import requests  # Import requests to call external APIs
from flask import Flask, request, jsonify  # Import Flask framework
from pymongo import MongoClient  # Import MongoDB client to interact with the database

# 🔹 Load MongoDB URI from environment variable
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@mongodb:27017/stockdb?authSource=admin")
client = MongoClient(MONGO_URI)  # Connect to MongoDB
db = client["stockdb"]  # Select the database
# stocks_collection = db["stocks"]  # Select the collection for storing stocks

COLLECTION_NAME = os.getenv("STOCKS_COLLECTION", "stocks")  
stocks_collection = db[COLLECTION_NAME]


# 🔹 API Ninjas configuration
API_KEY = os.getenv("NINJA_API_KEY", "fMYKMHPC1CA9KlTDEH9sag==79z6HMNJjIRIJNhN")  # Load API key from environment variables
API_URL = "https://api.api-ninjas.com/v1/stockprice"  # API Ninjas endpoint for stock prices


def create_routes(app):

    # 📌 STEP 1️⃣: User Adds or Retrieves Stocks
    @app.route("/stocks", methods=["GET", "POST"])
    def manage_stocks():
        if request.method == "GET":
            if "id" in request.args:
                the_id = request.args["id"]
                stock = stocks_collection.find_one({"id": the_id}, {"_id": 0})
                if stock:
                    return jsonify([stock]), 200
                else:
                    return jsonify([]), 404
            else:
                # Return all
                stocks = list(stocks_collection.find({}, {"_id": 0}))
                return jsonify(stocks), 200

        if request.method == "POST":  # 🔹 If it's a POST request, add a new stock
            data = request.json  # Get JSON request data
            if not all(field in data for field in ["symbol", "purchase price", "shares"]):  # Validate input
                return jsonify({"error": "Malformed data"}), 400  # Return error if missing fields

            stock_id = str(uuid.uuid4())  # Generate unique stock ID
            new_stock = {
                "id": stock_id,
                "name": data.get("name", "NA"),  # Stock name (manual input)
                "symbol": data["symbol"].upper(),  # Convert symbol to uppercase
                "purchase price": round(float(data["purchase price"]), 2),  # Round purchase price
                "purchase date": data.get("purchase date", "NA"),  # Get purchase date
                "shares": int(data["shares"]),  # Convert shares to integer
            }

            # 🔹 Check if stock symbol already exists
            if stocks_collection.find_one({"symbol": new_stock["symbol"]}):
                return jsonify({"error": "Stock symbol already exists"}), 400  # Prevent duplicate stocks

            stocks_collection.insert_one(new_stock)  # Insert stock into MongoDB
            return jsonify({"id": stock_id}), 201  # Return success response

    # 📌 STEP 2️⃣: User Checks a Specific Stock (GET / PUT / DELETE)
    @app.route("/stocks/<id>", methods=["GET", "PUT", "DELETE"])
    def manage_stock(id):
        stock = stocks_collection.find_one({"id": id}, {"_id": 0})  # 🔹 Find stock by ID
        if not stock:  
            return jsonify({"error": "Not found"}), 404  # 🔹 Return error if stock not found

        if request.method == "GET":  # 🔹 Return stock details
            return jsonify(stock), 200  

        if request.method == "PUT":  # 🔹 Update stock details
            data = request.json
            stocks_collection.update_one({"id": id}, {"$set": data})  # Update MongoDB record
            return jsonify({"id": id}), 200  

        if request.method == "DELETE":  # 🔹 Delete stock
            stocks_collection.delete_one({"id": id})  
            return "", 204  # Return empty response (successful deletion)

    # 📌 STEP 3️⃣: Get Real-Time Stock Value
    @app.route("/stock-value/<id>", methods=["GET"])
    def stock_value(id):
        stock = stocks_collection.find_one({"id": id}, {"_id": 0})  # 🔹 Find stock by ID
        if not stock:
            return jsonify({"error": "Not found"}), 404  

        symbol = stock["symbol"]
        response = requests.get(API_URL, headers={"X-Api-Key": API_KEY}, params={"ticker": symbol})  # 🔹 Fetch real-time price

        if response.status_code != 200:
            return jsonify({"server error": f"API response code {response.status_code}"}), 500  # Handle API error

        ticker_price = response.json()["price"]  # Extract stock price from API response
        stock_value = round(stock["shares"] * ticker_price, 2)  # Calculate stock value

        return jsonify({  # 🔹 Return stock price and value
            "symbol": symbol,
            "ticker": ticker_price,
            "stock value": stock_value
        }), 200

    # 📌 STEP 4️⃣: Get Portfolio Total Value (FIXED VERSION)
    @app.route("/portfolio-value", methods=["GET"])
    def portfolio_value():
        total_value = 0  # Initialize total value to zero

        stocks = list(stocks_collection.find({}, {"_id": 0}))  # 🔹 Fetch all stocks from MongoDB
        for stock in stocks:
            symbol = stock["symbol"]
            response = requests.get(API_URL, headers={"X-Api-Key": API_KEY}, params={"ticker": symbol})  # 🔹 Fetch live price

            if response.status_code != 200:
                return jsonify({"server error": f"API response code {response.status_code}"}), 500  # Handle API error

            ticker_price = response.json()["price"]  # Get live stock price
            total_value += stock["shares"] * ticker_price  # 🔹 Calculate total portfolio value

        return jsonify({  # 🔹 Return total portfolio value
            "date": "07-12-2024",
            "portfolio value": round(total_value, 2)
        }), 200
    
    @app.route('/kill', methods=['GET'])
    def kill_container():
        os._exit(1)

