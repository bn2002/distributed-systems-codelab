#!/usr/bin/env python3
"""
Demo script để test KVSS và tạo traffic cho Wireshark analysis
"""

import socket
import time
import sys
import threading

def test_short_messages():
    """Test với thông điệp ngắn"""
    print("=== Test Short Messages ===")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5050))
        
        # Test PUT
        request = "KV/1.0 PUT name John\n"
        print(f"Sending: {request.strip()}")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")
        
        # Test GET
        request = "KV/1.0 GET name\n"
        print(f"Sending: {request.strip()}")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")
        
        # Test STATS
        request = "KV/1.0 STATS\n"
        print(f"Sending: {request.strip()}")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")
        
        # Test QUIT
        request = "KV/1.0 QUIT\n"
        print(f"Sending: {request.strip()}")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")
        
        s.close()
        
    except Exception as e:
        print(f"Error: {e}")

def test_long_messages():
    """Test với thông điệp dài"""
    print("\n=== Test Long Messages ===")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5050))
        
        # Tạo value dài 2000 ký tự
        long_value = 'A' * 2000
        request = f"KV/1.0 PUT bigkey {long_value}\n"
        
        print(f"Sending long message ({len(request)} bytes)...")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")
        
        # Test GET
        request = "KV/1.0 GET bigkey\n"
        print(f"Sending: {request.strip()}")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response length: {len(response)} chars")
        print(f"Response preview: {response[:50]}...")
        
        s.close()
        
    except Exception as e:
        print(f"Error: {e}")

def test_multiple_requests():
    """Test nhiều requests liên tiếp"""
    print("\n=== Test Multiple Requests ===")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5050))
        
        for i in range(5):
            # PUT
            request = f"KV/1.0 PUT key{i} value{i}\n"
            print(f"Request {i+1}: {request.strip()}")
            s.send(request.encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            print(f"Response: {response.strip()}")
            
            time.sleep(0.1)  # Delay nhỏ để quan sát trong Wireshark
        
        # STATS
        request = "KV/1.0 STATS\n"
        print(f"Final request: {request.strip()}")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")
        
        s.close()
        
    except Exception as e:
        print(f"Error: {e}")

def test_error_cases():
    """Test các trường hợp lỗi"""
    print("\n=== Test Error Cases ===")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5050))
        
        # Test thiếu version
        request = "PUT name John\n"
        print(f"Test 1 - Missing version: {request.strip()}")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")
        
        # Test version sai
        request = "KV/2.0 PUT name John\n"
        print(f"Test 2 - Wrong version: {request.strip()}")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")
        
        # Test PUT thiếu value
        request = "KV/1.0 PUT name\n"
        print(f"Test 3 - Missing value: {request.strip()}")
        s.send(request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")
        
        s.close()
        
    except Exception as e:
        print(f"Error: {e}")

def test_concurrent_clients():
    """Test nhiều client đồng thời"""
    print("\n=== Test Concurrent Clients ===")
    
    def client_worker(client_id):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 5050))
            
            # Mỗi client thực hiện 3 operations
            for i in range(3):
                request = f"KV/1.0 PUT client{client_id}_key{i} value{i}\n"
                print(f"Client {client_id}: {request.strip()}")
                s.send(request.encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                print(f"Client {client_id} response: {response.strip()}")
                time.sleep(0.2)
            
            s.close()
            
        except Exception as e:
            print(f"Client {client_id} error: {e}")
    
    # Tạo 3 client threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=client_worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Đợi tất cả threads hoàn thành
    for t in threads:
        t.join()

def main():
    print("KVSS Wireshark Demo Script")
    print("=" * 50)
    print("Hướng dẫn:")
    print("1. Khởi động server: python3 kvss_server.py")
    print("2. Mở Wireshark và bắt đầu capture với filter: tcp.port == 5050")
    print("3. Chạy script này: python3 demo_wireshark.py")
    print("4. Quan sát packets trong Wireshark")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "all"
    
    if test_type == "short" or test_type == "all":
        test_short_messages()
    
    if test_type == "long" or test_type == "all":
        test_long_messages()
    
    if test_type == "multiple" or test_type == "all":
        test_multiple_requests()
    
    if test_type == "error" or test_type == "all":
        test_error_cases()
    
    if test_type == "concurrent" or test_type == "all":
        test_concurrent_clients()
    
    print("\nDemo completed! Check Wireshark for packet analysis.")

if __name__ == "__main__":
    main()
