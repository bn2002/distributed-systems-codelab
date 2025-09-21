# Mini Key-Value Store Service (KVSS)

## Mô tả
Đây là bài thực hành môn **Hệ phân tán** về khái niệm **Interface** trong các hệ thống phân tán. Dự án xây dựng một dịch vụ lưu trữ key-value đơn giản với giao thức TCP text-based.

## Kiến trúc
- **Server**: TCP server xử lý đa client với threading
- **Client**: Command-line interface để tương tác với server
- **Protocol**: Text-based line protocol với UTF-8 encoding
- **Port**: 127.0.0.1:5050 (mặc định)

## Interface Specification

### Kết nối
- **Protocol**: TCP
- **Host**: 127.0.0.1
- **Port**: 5050
- **Encoding**: UTF-8
- **Message Format**: Text lines ending with `\n` (LF)

### Request Format
```
<version> <command> [<args>]
```

**BNF Grammar:**
```
<version> ::= "KV/1.0"
<command> ::= "PUT" | "GET" | "DEL" | "STATS" | "QUIT"
<args>    ::= <key> [ " " <value> ]
<key>     ::= 1*VCHAR (không chứa khoảng trắng)
<value>   ::= 1*VCHAR (tồn tại khi PUT)
```

### Response Codes
- `200 OK [data]` - Thành công
- `201 CREATED` - Tạo mới thành công (PUT)
- `204 NO_CONTENT` - Xóa thành công (DEL)
- `400 BAD_REQUEST` - Lỗi cú pháp/thiếu tham số
- `404 NOT_FOUND` - Không tìm thấy key
- `426 UPGRADE_REQUIRED` - Version không đúng
- `500 SERVER_ERROR` - Lỗi server

## Cài đặt và Chạy

### Yêu cầu hệ thống
- Python 3.6+
- Linux/Ubuntu
- netcat
- telnet

### 1. Chạy Server
```bash
python3 kvss_server.py
```

Server sẽ:
- Chạy trên port 5050
- Ghi log vào file `kvss_server.log`
- Hỗ trợ đa client với threading
- Lưu trữ dữ liệu trong memory

### 2. Chạy Client (Interactive Mode)
```bash
python3 kvss_client.py
```

### 3. Chạy Client (Batch Mode)
```bash
python3 kvss_client.py PUT name John GET name DEL name STATS
```

## Test Cases

### Chạy Test Suite Tự động
```bash
# Chạy tất cả test cases
python3 test_cases.py

# Hoặc sử dụng script bash
./run_tests.sh
```

### Test Cases bao gồm:

#### ✅ Test Cases Hợp lệ:
1. **PUT hợp lệ - tạo mới**: `KV/1.0 PUT name John` → `201 CREATED`
2. **PUT hợp lệ - cập nhật**: `KV/1.0 PUT name Jane` → `200 OK`
3. **GET hợp lệ - key tồn tại**: `KV/1.0 GET name` → `200 OK Jane`
4. **GET hợp lệ - key không tồn tại**: `KV/1.0 GET nonexistent` → `404 NOT_FOUND`
5. **DEL hợp lệ - key tồn tại**: `KV/1.0 DEL name` → `204 NO_CONTENT`
6. **DEL hợp lệ - key không tồn tại**: `KV/1.0 DEL name` → `404 NOT_FOUND` (idempotent)
7. **STATS hợp lệ**: `KV/1.0 STATS` → `200 OK keys=X uptime=Ys served=Z`
8. **QUIT hợp lệ**: `KV/1.0 QUIT` → `200 OK`

#### ❌ Test Cases Lỗi:
9. **Thiếu version**: `PUT name John` → `426 UPGRADE_REQUIRED`
10. **Version sai**: `KV/2.0 PUT name John` → `426 UPGRADE_REQUIRED`
11. **PUT thiếu value**: `KV/1.0 PUT name` → `400 BAD_REQUEST`
12. **GET thiếu key**: `KV/1.0 GET` → `400 BAD_REQUEST`
13. **Command không hợp lệ**: `KV/1.0 INVALID` → `400 BAD_REQUEST`
14. **Key chứa khoảng trắng**: `KV/1.0 PUT my key value` → `400 BAD_REQUEST`
15. **PUT với value dài**: Test với value 1000 ký tự

## Test thủ công với nc/telnet

### Sử dụng netcat (nc)
```bash
# Kết nối đến server
nc 127.0.0.1 5050

# Các lệnh test:
KV/1.0 PUT testkey testvalue
KV/1.0 GET testkey
KV/1.0 DEL testkey
KV/1.0 STATS
KV/1.0 QUIT
```

### Sử dụng telnet
```bash
telnet 127.0.0.1 5050
```

### Test với curl
```bash
echo "KV/1.0 PUT testkey testvalue" | nc 127.0.0.1 5050
echo "KV/1.0 GET testkey" | nc 127.0.0.1 5050
echo "KV/1.0 STATS" | nc 127.0.0.1 5050
```

## Quan sát Traffic với Wireshark

### 1. Cài đặt Wireshark
```bash
sudo apt update
sudo apt install wireshark
```

### 2. Capture Traffic
1. Mở Wireshark
2. Chọn interface `lo` (loopback) hoặc `any`
3. Bắt đầu capture
4. Chạy các test cases
5. Dừng capture và quan sát packets

### 3. Filter cho KVSS
Sử dụng filter: `tcp.port == 5050`

### 4. Quan sát Protocol
- **TCP Handshake**: SYN, SYN-ACK, ACK
- **Data Exchange**: Text-based protocol
- **Connection Close**: FIN, FIN-ACK, ACK

## Cấu trúc Files

```
KVSS/
├── kvss_server.py          # Server implementation
├── kvss_client.py          # Client implementation  
├── test_cases.py           # Automated test suite
├── run_tests.sh           # Bash test script
├── manual_test_guide.md   # Hướng dẫn test thủ công
├── README.md              # File này
└── logs/
    └── server.log         # Server logs (tự tạo)
```

## Tính năng nổi bật

### Server Features:
- ✅ **Multi-threading**: Hỗ trợ nhiều client đồng thời
- ✅ **Logging**: Ghi log chi tiết mọi request/response
- ✅ **Error Handling**: Xử lý đầy đủ các trường hợp lỗi
- ✅ **Idempotent Operations**: DEL và GET đảm bảo idempotent
- ✅ **Memory Storage**: Lưu trữ key-value trong memory

### Client Features:
- ✅ **Interactive Mode**: Giao diện dòng lệnh thân thiện
- ✅ **Batch Mode**: Chạy nhiều lệnh cùng lúc
- ✅ **Error Display**: Hiển thị response rõ ràng
- ✅ **Connection Management**: Tự động kết nối/ngắt kết nối

### Protocol Features:
- ✅ **Version Control**: Hỗ trợ versioning (KV/1.0)
- ✅ **Text-based**: Dễ đọc và debug
- ✅ **UTF-8 Support**: Hỗ trợ Unicode
- ✅ **Line Protocol**: Mỗi message kết thúc bằng `\n`

## Troubleshooting

### Server không khởi động được
```bash
# Kiểm tra port có bị chiếm không
netstat -tulpn | grep 5050

# Kiểm tra log
cat kvss_server.log
```

### Client không kết nối được
```bash
# Kiểm tra server có chạy không
ps aux | grep kvss_server

# Test kết nối
telnet 127.0.0.1 5050
```

### Test cases fail
```bash
# Chạy test với verbose
python3 test_cases.py

# Kiểm tra server log
tail -f kvss_server.log
```

## Kết luận

Dự án này minh họa rõ ràng vai trò của **Interface** trong hệ thống phân tán:

1. **Tính thống nhất**: Cả client và server đều tuân thủ cùng một protocol
2. **Khả năng tương thích**: Có thể thay thế client/server mà không ảnh hưởng đến chức năng
3. **Dễ mở rộng**: Có thể thêm commands mới mà không phá vỡ tương thích ngược
4. **Debugging**: Text-based protocol dễ quan sát và debug
5. **Testing**: Interface rõ ràng giúp viết test cases dễ dàng