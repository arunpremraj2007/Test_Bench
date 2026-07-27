from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# Configuration parameters
SERVER_IP = "102.79.221.102"  # Replace with your Modbus TCP server/PLC IP
PORT = 502                    # Default Modbus TCP port
START_ADDRESS = 0            # The register address you want to start reading from
REGISTER_COUNT = 5            # Number of consecutive registers to read
SLAVE_ID = 1                 # Unit Identifier / Slave Address (often defaults to 1 or 247)

def read_holding_registers():
    # Initialize the Modbus TCP Client
    client = ModbusTcpClient(SERVER_IP, port=PORT)
    
    try:
        # Establish the connection
        if client.connect():
            print(f"Successfully connected to {SERVER_IP}:{PORT}")
            
            # Request holding registers (Function Code 0x03)
            result = client.read_holding_registers(
                address=START_ADDRESS, 
                count=REGISTER_COUNT, 
                device_id=SLAVE_ID,
            )
            
            # Check if the response contains Modbus errors
            if not result.isError():
                # Extract and print register values
                # result.registers is a list containing 16-bit integer values
                print("Register Values:", result.registers)
                
                # Loop through each item
                for index, value in enumerate(result.registers):
                    actual_address = START_ADDRESS + index
                    print(f"Address {actual_address}: {value}")
            else:
                print(f"Modbus Error response received: {result}")
                
        else:
            print(f"Failed to connect to server at {SERVER_IP}")
            
    except ModbusException as e:
        print(f"An unexpected Modbus protocol error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Always close the network socket connection cleanly
        client.close()
        print("Connection closed.")

if __name__ == "__main__":
    read_holding_registers()


from flask import Flask, render_template_string
from pymodbus.client import ModbusTcpClient
import time

# --- Configuration ---
SERVER_IP = "102.79.221.102"
PORT = 502
START_ADDRESS = 0
REGISTER_COUNT = 5
POLL_INTERVAL = 2  # seconds

app = Flask(__name__)

# --- HTML Template ---
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Modbus Register Viewer</title>
    <meta http-equiv="refresh" content="3"> <!-- auto-refresh every 3s -->
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 50%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>Modbus Holding Registers</h2>
    <table>
        <tr><th>Address</th><th>Value</th></tr>
        {% for addr, val in registers %}
        <tr><td>{{ addr }}</td><td>{{ val }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def read_registers():
    client = ModbusTcpClient(SERVER_IP, port=PORT)
    values = []
    try:
        if client.connect():
            result = client.read_holding_registers(START_ADDRESS, REGISTER_COUNT)
            if result and not result.isError():
                for i, val in enumerate(result.registers):
                    values.append((START_ADDRESS + i, val))
            else:
                values.append(("Error", str(result)))
        else:
            values.append(("Connection", "Failed"))
    finally:
        client.close()
    return values

@app.route("/")
def index():
    registers = read_registers()
    return render_template_string(html_template, registers=registers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)


