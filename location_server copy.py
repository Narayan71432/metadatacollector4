import socket
import csv
import os
import logging
from datetime import datetime
import threading

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
CSV_FILE_PATH = 'location_data.csv'

def setup_logging():
    """Configure logging with file and console output."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

def ensure_csv_exists():
    """Ensure the CSV file exists with the correct headers."""
    try:
        if not os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Device_ID', 'Latitude', 'Longitude', 'Timestamp'])
            logging.info(f"Created CSV file: {CSV_FILE_PATH}")
    except Exception as e:
        logging.error(f"Error creating CSV file: {e}")

def handle_client_connection(client_socket, address):
    """Handle individual client connections."""
    try:
        logging.info(f"Connection from {address}")
        data = client_socket.recv(1024).decode('utf-8').strip()
        
        if not data:
            logging.warning(f"Received empty data from {address}")
            return

        logging.info(f"Received location data from {address}: {data}")

        # Append data to CSV
        with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
            csvfile.write(data + '\n')
        
        logging.info(f"Saved location data: {data}")

    except Exception as e:
        logging.error(f"Error processing data from {address}: {e}")
    finally:
        client_socket.close()

def start_server():
    """Start the socket server to receive location data."""
    setup_logging()
    ensure_csv_exists()

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
