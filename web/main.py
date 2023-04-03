# Imports
import os
import json
import requests
from flask import Flask, request, jsonify, render_template
from kafka import KafkaProducer
import socket


# Create Flask app instance
app = Flask(__name__)

# Get kafka connection creds from env vars and convert to IP
kafka_address = os.getenv('KAFKA_ADDRESS')
kafka_address = socket.gethostbyname(kafka_address)

# Get API hostname from env vars and convert to IP
api_address = os.getenv('API_ADDRESS')
api_address = socket.gethostbyname(api_address)

# Create Kafka producer
producer = KafkaProducer(bootstrap_servers=f'{kafka_address}:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))


@app.route('/')
def show_form():
    return render_template('index.html')


@app.route('/produce', methods=['POST'])
# Get the message data from the request body and create a kafka message
def produce_message():
    message = {
        "username": request.json['username'],
        "userid": request.json['userid'],
        "price": int(request.json['price'])
    }
    # Send the message to Kafka topic using producer
    producer.send('my_topic', message)
    return 'Message sent to Kafka'

@app.route('/purchases/<user_id>', methods=['GET'])
# Send a GET request to the API and return purchases info for the requested user ID
def get_user_purchases(user_id):
    api_url = f"http://{api_address}:5001/api/purchases"
    response = requests.get(api_url)
    if response.status_code == 200:
        purchases = []
        for purchase in response.json():
            if purchase['userid'] == user_id:
                purchases.append(purchase)
        return jsonify(purchases)
    else:
        return jsonify({'error': 'Failed to fetch purchases from API'})


if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', debug=True, port=5002)
