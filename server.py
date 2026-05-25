import socket
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

with open('data.json', 'r') as file:
    app_data = json.load(file)

inventory_db = app_data['inventory_db']

def calculate_quote(item_type: str, quantity_or_grams: int):
    """Calculates the price for standard 3D printed items or when filament usage in grams is known."""

    print(f"\n[Agent Activity] Executing 'calculate_quote' -> Item: {item_type}, Qty: {quantity_or_grams}")
    
    pricing = inventory_db["pricing"]
    
    if item_type.lower() == "keychain":
        total_cost = quantity_or_grams * pricing["keychain_flat"]
        return f"System: Quote successful. {quantity_or_grams} keychains cost a total of {total_cost} PKR."
        
    elif item_type.lower() == "gcode_print":
        material_cost = quantity_or_grams * pricing["base_rate_per_gram"]
        total_cost = material_cost + pricing["machine_hourly_rate"]
        return f"System: Quote successful. A {quantity_or_grams}g print costs {total_cost} PKR."
        
    else:
        return f"System: Error. I do not know how to calculate a price for '{item_type}'."

def log_manual_review(filepath: str, infill: str, color: str):
    """Saves the user's preferences for an un-sliced STL or 3MF file to a queue."""
    
    print(f"\n[Agent Activity] ⚡ Executing 'log_manual_review' -> File: {filepath}, Infill: {infill}, Color: {color}")
    
    try:
        with open("printing_queue.txt", "a") as f:
            f.write(f"--- NEW QUEUE ITEM ---\n")
            f.write(f"File:   {filepath}\n")
            f.write(f"Infill: {infill}\n")
            f.write(f"Color:  {color}\n\n")
            
        return "System: Success. The file and preferences have been securely logged."
    except Exception as e:
        return f"System: Failed to save to database. Error: {e}"
    
def chat_with_agent(user_message, chat_session):
    """Handles the agentic loop using Gemini's automatic tool execution."""
    try:
        response = chat_session.send_message(user_message)
        return response.text
    except Exception as e:
        return f"API Communication Error: {e}"

def start_server():
    HOST = '127.0.0.1'
    PORT = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    
    print(f"=== Agentic Server listening on {HOST}:{PORT} ===")

    while True:
        conn, addr = server_socket.accept()
        print(f"\n[+] Customer connected from {addr}")

        try:
            with open("prompts.txt", "r") as f:
                system_prompt = f.read().strip()
        except FileNotFoundError:
            print("[Warning] prompts.txt not found. Falling back to default prompt.")
            system_prompt = "You are a helpful 3D printing assistant."

        # Initialize the New Gemini Model Config
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
            tools=[calculate_quote, log_manual_review] 
        )
        
        chat_session = client.chats.create(
            model='gemini-3.5-flash',
            config=config
        )

        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break 
                
                user_message = data.decode('utf-8')
                print(f"Customer: {user_message}")

                # The Data Extraction Layer
                if user_message.startswith("[FILE_UPLOAD]"):
                    filepath = user_message.replace("[FILE_UPLOAD] ", "").strip()
                    
                    if filepath.endswith('.gcode'):
                        user_message = f"System override: The user uploaded a G-code file at {filepath}. It uses 15 grams of filament."
                    else:
                        user_message = f"System override: The user uploaded an un-sliced file at {filepath}. Find out what color and infill they want."

                # Route to the Brain
                ai_reply = chat_with_agent(user_message, chat_session)
                conn.send(ai_reply.encode('utf-8'))

        except Exception as e:
            print(f"Connection lost: {e}")
        finally:
            conn.close()
            print(f"[-] Customer disconnected. Waiting for new connection...")

if __name__ == "__main__":
    start_server()
