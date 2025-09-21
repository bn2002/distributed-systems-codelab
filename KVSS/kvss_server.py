"""
Mini Key-Value Store Service (KVSS) - Server
"""

import socket
import threading
import time
import sys
from datetime import datetime
import logging

class KVSSServer:
    def __init__(self, host='127.0.0.1', port=5050):
        self.host = host
        self.port = port
        self.kv_store = {}  # Dictionary để lưu trữ key-value
        self.stats = {
            'total_requests': 0,
            'put_requests': 0,
            'get_requests': 0,
            'del_requests': 0,
            'stats_requests': 0,
            'error_requests': 0
        }
        self.start_time = time.time()  # Thời gian khởi động server
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kvss_server.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_request(self, client_addr, request, response):
        """Ghi log request/response với timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.logger.info(f"[{timestamp}] {client_addr} -> {request.strip()}")
        self.logger.info(f"[{timestamp}] {client_addr} <- {response.strip()}")
    
    def parse_request(self, request):
        """Parse request theo format KV/1.0 <command> [args]"""
        try:
            parts = request.strip().split(' ', 2)
            if len(parts) < 2:
                return None, None, None, "400 BAD_REQUEST"
            
            version = parts[0]
            command = parts[1]
            args = parts[2] if len(parts) > 2 else ""
            
            # Kiểm tra version
            if version != "KV/1.0":
                return None, None, None, "426 UPGRADE_REQUIRED"
            
            return version, command, args, None
        except Exception as e:
            return None, None, None, "400 BAD_REQUEST"
    
    def handle_put(self, args):
        """Xử lý lệnh PUT key value"""
        try:
            # Kiểm tra args có chứa ít nhất 2 phần (key và value)
            parts = args.split(' ', 1)
            if len(parts) != 2:
                return "400 BAD_REQUEST", None
            
            key, value = parts
            if not key or not value:
                return "400 BAD_REQUEST", None
            
            # Kiểm tra key không chứa khoảng trắng
            if (' ' in key) or (' ' in value):
                return "400 BAD_REQUEST", None
            
            is_new = key not in self.kv_store
            self.kv_store[key] = value
            
            if is_new:
                return "201 CREATED", None
            else:
                return "200 OK", None
                
        except Exception as e:
            return "500 SERVER_ERROR", None
    
    def handle_get(self, args):
        """Xử lý lệnh GET key"""
        try:
            key = args.strip()
            if not key:
                return "400 BAD_REQUEST", None
            
            if key in self.kv_store:
                return "200 OK", self.kv_store[key]
            else:
                return "404 NOT_FOUND", None
                
        except Exception as e:
            return "500 SERVER_ERROR", None
    
    def handle_del(self, args):
        """Xử lý lệnh DEL key"""
        try:
            key = args.strip()
            if not key:
                return "400 BAD_REQUEST", None
            
            if key in self.kv_store:
                del self.kv_store[key]
                return "204 NO_CONTENT", None
            else:
                return "404 NOT_FOUND", None
                
        except Exception as e:
            return "500 SERVER_ERROR", None
    
    def handle_stats(self, args):
        """Xử lý lệnh STATS"""
        try:
            # Tính uptime
            uptime_seconds = int(time.time() - self.start_time)
            uptime_str = f"{uptime_seconds}s"
            
            # Format: OK keys=0 uptime=12s served=7
            stats_data = f"OK keys={len(self.kv_store)} uptime={uptime_str} served={self.stats['total_requests']}"
            
            return "200", stats_data
        except Exception as e:
            return "500 SERVER_ERROR", None
    
    def handle_request(self, request, client_addr):
        """Xử lý một request"""
        self.stats['total_requests'] += 1
        
        version, command, args, error = self.parse_request(request)
        
        if error:
            self.stats['error_requests'] += 1
            response = error
            self.log_request(client_addr, request, response)
            return response + "\n"
        
        # Xử lý các lệnh
        if command == "PUT":
            self.stats['put_requests'] += 1
            status, data = self.handle_put(args)
        elif command == "GET":
            self.stats['get_requests'] += 1
            status, data = self.handle_get(args)
        elif command == "DEL":
            self.stats['del_requests'] += 1
            status, data = self.handle_del(args)
        elif command == "STATS":
            self.stats['stats_requests'] += 1
            status, data = self.handle_stats(args)
        elif command == "QUIT":
            response = "200 OK"
            self.log_request(client_addr, request, response)
            return response + "\n"
        else:
            self.stats['error_requests'] += 1
            status, data = "400 BAD_REQUEST", None
        
        # Tạo response
        if data:
            response = f"{status} {data}"
        else:
            response = status
        
        self.log_request(client_addr, request, response)
        return response + "\n"
    
    def handle_client(self, client_socket, client_addr):
        """Xử lý một client connection"""
        self.logger.info(f"Client connected: {client_addr}")
        
        try:
            while True:
                # Nhận request
                request = client_socket.recv(1024).decode('utf-8')
                if not request:
                    break
                
                # Xử lý request
                response = self.handle_request(request, client_addr)
                
                # Gửi response
                client_socket.send(response.encode('utf-8'))
                
                # Kiểm tra QUIT
                if request.strip().endswith("QUIT"):
                    break
                    
        except Exception as e:
            self.logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            client_socket.close()
            self.logger.info(f"Client disconnected: {client_addr}")
    
    def start(self):
        """Khởi động server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.logger.info(f"KVSS Server started on {self.host}:{self.port}")
            self.logger.info("Waiting for connections...")
            
            while True:
                client_socket, client_addr = server_socket.accept()
                
                # Tạo thread mới cho mỗi client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            self.logger.info("Server shutting down...")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = KVSSServer()
    server.start()
