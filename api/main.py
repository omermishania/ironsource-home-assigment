import os
from flask import Flask, jsonify
from threading import Thread
from pymongo import MongoClient
from datetime import datetime
from bson import json_util, ObjectId
from kafka.consumer import KafkaConsumer
import json
import socket


app = Flask(__name__)

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_address = os.getenv('DB_ADDRESS')
db_address = socket.gethostbyname(db_address)
kafka_address = os.getenv('KAFKA_ADDRESS')
kafka_address = socket.gethostbyname(kafka_address)

URI = f"mongodb://{db_user}:{db_password}@{db_address}:27017"

client = MongoClient(URI)
db = client["PurchasesDB"]
collection = db["UserPurchases"]


consumer = KafkaConsumer('my_topic',
                         bootstrap_servers=[f'{kafka_address}:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                         enable_auto_commit=False,
                         auto_offset_reset='earliest',
                         max_poll_records=1)


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
        except Exception as e:
            print(f"Error inserting purchase: {e}")
            continue


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
