import socket
import os
import logging
from datetime import datetime
import threading
import pandas as pd
from pymongo import MongoClient

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
SERVER_PORT = 8080

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

def start_server():
    """Start the socket server to receive location data."""
    setup_logging()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5)
        logging.info(f"Location server listening on {SERVER_HOST}:{SERVER_PORT}")

        while True:
            try:
                client_socket, address = server_socket.accept()
                
                # Use threading to handle multiple connections
                client_thread = threading.Thread(
                    target=handle_client_connection, 
                    args=(client_socket, address)
                )
                client_thread.start()

            except Exception as connection_error:
                logging.error(f"Connection error: {connection_error}")

    except Exception as server_error:
        logging.critical(f"Server startup error: {server_error}")
    finally:
        server_socket.close()

def main():
    """Main entry point for the server."""
    try:
        start_server()
    except KeyboardInterrupt:
        logging.info("Server stopped by user.")
    except Exception as e:
        logging.critical(f"Unexpected server error: {e}")

if __name__ == '__main__':
    main()
