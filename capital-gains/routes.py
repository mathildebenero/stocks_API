import os
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient

# retrieves real-time stock prices.
# calculates capital gains for stored stocks.

# 🔹 Load MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@mongodb:27017/stockdb?authSource=admin")
client = MongoClient(MONGO_URI)
db = client["stockdb"]
stocks_collection = db["stocks"]

# 🔹 API Ninjas configuration
API_KEY = os.getenv("NINJA_API_KEY", "fMYKMHPC1CA9KlTDEH9sag==79z6HMNJjIRIJNhN")
API_URL = "https://api.api-ninjas.com/v1/stockprice"


def create_routes(app):
    @app.route("/capital-gains", methods=["GET"])
    def calculate_capital_gains():
        """Calculate capital gains for all stocks in the database."""
        query = {}

        # 🔹 Apply query filters if provided
        if "numsharesgt" in request.args:
            query["shares"] = {"$gt": int(request.args["numsharesgt"])}
        if "numshareslt" in request.args:
            query.setdefault("shares", {})["$lt"] = int(request.args["numshareslt"])

        if "portfolio" in request.args:
            which = request.args["portfolio"]
            if which == "stocks1":
                col = db["stocks1"]
            elif which == "stocks2":
                col = db["stocks2"]
            else:
                return jsonify({"error": "Unknown portfolio"}), 400
            stocks = list(col.find(query, {"_id": 0}))
        else:
            # No portfolio param => combine both
            stocks_1 = list(db["stocks1"].find(query, {"_id": 0}))
            stocks_2 = list(db["stocks2"].find(query, {"_id": 0}))
            stocks = stocks_1 + stocks_2


        results = []
        for stock in stocks:
            symbol = stock["symbol"]

            # 🔹 Fetch real-time stock price
            response = requests.get(API_URL, headers={"X-Api-Key": API_KEY}, params={"ticker": symbol})
            if response.status_code != 200:
                return jsonify({"error": f"Failed to fetch price for {symbol}"}), 500

            current_price = response.json()["price"]
            capital_gain = (current_price - stock["purchase price"]) * stock["shares"]

            results.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "purchase price": stock["purchase price"],
                "current price": current_price,
                "shares": stock["shares"],
                "capital gain": round(capital_gain, 2)
            })

        return jsonify(results), 200


