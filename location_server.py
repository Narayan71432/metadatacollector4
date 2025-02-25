import socket
import os
import logging
from datetime import datetime
import threading
import pandas as pd
from pymongo import MongoClient
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('location_server.log'),
        logging.StreamHandler()
    ]
)

SERVER_HOST = '0.0.0.0'  # Listen on all available interfaces
SERVER_PORT = 10000  # Render uses port 10000

# MongoDB connection string
connection_string = "mongodb+srv://metadatacollector1:metadatacollector1@cluster0.shnle.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)

# Access the database and collection
db = client['your_database_name']  # replace with your database name
collection = db['your_collection_name']  # replace with your collection name

def setup_logging():
    """Configure logging with file and console output."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

def store_data_in_mongodb(data):
    """Store incoming data directly into MongoDB Atlas."""
    try:
        collection.insert_many(data)
        logging.info("Data inserted successfully into MongoDB!")
    except Exception as e:
        logging.error(f"Error inserting data into MongoDB: {e}")

def handle_client_connection(client_socket, address):
    """Handle individual client connections."""
    try:
        data = client_socket.recv(1024).decode('utf-8')
        logging.info(f"Received location data from {address}: {data}")

        # Split the incoming data by commas
        uuid, latitude, longitude, timestamp = data.split(',')

        # Create a dictionary with appropriate keys
        data_dict = [{
            'UUID': uuid,
            'Latitude': float(latitude),
            'Longitude': float(longitude),
            'Timestamp': timestamp
        }]

        # Store data in MongoDB
        store_data_in_mongodb(data_dict)

        logging.info(f"Saved location data: {data}")
    except Exception as e:
        logging.error(f"Error handling client connection: {e}")

def start_socket_server():
    """Start the socket server and listen for incoming connections."""
    setup_logging()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT + 1))  # Use a different port for socket
    server_socket.listen(5)
    logging.info(f"Socket server listening on {SERVER_HOST}:{SERVER_PORT + 1}")

    while True:
        try:
            client_socket, address = server_socket.accept()
            logging.info(f"Accepted connection from {address}")
            client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, address))
            client_thread.start()
        except Exception as connection_error:
            logging.error(f"Connection error: {connection_error}")

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify({'status': 'success', 'message': 'Connected to server'})

@app.route('/api/locations', methods=['POST'])
def save_location():
    try:
        data = request.json
        
        # Create a dictionary with appropriate keys
        data_dict = [{
            'UUID': data['deviceId'],
            'Latitude': float(data['latitude']),
            'Longitude': float(data['longitude']),
            'Timestamp': data['timestamp']
        }]

        # Store data in MongoDB
        store_data_in_mongodb(data_dict)
        
        logging.info(f"Saved location data via HTTP: {data_dict}")
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logging.error(f"Error saving location via HTTP: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    # Start socket server in a separate thread
    socket_thread = threading.Thread(target=start_socket_server)
    socket_thread.daemon = True
    socket_thread.start()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=10000, debug=True)