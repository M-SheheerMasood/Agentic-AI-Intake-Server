import socket
import sys
import os

def start_client():
    # Network Config
    HOST = '127.0.0.1'  # Localhost (since the server is on the same machine)
    PORT = 5000         # Listing port

    # TCP socket (IPv4, TCP stream)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to server
        client_socket.connect((HOST, PORT))
        print("=== Connected to the 3D Printing Assistant ===")
        print("Type your message, paste a local file path (e.g., C:/specs.gcode), or type 'quit' to exit.\n")
        
        # Main loop
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            # exit condition
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Closing connection...")
                break
                
            # valid formats
            valid_extensions = ('.stl', '.3mf', '.gcode')
            
            # Check if the user is trying to upload a 3D printing file
            if user_input.lower().endswith(valid_extensions):
                
                # Validate the path exists on their computer
                if os.path.exists(user_input):
                    print("[System] Valid 3D file detected. Sending to server...")
                    # Prepend the hidden tag for the server to parse
                    payload_to_send = f"[FILE_UPLOAD] {user_input}"
                        
                else:
                    # Catch error locally, dont send anything over TCP
                    print(f"[Error] The file '{user_input}' does not exist. Please check the path.")
                    continue
            else:
                # normal chat msg
                payload_to_send = user_input
                
            # encoding string
            client_socket.send(payload_to_send.encode('utf-8'))

            # Wait for response
            response_bytes = client_socket.recv(4096)
            
            # checking if valid server response
            if not response_bytes:
                print("\n[Server disconnected]")
                break
                
            # Decoding string
            response = response_bytes.decode('utf-8')
            print(f"\nAssistant: {response}\n")
            
    except ConnectionRefusedError:
        print("Error: Could not connect to the server. Make sure server.py is running first!")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # closing port
        client_socket.close()
        sys.exit()

if __name__ == "__main__":
    start_client()