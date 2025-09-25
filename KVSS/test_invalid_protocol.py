#!/usr/bin/env python3
"""
Test case để minh họa cách server xử lý client gửi sai giao thức
Ví dụ: KV/1.0 POTT user42 Alice (command sai)
"""

import socket
import time
import sys

def test_invalid_command():
    """Test với command không hợp lệ: POTT thay vì PUT"""
    print("=== Test Invalid Command: POTT ===")
    
    try:
        # Kết nối đến server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5050))
        
        # Gửi request sai giao thức
        invalid_request = "KV/1.0 POTT user42 Alice\n"
        print(f"Gửi request sai: {invalid_request.strip()}")
        
        s.send(invalid_request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        
        print(f"Server phản hồi: {response.strip()}")
        
        # Phân tích response
        if "400 BAD_REQUEST" in response:
            print("✅ Server trả về 400 BAD_REQUEST - Đúng!")
            print("   Lý do: Command 'POTT' không tồn tại trong giao thức")
        else:
            print("❌ Server phản hồi không đúng")
        
        s.close()
        return response.strip()
        
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return None

def test_other_invalid_cases():
    """Test các trường hợp sai giao thức khác"""
    print("\n=== Test Các Trường Hợp Sai Giao Thức Khác ===")
    
    test_cases = [
        ("KV/1.0 POTT user42 Alice", "Command sai: POTT"),
        ("KV/1.0 PUTT user42 Alice", "Command sai: PUTT"), 
        ("KV/1.0 GETT user42", "Command sai: GETT"),
        ("KV/1.0 DELL user42", "Command sai: DELL"),
        ("KV/1.0 STATSS", "Command sai: STATSS"),
        ("KV/1.0 QUITT", "Command sai: QUITT"),
        ("KV/1.0 PUT user42 Alice extra", "Thừa tham số"),
        ("KV/1.0 PUT", "Thiếu tham số"),
        ("KV/1.0", "Thiếu command"),
        ("KV/1.0 PUT user42", "PUT thiếu value"),
        ("KV/1.0 GET", "GET thiếu key"),
    ]
    
    for request, description in test_cases:
        print(f"\n--- {description} ---")
        print(f"Request: {request}")
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 5050))
            
            s.send((request + "\n").encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            
            print(f"Response: {response.strip()}")
            
            # Phân tích loại lỗi
            if "400 BAD_REQUEST" in response:
                print("   → Lỗi cú pháp/command không hợp lệ")
            elif "426 UPGRADE_REQUIRED" in response:
                print("   → Lỗi version")
            else:
                print("   → Lỗi khác")
            
            s.close()
            time.sleep(0.1)  # Delay nhỏ giữa các test
            
        except Exception as e:
            print(f"Lỗi: {e}")

def analyze_server_behavior():
    """Phân tích cách server xử lý lỗi giao thức"""
    print("\n=== Phân Tích Cách Server Xử Lý Lỗi Giao Thức ===")
    
    print("""
1. QUY TRÌNH XỬ LÝ LỖI CỦA SERVER:
   ┌─────────────────┐
   │  Nhận request  │
   └─────────┬───────┘
             │
   ┌─────────▼───────┐
   │  Parse request  │
   │  (version, cmd, │
   │   args)         │
   └─────────┬───────┘
             │
   ┌─────────▼───────┐
   │ Kiểm tra version│
   │ ≠ "KV/1.0"      │
   └─────────┬───────┘
             │
   ┌─────────▼───────┐
   │ Kiểm tra command│
   │ ∉ {PUT,GET,DEL, │
   │   STATS,QUIT}   │
   └─────────┬───────┘
             │
   ┌─────────▼───────┐
   │ Trả về 400      │
   │ BAD_REQUEST     │
   └─────────────────┘

2. CÁC LOẠI LỖI ĐƯỢC XỬ LÝ:
   - Command không tồn tại → 400 BAD_REQUEST
   - Thiếu tham số → 400 BAD_REQUEST  
   - Thừa tham số → 400 BAD_REQUEST
   - Version sai → 426 UPGRADE_REQUIRED
   - Cú pháp sai → 400 BAD_REQUEST

3. ĐẶC ĐIỂM CỦA INTERFACE:
   - Tính nhất quán: Server luôn trả về error code rõ ràng
   - Tính ổn định: Không crash khi nhận request sai
   - Tính dự đoán được: Mỗi loại lỗi có response code riêng
   - Tính bảo mật: Không tiết lộ thông tin nội bộ
    """)

def demonstrate_interface_characteristics():
    """Minh họa các đặc điểm của Interface"""
    print("\n=== Đặc Điểm Của Interface Thể Hiện Qua Xử Lý Lỗi ===")
    
    print("""
1. TÍNH NHẤT QUÁN (Consistency):
   - Mọi lỗi giao thức đều được xử lý theo cùng một cách
   - Response format luôn giống nhau: <status_code> <message>
   - Error codes được định nghĩa rõ ràng trong specification

2. TÍNH ỔN ĐỊNH (Stability):
   - Server không crash khi nhận request sai
   - Luôn trả về response hợp lệ
   - Tiếp tục phục vụ các client khác

3. TÍNH DỰ ĐOÁN ĐƯỢC (Predictability):
   - Client có thể dự đoán được response cho mỗi loại lỗi
   - Error codes có ý nghĩa rõ ràng
   - Behavior nhất quán qua các lần test

4. TÍNH BẢO MẬT (Security):
   - Không tiết lộ thông tin nội bộ của server
   - Không cho biết server được implement như thế nào
   - Chỉ trả về thông tin cần thiết

5. TÍNH TƯƠNG THÍCH (Compatibility):
   - Interface không thay đổi khi server được update
   - Client cũ vẫn hoạt động với server mới
   - Có thể mở rộng thêm commands mới

6. TÍNH DEBUGGING (Debuggability):
   - Error messages rõ ràng giúp debug
   - Logs chi tiết cho developer
   - Dễ dàng trace lỗi từ client
    """)

def main():
    print("=" * 60)
    print("DEMO: Xử Lý Lỗi Giao Thức trong KVSS")
    print("=" * 60)
    
    print("Hướng dẫn:")
    print("1. Khởi động server: python3 kvss_server.py")
    print("2. Chạy script này: python3 test_invalid_protocol.py")
    print("3. Quan sát cách server xử lý các lỗi giao thức")
    print("=" * 60)
    
    # Test case chính
    test_invalid_command()
    
    # Test các trường hợp khác
    test_other_invalid_cases()
    
    # Phân tích
    analyze_server_behavior()
    
    # Minh họa đặc điểm Interface
    demonstrate_interface_characteristics()
    
    print("\n" + "=" * 60)
    print("KẾT LUẬN:")
    print("Việc server xử lý lỗi giao thức một cách nhất quán và")
    print("có thể dự đoán được thể hiện rõ các đặc điểm quan trọng")
    print("của Interface trong hệ thống phân tán.")
    print("=" * 60)

if __name__ == "__main__":
    main()
