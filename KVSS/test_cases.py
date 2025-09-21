"""
Test Cases cho Mini Key-Value Store Service (KVSS)
Hệ phân tán - Interface Specification
"""

import subprocess
import time
import socket
import threading

class KVSSClient:
    """Simple client for testing"""
    def __init__(self, host='127.0.0.1', port=5050):
        self.host = host
        self.port = port
    
    def send_request(self, request):
        """Gửi request và nhận response"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.send(request.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            sock.close()
            return response.strip()
        except Exception as e:
            return f"ERROR: {e}"

def run_test_case(test_name, request, expected_status, expected_data=None):
    """Chạy một test case"""
    print(f"\n{'='*60}")
    print(f"TEST CASE: {test_name}")
    print(f"{'='*60}")
    
    client = KVSSClient()
    response = client.send_request(request)
    
    print(f"Request:  {request.strip()}")
    print(f"Response: {response}")
    
    # Kiểm tra status code
    if expected_status in response:
        print("✓ Status code: PASS")
        status_ok = True
    else:
        print(f"✗ Status code: FAIL (expected {expected_status})")
        status_ok = False
    
    # Kiểm tra data nếu có
    data_ok = True
    if expected_data is not None:
        if expected_data in response:
            print("✓ Data: PASS")
        else:
            print(f"✗ Data: FAIL (expected {expected_data})")
            data_ok = False
    
    overall_result = "PASS" if (status_ok and data_ok) else "FAIL"
    print(f"\nResult: {overall_result}")
    return overall_result == "PASS"

def start_server():
    """Khởi động server trong background"""
    try:
        process = subprocess.Popen(['python3', 'kvss_server.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        time.sleep(2)  # Đợi server khởi động
        return process
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def main():
    """Chạy tất cả test cases"""
    print("Starting KVSS Test Suite")
    print("="*60)
    
    # Khởi động server
    server_process = start_server()
    if not server_process:
        print("Cannot start server. Exiting.")
        return
    
    try:
        # Đợi server khởi động hoàn toàn
        time.sleep(3)
        
        test_results = []
        
        # Test Case 1: PUT hợp lệ - tạo mới
        result1 = run_test_case(
            "PUT hợp lệ - tạo mới key",
            "KV/1.0 PUT name John\n",
            "201 CREATED"
        )
        test_results.append(("PUT hợp lệ - tạo mới", result1))
        
        # Test Case 2: PUT hợp lệ - cập nhật
        result2 = run_test_case(
            "PUT hợp lệ - cập nhật key",
            "KV/1.0 PUT name Jane\n",
            "200 OK"
        )
        test_results.append(("PUT hợp lệ - cập nhật", result2))
        
        # Test Case 3: GET hợp lệ - key tồn tại
        result3 = run_test_case(
            "GET hợp lệ - key tồn tại",
            "KV/1.0 GET name\n",
            "200 OK",
            "Jane"
        )
        test_results.append(("GET hợp lệ - key tồn tại", result3))
        
        # Test Case 4: GET hợp lệ - key không tồn tại
        result4 = run_test_case(
            "GET hợp lệ - key không tồn tại",
            "KV/1.0 GET nonexistent\n",
            "404 NOT_FOUND"
        )
        test_results.append(("GET hợp lệ - key không tồn tại", result4))
        
        # Test Case 5: DEL hợp lệ - key tồn tại
        result5 = run_test_case(
            "DEL hợp lệ - key tồn tại",
            "KV/1.0 DEL name\n",
            "204 NO_CONTENT"
        )
        test_results.append(("DEL hợp lệ - key tồn tại", result5))
        
        # Test Case 6: DEL hợp lệ - key không tồn tại (idempotent)
        result6 = run_test_case(
            "DEL hợp lệ - key không tồn tại (idempotent)",
            "KV/1.0 DEL name\n",
            "404 NOT_FOUND"
        )
        test_results.append(("DEL hợp lệ - key không tồn tại", result6))
        
        # Test Case 7: STATS hợp lệ
        result7 = run_test_case(
            "STATS hợp lệ",
            "KV/1.0 STATS\n",
            "200 OK",
            "keys="
        )
        test_results.append(("STATS hợp lệ", result7))
        
        # Test Case 8: Lỗi - thiếu version
        result8 = run_test_case(
            "Lỗi - thiếu version",
            "PUT name John\n",
            "426 UPGRADE_REQUIRED"
        )
        test_results.append(("Lỗi - thiếu version", result8))
        
        # Test Case 9: Lỗi - version sai
        result9 = run_test_case(
            "Lỗi - version sai",
            "KV/2.0 PUT name John\n",
            "426 UPGRADE_REQUIRED"
        )
        test_results.append(("Lỗi - version sai", result9))
        
        # Test Case 10: Lỗi - PUT thiếu value
        result10 = run_test_case(
            "Lỗi - PUT thiếu value",
            "KV/1.0 PUT name\n",
            "400 BAD_REQUEST"
        )
        test_results.append(("Lỗi - PUT thiếu value", result10))
        
        # Test Case 11: Lỗi - GET thiếu key
        result11 = run_test_case(
            "Lỗi - GET thiếu key",
            "KV/1.0 GET\n",
            "400 BAD_REQUEST"
        )
        test_results.append(("Lỗi - GET thiếu key", result11))
        
        # Test Case 12: Lỗi - command không hợp lệ
        result12 = run_test_case(
            "Lỗi - command không hợp lệ",
            "KV/1.0 INVALID\n",
            "400 BAD_REQUEST"
        )
        test_results.append(("Lỗi - command không hợp lệ", result12))
        
        # Test Case 13: Test với key chứa khoảng trắng (không hợp lệ)
        result13 = run_test_case(
            "Lỗi - key chứa khoảng trắng",
            "KV/1.0 PUT my key value\n",
            "400 BAD_REQUEST"
        )
        test_results.append(("Lỗi - key chứa khoảng trắng", result13))
        
        # Test Case 14: Test với value dài
        long_value = "A" * 1000
        result14 = run_test_case(
            "PUT với value dài",
            f"KV/1.0 PUT longkey {long_value}\n",
            "201 CREATED"
        )
        test_results.append(("PUT với value dài", result14))
        
        # Test Case 15: QUIT command
        result15 = run_test_case(
            "QUIT command",
            "KV/1.0 QUIT\n",
            "200 OK"
        )
        test_results.append(("QUIT command", result15))
        
        # Tổng kết kết quả
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "PASS" if result else "FAIL"
            print(f"{test_name:<40} {status}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{total} tests passed")
        print(f"Success rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("All tests passed!")
        else:
            print("Some tests failed!")
            
    finally:
        # Dừng server
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
