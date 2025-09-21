# Câu hỏi 1: Interface trong hệ thống phân tán là gì? Tại sao cần phải có Interface khi triển khai các dịch vụ?

Trong hệ phân tán, Interface (giao diện) là một bản "hợp đồng" định nghĩa rõ ràng các dịch vụ mà một server cung cấp, bao gồm tên các hàm và kiểu dữ liệu, nhưng không cho biết cách thức triển khai bên trong.

Nó cần thiết vì 3 lý do chính:
- Khả năng phối hợp (Interoperability): Cho phép client và server viết bằng các ngôn ngữ khác nhau có thể "nói chuyện" và làm việc được với nhau
- Tách biệt Client và Server: Client chỉ cần biết đến "hợp đồng" này mà không cần quan tâm server được cài đặt ra sao. Nhờ đó, server có thể được nâng cấp hoặc thay đổi thoải mái miễn là không phá vỡ "hợp đồng".
- Tính rõ ràng và trừu tượng: Interface che giấu sự phức tạp bên trong, giúp các nhà phát triển khác dễ dàng hiểu và sử dụng dịch vụ.


# Câu hỏi 2: Hãy giải thích ý nghĩa của mã trạng thái 201 CREATED, 204 NO_CONTENT và 404 NOT_FOUND trong giao thức KVSS

## 1. 201 CREATED
- Ý nghĩa: Thành công tạo mới một cặp key-value
- Khi nào sử dụng: Khi thực hiện lệnh PUT với một key chưa tồn tại trong store
- Ví dụ:
```  
Request: KV/1.0 PUT name John
Response: 201 CREATED
```

## 2. 204 NO_CONTENT
- Ý nghĩa: Thành công xóa một key (không có nội dung trả về)
- Khi nào sử dụng: Khi thực hiện lệnh DEL với một key tồn tại trong store
- Ví dụ
```
Request: KV/1.0 DEL name
Response: 204 NO_CONTENT
```
## 3. 404 NOT_FOUND
- Ý nghĩa: Không tìm thấy key được yêu cầu
- Khi nào sử dụng: Khi thực hiện lệnh GET với key không tồn tại hoặc Khi thực hiện lệnh DEL với key không tồn tại (idempotent operation)
- Ví dụ:
```
Request: KV/1.0 GET nonexistent_key
Response: 404 NOT_FOUND
```

# Câu hỏi 3. Trong bài lab KVSS, nếu client không tuân thủ quy ước Interface (ví dụ: thiếu version KV/1.0), server sẽ phản hồi thế nào? Tại sao phải quy định rõ ràng tình huống này?

Trong trường hợp này, server sẽ phản hồi:
```
Response: 426 UPGRADE_REQUIRED
```

Cần quy định rõ ràng là bởi: 
- Đảm bảo tính ổn định của hệ thống
- Hỗ trợ phát triển và bảo trì
- Thuận tiện trong việc debug
- Tạo nền tảng cho việc mở rộng trong tương lai
- Tính Tương Thích Ngược

# Câu hỏi 4. Quan sát một phiên làm việc qua Wireshark: hãy mô tả cách mà gói tin TCP được chia để truyền thông điệp theo “line-based protocol”.

## Phân tích Chi tiết TCP Packet Segmentation

### 1. TCP Handshake (3-way handshake)

**Packet 1: SYN**
```
Source: 127.0.0.1:random_port
Destination: 127.0.0.1:5050
Flags: SYN
```

**Packet 2: SYN-ACK**
```
Source: 127.0.0.1:5050
Destination: 127.0.0.1:random_port
Flags: SYN, ACK
```

**Packet 3: ACK**
```
Source: 127.0.0.1:random_port
Destination: 127.0.0.1:5050
Flags: ACK
```

### 2. Data Transmission - Line-based Protocol

#### Ví dụ: Request "KV/1.0 PUT name John\n"

**Phân tích trong Wireshark:**

1. **Packet 4: Client → Server**
   ```
   Protocol: TCP
   Source: 127.0.0.1:random_port
   Destination: 127.0.0.1:5050
   Length: 25 bytes
   Data: "KV/1.0 PUT name John\n"
   ```

2. **Packet 5: Server → Client (ACK)**
   ```
   Protocol: TCP
   Source: 127.0.0.1:5050
   Destination: 127.0.0.1:random_port
   Flags: ACK
   Length: 0 bytes (chỉ ACK)
   ```

3. **Packet 6: Server → Client (Response)**
   ```
   Protocol: TCP
   Source: 127.0.0.1:5050
   Destination: 127.0.0.1:random_port
   Length: 12 bytes
   Data: "201 CREATED\n"
   ```

### 3. Cách TCP Chia Nhỏ Thông Điệp

#### Trường hợp thông điệp ngắn (≤ MSS):
- **MSS (Maximum Segment Size)**: Thường là 1460 bytes cho Ethernet
- Thông điệp KVSS thường < 100 bytes → Gửi trong 1 packet duy nhất

#### Trường hợp thông điệp dài (> MSS):
Ví dụ với thông điệp dài: `KV/1.0 PUT bigkey [10000 ký tự A]\n`

**Packet 1:**
```
Data: "KV/1.0 PUT bigkey AAAA...AAAA" (1460 bytes)
Flags: PSH (Push)
```

**Packet 2:**
```
Data: "AAAA...AAAA" (1460 bytes)
Flags: PSH
```

**Packet 3:**
```
Data: "AAAA...AAAA\n" (còn lại)
Flags: PSH
```

### 4. Đặc điểm của Line-based Protocol

#### Ký tự kết thúc dòng (\n):
- **ASCII Code**: 0x0A (10 decimal)
- **Vai trò**: Đánh dấu kết thúc thông điệp
- **Trong Wireshark**: Hiển thị là `\n` trong phần Data

#### Buffering và Segmentation:
```
Client gửi: "KV/1.0 PUT name John\n"
TCP Layer: Chia thành segments nếu cần
Server nhận: "KV/1.0 PUT name John\n" (đầy đủ)
Application: Parse theo dòng (\n)
```

# Câu hỏi 5. Giả sử có một client viết sai giao thức (gửi KV/1.0 POTT user42 Alice). Server sẽ xử lý như thế nào? Kết quả này thể hiện đặc điểm gì của Interface?

## Trường hợp: Client gửi sai giao thức

**Request sai:** `KV/1.0 POTT user42 Alice`

**Command đúng:** `KV/1.0 PUT user42 Alice`

## Cách Server Xử Lý

### 1. Quy trình xử lý trong code

```python
def handle_request(self, request, client_addr):
    # Bước 1: Parse request
    version, command, args, error = self.parse_request(request)
    
    # Bước 2: Kiểm tra version (OK - "KV/1.0")
    if error:
        return error + "\n"
    
    # Bước 3: Kiểm tra command
    if command == "PUT":          # ❌ "POTT" không match
        # Xử lý PUT
    elif command == "GET":        # ❌ "POTT" không match  
        # Xử lý GET
    elif command == "DEL":        # ❌ "POTT" không match
        # Xử lý DEL
    elif command == "STATS":      # ❌ "POTT" không match
        # Xử lý STATS
    elif command == "QUIT":       # ❌ "POTT" không match
        # Xử lý QUIT
    else:
        # ❌ Command không hợp lệ
        self.stats['error_requests'] += 1
        status, data = "400 BAD_REQUEST", None
```

### 2. Kết quả xử lý

**Response từ server:** `400 BAD_REQUEST\n`

**Lý do:**
- Command "POTT" không nằm trong danh sách commands hợp lệ
- Server rơi vào trường hợp `else` → trả về `400 BAD_REQUEST`
- Được ghi vào log và thống kê lỗi

## Đặc điểm của Interface thể hiện qua xử lý lỗi

### 1. **Tính Nhất Quán (Consistency)**

**Thể hiện:**
- Mọi command không hợp lệ đều được xử lý giống nhau
- Response format luôn nhất quán: `<status_code>\n`
- Error code `400 BAD_REQUEST` được sử dụng cho tất cả lỗi cú pháp

**Ví dụ:**
```
KV/1.0 POTT user42 Alice  → 400 BAD_REQUEST
KV/1.0 PUTT user42 Alice  → 400 BAD_REQUEST  
KV/1.0 GETT user42        → 400 BAD_REQUEST
KV/1.0 INVALID            → 400 BAD_REQUEST
```

### 2. **Tính Ổn Định (Stability)**

**Thể hiện:**
- Server không crash khi nhận request sai
- Luôn trả về response hợp lệ
- Tiếp tục phục vụ các client khác bình thường

**Code minh họa:**
```python
try:
    # Xử lý request
    response = self.handle_request(request, client_addr)
    client_socket.send(response.encode('utf-8'))
except Exception as e:
    # Log lỗi nhưng không crash server
    self.logger.error(f"Error handling client: {e}")
```

### 3. **Tính Dự Đoán Được (Predictability)**

**Thể hiện:**
- Client có thể dự đoán được response cho mỗi loại lỗi
- Error codes có ý nghĩa rõ ràng và được document
- Behavior nhất quán qua các lần test

**Bảng dự đoán:**
| Lỗi | Response Code | Ý nghĩa |
|-----|---------------|---------|
| Command sai | 400 BAD_REQUEST | Cú pháp không đúng |
| Version sai | 426 UPGRADE_REQUIRED | Version không hỗ trợ |
| Thiếu tham số | 400 BAD_REQUEST | Request không đầy đủ |
| Thừa tham số | 400 BAD_REQUEST | Request có tham số thừa |

### 4. **Tính Bảo Mật (Security)**

**Thể hiện:**
- Không tiết lộ thông tin nội bộ của server
- Không cho biết server được implement như thế nào
- Chỉ trả về thông tin cần thiết cho client

**Ví dụ:**
```
❌ Không trả về: "Command POTT not implemented yet"
✅ Trả về: "400 BAD_REQUEST"
```

### 5. **Tính Tương Thích (Compatibility)**

**Thể hiện:**
- Interface không thay đổi khi server được update
- Client cũ vẫn hoạt động với server mới
- Có thể mở rộng thêm commands mới mà không phá vỡ tương thích

**Ví dụ mở rộng:**
```python
# Thêm command mới
elif command == "UPDATE":  # Command mới
    # Xử lý UPDATE
elif command == "LIST":    # Command mới
    # Xử lý LIST
else:
    # Vẫn xử lý command không hợp lệ như cũ
    status, data = "400 BAD_REQUEST", None
```