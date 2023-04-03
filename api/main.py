# Imports
import os
from flask import Flask, jsonify
from threading import Thread
from pymongo import MongoClient
from datetime import datetime
from bson import json_util, ObjectId
from kafka.consumer import KafkaConsumer
import json
import socket

# Create Flask app instance
app = Flask(__name__)

# Get db connection creds from env vars and convert to IP
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_address = os.getenv('DB_ADDRESS')
db_address = socket.gethostbyname(db_address)

# Build Mongo URI string
URI = f"mongodb://{db_user}:{db_password}@{db_address}:27017"

# MongoDB client database and collection
client = MongoClient(URI)
db = client["PurchasesDB"]
collection = db["UserPurchases"]

# Get kafka connection creds from env vars and convert to IP
kafka_address = os.getenv('KAFKA_ADDRESS')
kafka_address = socket.gethostbyname(kafka_address)


# Create Kafka consumer
consumer = KafkaConsumer('my_topic',
                         group_id='my_group',
                         bootstrap_servers=[f'{kafka_address}:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                         auto_offset_reset='earliest',
                         max_poll_records=1)


# Process Kafka messages
def process_message():
    while True:
        message = consumer.poll(timeout_ms=1000, max_records=1)
        if not message:
            continue
        try:
            print(message)
            record = next(iter(message.values()))[0]
            print(record)
            data = record.value
            print(data)
            print("test")
            purchase = {
                "username": data["username"],
                "userid": data["userid"],
                "price": data["price"]
            }
            purchase["timestamp"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            print(purchase)
            # Insert the purchase into the DB
            result = collection.insert_one(purchase)
            print(f"Inserted purchase with ID: {result.inserted_id}")
            consumer.commit
        except Exception as e:
            print(f"Error inserting purchase: {e}")
            continue


# Retrieve purchases
@app.route("/api/purchases", methods=["GET"])
def get_all_purchases():
    try:
        purchases = list(collection.find())
        for purchase in purchases:
            purchase["_id"] = str(purchase["_id"])
        return jsonify(purchases), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Start the process_message function in a separate thread
    process_thread = Thread(target=process_message)
    process_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', debug=True, port=5001)
