# Location Tracking Server

## Prerequisites
- Python 3.7+
- No additional libraries required (uses standard library)

## Setup and Running

1. **Firewall Configuration**:
   - Ensure port 8080 is open
   - Temporarily disable firewall for testing

2. **Running the Server**:
   ```bash
   python location_server.py
   ```

3. **Server Behavior**:
   - Listens on all network interfaces (0.0.0.0)
   - Port: 8080
   - Saves location data to `location_data.csv`
   - Logs events to `location_server.log`

## Troubleshooting
- Check `location_server.log` for detailed logs
- Verify server IP matches the one entered in the app
- Ensure no other service is using port 8080

## Data Format
CSV columns: Device_ID, Latitude, Longitude, Timestamp

## Testing
- Use the mobile app to send location data
- Verify data in `location_data.csv`

## Security Note
This is a basic test server. Do not use in production without proper security measures.
