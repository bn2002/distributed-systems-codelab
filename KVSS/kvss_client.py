"""
Mini Key-Value Store Service (KVSS) - Client
Hệ phân tán - Interface Specification
"""

import socket
import sys
import threading
import time

class KVSSClient:
    def __init__(self, host='127.0.0.1', port=5050):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self):
        """Kết nối đến server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to KVSS server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Ngắt kết nối"""
        if self.socket:
            self.socket.close()
            self.connected = False
            print("Disconnected from server")
    
    def send_request(self, request):
        """Gửi request và nhận response"""
        if not self.connected:
            print("Not connected to server")
            return None
        
        try:
            # Gửi request
            self.socket.send(request.encode('utf-8'))
            
            # Nhận response
            response = self.socket.recv(1024).decode('utf-8')
            return response.strip()
        except Exception as e:
            print(f"Error sending request: {e}")
            return None
    
    def put(self, key, value):
        """Thực hiện lệnh PUT"""
        request = f"KV/1.0 PUT {key} {value}\n"
        print(f"Sending: {request.strip()}")
        response = self.send_request(request)
        if response:
            print(f"Response: {response}")
        return response
    
    def get(self, key):
        """Thực hiện lệnh GET"""
        request = f"KV/1.0 GET {key}\n"
        print(f"Sending: {request.strip()}")
        response = self.send_request(request)
        if response:
            print(f"Response: {response}")
        return response
    
    def delete(self, key):
        """Thực hiện lệnh DEL"""
        request = f"KV/1.0 DEL {key}\n"
        print(f"Sending: {request.strip()}")
        response = self.send_request(request)
        if response:
            print(f"Response: {response}")
        return response
    
    def stats(self):
        """Thực hiện lệnh STATS"""
        request = "KV/1.0 STATS\n"
        print(f"Sending: {request.strip()}")
        response = self.send_request(request)
        if response:
            print(f"Response: {response}")
        return response
    
    def quit(self):
        """Thực hiện lệnh QUIT"""
        request = "KV/1.0 QUIT\n"
        print(f"Sending: {request.strip()}")
        response = self.send_request(request)
        if response:
            print(f"Response: {response}")
        self.disconnect()
        return response

def interactive_mode():
    """Chế độ tương tác"""
    client = KVSSClient()
    
    if not client.connect():
        return
    
    print("\n=== KVSS Client Interactive Mode ===")
    print("Commands:")
    print("  PUT <key> <value>  - Store key-value pair")
    print("  GET <key>          - Retrieve value by key")
    print("  DEL <key>          - Delete key")
    print("  STATS              - Show server statistics")
    print("  QUIT               - Exit")
    print("  HELP               - Show this help")
    print("=" * 40)
    
    try:
        while True:
            try:
                command = input("\nKVSS> ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].upper()
                
                if cmd == "QUIT":
                    client.quit()
                    break
                elif cmd == "HELP":
                    print("Commands: PUT <key> <value>, GET <key>, DEL <key>, STATS, QUIT, HELP")
                elif cmd == "PUT":
                    if len(parts) >= 3:
                        key = parts[1]
                        value = " ".join(parts[2:])
                        client.put(key, value)
                    else:
                        print("Usage: PUT <key> <value>")
                elif cmd == "GET":
                    if len(parts) >= 2:
                        key = parts[1]
                        client.get(key)
                    else:
                        print("Usage: GET <key>")
                elif cmd == "DEL":
                    if len(parts) >= 2:
                        key = parts[1]
                        client.delete(key)
                    else:
                        print("Usage: DEL <key>")
                elif cmd == "STATS":
                    client.stats()
                else:
                    print("Unknown command. Type HELP for available commands.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                client.quit()
                break
            except EOFError:
                print("\nExiting...")
                client.quit()
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()

def batch_mode(commands):
    """Chế độ batch - thực hiện nhiều lệnh"""
    client = KVSSClient()
    
    if not client.connect():
        return
    
    for command in commands:
        print(f"\nExecuting: {command}")
        parts = command.split()
        cmd = parts[0].upper()
        
        if cmd == "PUT" and len(parts) >= 3:
            key = parts[1]
            value = " ".join(parts[2:])
            client.put(key, value)
        elif cmd == "GET" and len(parts) >= 2:
            key = parts[1]
            client.get(key)
        elif cmd == "DEL" and len(parts) >= 2:
            key = parts[1]
            client.delete(key)
        elif cmd == "STATS":
            client.stats()
        else:
            print(f"Invalid command: {command}")
    
    client.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Batch mode với các lệnh từ command line
        commands = sys.argv[1:]
        batch_mode(commands)
    else:
        # Interactive mode
        interactive_mode()
