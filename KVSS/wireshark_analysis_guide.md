# Hướng dẫn phân tích TCP Line-based Protocol với Wireshark

## Tổng quan về Line-based Protocol trong KVSS

Trong project KVSS này, giao thức sử dụng **line-based protocol** với các đặc điểm:
- Mỗi thông điệp kết thúc bằng ký tự `\n` (LF - Line Feed)
- Sử dụng TCP để đảm bảo thứ tự và độ tin cậy
- Encoding UTF-8
- Format: `<version> <command> [<args>]\n`

## Cài đặt và Chuẩn bị

### 1. Cài đặt Wireshark
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install wireshark

# Windows: Tải từ https://www.wireshark.org/
```

### 2. Cấu hình Wireshark
- Mở Wireshark với quyền administrator (Windows) hoặc sudo (Linux)
- Chọn interface phù hợp:
  - **Windows**: Chọn "Loopback" hoặc "Ethernet"
  - **Linux**: Chọn "lo" (loopback) hoặc "any"

## Các bước Capture và Phân tích

### Bước 1: Bắt đầu Capture
1. Mở Wireshark
2. Chọn interface `lo` (loopback) hoặc `any`
3. Click "Start capturing" (nút cá mập)
4. Áp dụng filter: `tcp.port == 5050`

### Bước 2: Chạy Test Cases
Mở terminal mới và chạy:

```bash
# Terminal 1: Khởi động server
python3 kvss_server.py

# Terminal 2: Chạy client test
python3 kvss_client.py PUT name John GET name STATS QUIT
```

### Bước 3: Dừng Capture
Sau khi test xong, click "Stop capturing" trong Wireshark.

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

## Các Filter Wireshark Hữu ích

### 1. Filter cơ bản:
```
tcp.port == 5050
```

### 2. Filter theo hướng:
```
# Chỉ client → server
tcp.port == 5050 and tcp.dstport == 5050

# Chỉ server → client  
tcp.port == 5050 and tcp.srcport == 5050
```

### 3. Filter theo nội dung:
```
# Tìm packets chứa "PUT"
tcp.port == 5050 and tcp.payload contains "PUT"

# Tìm packets chứa "201 CREATED"
tcp.port == 5050 and tcp.payload contains "201"
```

### 4. Filter theo kích thước:
```
# Packets có data > 0
tcp.port == 5050 and tcp.len > 0

# Packets chỉ ACK
tcp.port == 5050 and tcp.len == 0
```

## Phân tích Chi tiết trong Wireshark

### 1. Mở rộng TCP Header:
```
Transmission Control Protocol, Src Port: 12345, Dst Port: 5050, Seq: 1, Ack: 1, Len: 25
    Source Port: 12345
    Destination Port: 5050
    Sequence Number: 1
    Acknowledgment Number: 1
    Header Length: 20 bytes
    Flags: 0x018 (PSH, ACK)
    Window Size: 65535
    Checksum: 0x1234
    Urgent Pointer: 0
    Options: (0 bytes)
    [TCP Segment Len: 25]
```

### 2. Mở rộng Data:
```
Data (25 bytes)
    Data: 4b562f312e3020505554206e616d65204a6f686e0a
    [Length: 25]
    
    # Decode hex:
    # 4b56 = "KV"
    # 2f = "/"
    # 312e30 = "1.0"
    # 20 = " " (space)
    # 505554 = "PUT"
    # 20 = " " (space)
    # 6e616d65 = "name"
    # 20 = " " (space)
    # 4a6f686e = "John"
    # 0a = "\n" (LF)
```

## Test Cases để Quan sát

### 1. Test thông điệp ngắn:
```bash
python3 kvss_client.py PUT a b GET a STATS QUIT
```

### 2. Test thông điệp dài:
```bash
python3 -c "
import socket
s = socket.socket()
s.connect(('127.0.0.1', 5050))
long_value = 'A' * 2000
s.send(f'KV/1.0 PUT bigkey {long_value}\n'.encode())
print(s.recv(1024).decode())
s.close()
"
```

### 3. Test nhiều thông điệp liên tiếp:
```bash
for i in {1..10}; do
    echo "KV/1.0 PUT key$i value$i" | nc 127.0.0.1 5050
done
```

## Kết luận về TCP Segmentation cho Line-based Protocol

### 1. **Tính nguyên vẹn của dòng:**
- TCP đảm bảo thứ tự bytes
- Ký tự `\n` luôn được bảo toàn
- Application layer nhận được dòng hoàn chỉnh

### 2. **Hiệu quả truyền tải:**
- Thông điệp ngắn: 1 packet
- Thông điệp dài: Nhiều packets, nhưng vẫn đảm bảo tính nguyên vẹn
- TCP windowing tối ưu hóa throughput

### 3. **Debugging và Monitoring:**
- Wireshark cho thấy rõ cách TCP chia nhỏ data
- Có thể trace từng byte trong hex
- Dễ dàng phát hiện lỗi protocol

### 4. **So sánh với UDP:**
- **TCP**: Đảm bảo delivery, ordering, error checking
- **UDP**: Không đảm bảo, có thể mất hoặc sai thứ tự packets
- **Line-based protocol cần TCP** để đảm bảo tính toàn vẹn của dòng

## Lưu ý Quan trọng

1. **Luôn chạy Wireshark với quyền admin/sudo**
2. **Sử dụng filter để giảm noise**
3. **Quan sát cả TCP handshake và data flow**
4. **Chú ý đến ký tự `\n` trong data**
5. **Test với cả thông điệp ngắn và dài**

Bằng cách này, bạn có thể hiểu rõ cách TCP hoạt động với line-based protocol và tại sao nó phù hợp cho các ứng dụng text-based như KVSS.
