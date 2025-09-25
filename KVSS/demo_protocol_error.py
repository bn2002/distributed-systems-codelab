#!/usr/bin/env python3
"""
Demo thực tế: Minh họa cách server xử lý lỗi giao thức
"""

import socket
import time
import sys

def demo_invalid_command():
    """Demo với command POTT thay vì PUT"""
    print("=" * 60)
    print("DEMO: Client gửi sai giao thức")
    print("Request: KV/1.0 POTT user42 Alice")
    print("=" * 60)
    
    try:
        # Kết nối đến server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5050))
        
        # Gửi request sai
        invalid_request = "KV/1.0 POTT user42 Alice\n"
        print(f"Client gửi: {invalid_request.strip()}")
        
        s.send(invalid_request.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
        
        print(f"Server phản hồi: {response.strip()}")
        
        # Phân tích
        print("\n--- PHÂN TÍCH ---")
        if "400 BAD_REQUEST" in response:
            print("✅ Server trả về 400 BAD_REQUEST")
            print("   → Command 'POTT' không tồn tại trong giao thức")
            print("   → Server xử lý lỗi một cách nhất quán")
        else:
            print("❌ Server phản hồi không đúng")
        
        s.close()
        
    except Exception as e:
        print(f"Lỗi kết nối: {e}")

def demo_multiple_errors():
    """Demo với nhiều loại lỗi khác nhau"""
    print("\n" + "=" * 60)
    print("DEMO: Các loại lỗi giao thức khác")
    print("=" * 60)
    
    error_cases = [
        ("KV/1.0 POTT user42 Alice", "Command sai: POTT"),
        ("KV/1.0 PUTT user42 Alice", "Command sai: PUTT"),
        ("KV/1.0 GETT user42", "Command sai: GETT"),
        ("KV/1.0 DELL user42", "Command sai: DELL"),
        ("KV/1.0 STATSS", "Command sai: STATSS"),
        ("KV/1.0 QUITT", "Command sai: QUITT"),
        ("KV/1.0 PUT user42 Alice extra", "Thừa tham số"),
        ("KV/1.0 PUT", "Thiếu tham số"),
        ("KV/1.0", "Thiếu command"),
    ]
    
    for request, description in error_cases:
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
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Lỗi: {e}")

def demo_interface_characteristics():
    """Minh họa các đặc điểm của Interface"""
    print("\n" + "=" * 60)
    print("ĐẶC ĐIỂM CỦA INTERFACE THỂ HIỆN QUA XỬ LÝ LỖI")
    print("=" * 60)
    
    print("""
1. TÍNH NHẤT QUÁN (Consistency):
   ✅ Mọi command sai đều trả về 400 BAD_REQUEST
   ✅ Response format luôn giống nhau: <status_code>
   ✅ Error codes được định nghĩa rõ ràng

2. TÍNH ỔN ĐỊNH (Stability):
   ✅ Server không crash khi nhận request sai
   ✅ Luôn trả về response hợp lệ
   ✅ Tiếp tục phục vụ các client khác

3. TÍNH DỰ ĐOÁN ĐƯỢC (Predictability):
   ✅ Client có thể dự đoán được response
   ✅ Error codes có ý nghĩa rõ ràng
   ✅ Behavior nhất quán qua các lần test

4. TÍNH BẢO MẬT (Security):
   ✅ Không tiết lộ thông tin nội bộ
   ✅ Không cho biết implementation details
   ✅ Chỉ trả về thông tin cần thiết

5. TÍNH TƯƠNG THÍCH (Compatibility):
   ✅ Interface không thay đổi khi server update
   ✅ Client cũ vẫn hoạt động với server mới
   ✅ Có thể mở rộng commands mới

6. TÍNH DEBUGGING (Debuggability):
   ✅ Error messages rõ ràng
   ✅ Logs chi tiết cho developer
   ✅ Dễ dàng trace lỗi từ client
    """)

def demo_comparison():
    """So sánh với các cách xử lý khác"""
    print("\n" + "=" * 60)
    print("SO SÁNH CÁC CÁCH XỬ LÝ LỖI")
    print("=" * 60)
    
    print("""
❌ CÁCH XỬ LÝ KHÔNG TỐT:

1. Không xử lý gì:
   ```python
   else:
       pass  # Client bị treo
   ```

2. Crash server:
   ```python
   else:
       raise Exception("Unknown command")
   ```

3. Tiết lộ thông tin nội bộ:
   ```python
   else:
       return f"500 ERROR: Command '{command}' not implemented"
   ```

✅ CÁCH XỬ LÝ TỐT (KVSS):

```python
else:
    self.stats['error_requests'] += 1
    status, data = "400 BAD_REQUEST", None
```

ƯU ĐIỂM:
- Nhất quán và có thể dự đoán được
- An toàn và ổn định
- Dễ debug và maintain
- Tuân thủ HTTP status codes
- Không tiết lộ thông tin nội bộ
    """)

def main():
    print("DEMO: Xử Lý Lỗi Giao Thức trong KVSS")
    print("Minh họa: Client gửi 'KV/1.0 POTT user42 Alice'")
    
    print("\nHướng dẫn:")
    print("1. Khởi động server: python3 kvss_server.py")
    print("2. Chạy demo: python3 demo_protocol_error.py")
    print("3. Quan sát cách server xử lý lỗi")
    
    input("\nNhấn Enter để tiếp tục...")
    
    # Demo chính
    demo_invalid_command()
    
    # Demo các lỗi khác
    demo_multiple_errors()
    
    # Minh họa đặc điểm Interface
    demo_interface_characteristics()
    
    # So sánh các cách xử lý
    demo_comparison()
    
    print("\n" + "=" * 60)
    print("KẾT LUẬN:")
    print("Việc server xử lý lỗi giao thức một cách nhất quán")
    print("thể hiện rõ các đặc điểm quan trọng của Interface:")
    print("- Tính nhất quán và ổn định")
    print("- Tính dự đoán được và bảo mật")
    print("- Tính tương thích và dễ debug")
    print("=" * 60)

if __name__ == "__main__":
    main()
