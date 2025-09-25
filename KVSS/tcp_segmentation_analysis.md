# Phân tích TCP Segmentation cho Line-based Protocol trong Wireshark

## Tổng quan

Trong project KVSS, chúng ta sử dụng **line-based protocol** với TCP. Điều này có nghĩa là:
- Mỗi thông điệp kết thúc bằng ký tự `\n` (Line Feed)
- TCP có thể chia nhỏ thông điệp thành nhiều segments
- Application layer nhận được dữ liệu theo đúng thứ tự và đầy đủ

## Các khái niệm quan trọng

### 1. MSS (Maximum Segment Size)
- **MSS** = MTU - IP Header - TCP Header = 1500 - 20 - 20 = 1460 bytes
- Đây là kích thước tối đa của data trong một TCP segment
- Nếu thông điệp > MSS, TCP sẽ chia thành nhiều segments

### 2. TCP Window
- Cơ chế flow control của TCP
- Receiver thông báo cho sender biết có thể nhận bao nhiêu bytes
- Giúp tối ưu hóa throughput

### 3. PSH Flag
- Push flag báo hiệu cần đẩy data lên application layer ngay
- Quan trọng với line-based protocol để xử lý kịp thời

## Cách quan sát trong Wireshark

### Bước 1: Setup Wireshark
1. Mở Wireshark với quyền admin/sudo
2. Chọn interface `lo` (loopback)
3. Áp dụng filter: `tcp.port == 5050`
4. Bắt đầu capture

### Bước 2: Chạy Test
```bash
# Terminal 1: Start server
python3 kvss_server.py

# Terminal 2: Run demo
python3 demo_wireshark.py
```

### Bước 3: Phân tích Packets

## Phân tích chi tiết các loại packets

### 1. TCP Handshake

**Packet 1: SYN**
```
Protocol: TCP
Source: 127.0.0.1:random_port
Destination: 127.0.0.1:5050
Flags: SYN
Length: 0 bytes (no data)
```

**Packet 2: SYN-ACK**
```
Protocol: TCP
Source: 127.0.0.1:5050
Destination: 127.0.0.1:random_port
Flags: SYN, ACK
Length: 0 bytes (no data)
```

**Packet 3: ACK**
```
Protocol: TCP
Source: 127.0.0.1:random_port
Destination: 127.0.0.1:5050
Flags: ACK
Length: 0 bytes (no data)
```

### 2. Short Message (≤ MSS)

**Ví dụ: "KV/1.0 PUT name John\n" (25 bytes)**

**Packet 4: Data từ Client**
```
Protocol: TCP
Source: 127.0.0.1:random_port
Destination: 127.0.0.1:5050
Flags: PSH, ACK
Length: 25 bytes
Data: "KV/1.0 PUT name John\n"
```

**Packet 5: ACK từ Server**
```
Protocol: TCP
Source: 127.0.0.1:5050
Destination: 127.0.0.1:random_port
Flags: ACK
Length: 0 bytes (no data)
```

**Packet 6: Response từ Server**
```
Protocol: TCP
Source: 127.0.0.1:5050
Destination: 127.0.0.1:random_port
Flags: PSH, ACK
Length: 12 bytes
Data: "201 CREATED\n"
```

### 3. Long Message (> MSS)

**Ví dụ: "KV/1.0 PUT bigkey [2000 ký tự A]\n" (2010 bytes)**

**Packet 4: Segment 1**
```
Protocol: TCP
Source: 127.0.0.1:random_port
Destination: 127.0.0.1:5050
Flags: PSH, ACK
Length: 1460 bytes
Data: "KV/1.0 PUT bigkey AAAA...AAAA" (1460 bytes)
```

**Packet 5: ACK cho Segment 1**
```
Protocol: TCP
Source: 127.0.0.1:5050
Destination: 127.0.0.1:random_port
Flags: ACK
Length: 0 bytes
```

**Packet 6: Segment 2**
```
Protocol: TCP
Source: 127.0.0.1:random_port
Destination: 127.0.0.1:5050
Flags: PSH, ACK
Length: 550 bytes
Data: "AAAA...AAAA\n" (550 bytes còn lại)
```

**Packet 7: ACK cho Segment 2**
```
Protocol: TCP
Source: 127.0.0.1:5050
Destination: 127.0.0.1:random_port
Flags: ACK
Length: 0 bytes
```

## Các Filter Wireshark hữu ích

### 1. Filter cơ bản
```
tcp.port == 5050
```

### 2. Filter theo hướng
```
# Client → Server
tcp.port == 5050 and tcp.dstport == 5050

# Server → Client
tcp.port == 5050 and tcp.srcport == 5050
```

### 3. Filter theo loại packet
```
# Chỉ data packets (có payload)
tcp.port == 5050 and tcp.len > 0

# Chỉ ACK packets
tcp.port == 5050 and tcp.len == 0

# Packets có PSH flag
tcp.port == 5050 and tcp.flags.push == 1
```

### 4. Filter theo nội dung
```
# Tìm packets chứa "PUT"
tcp.port == 5050 and tcp.payload contains "PUT"

# Tìm packets chứa "201 CREATED"
tcp.port == 5050 and tcp.payload contains "201"

# Tìm packets chứa ký tự xuống dòng
tcp.port == 5050 and tcp.payload contains "0a"
```

## Phân tích Sequence Numbers

### 1. Sequence Number
- Mỗi byte được đánh số thứ tự
- Bắt đầu từ ISN (Initial Sequence Number)
- Tăng theo số bytes đã gửi

### 2. Acknowledgment Number
- Số thứ tự của byte tiếp theo mong đợi
- Xác nhận đã nhận được data

### 3. Ví dụ thực tế:
```
# Client gửi "KV/1.0 PUT name John\n" (25 bytes)
Packet 1: Seq=1, Len=25, Data="KV/1.0 PUT name John\n"
Packet 2: Ack=26 (xác nhận nhận được 25 bytes)

# Server gửi "201 CREATED\n" (12 bytes)  
Packet 3: Seq=1, Len=12, Data="201 CREATED\n"
Packet 4: Ack=13 (xác nhận nhận được 12 bytes)
```

## Quan sát TCP Window

### 1. Window Size
- Thông báo cho sender biết receiver có thể nhận bao nhiêu bytes
- Thường là 65535 bytes cho localhost

### 2. Window Scaling
- Mở rộng window size cho high-speed networks
- Không quan trọng với localhost

## Phân tích Performance

### 1. RTT (Round Trip Time)
- Thời gian từ khi gửi packet đến khi nhận ACK
- Với localhost thường < 1ms

### 2. Throughput
- Số bytes truyền được trong 1 giây
- Phụ thuộc vào window size và RTT

### 3. Bandwidth Delay Product
- BDP = Bandwidth × RTT
- Với localhost: BDP rất nhỏ

## Debugging Common Issues

### 1. Packet Loss
- Kiểm tra duplicate ACKs
- Kiểm tra retransmissions

### 2. Out of Order
- Kiểm tra sequence numbers
- TCP sẽ sắp xếp lại

### 3. Buffer Issues
- Kiểm tra window size
- Kiểm tra zero window

## Best Practices cho Wireshark Analysis

### 1. Sử dụng Statistics
- Go to Statistics → TCP Stream Graphs
- Quan sát throughput, RTT, window size

### 2. Follow TCP Stream
- Right-click packet → Follow → TCP Stream
- Xem toàn bộ conversation

### 3. Export Objects
- File → Export Objects → HTTP
- Lưu captured data

### 4. Color Coding
- Setup color rules cho different packet types
- Dễ dàng phân biệt SYN, ACK, DATA

## Kết luận

Qua việc phân tích TCP segmentation trong Wireshark, chúng ta thấy:

1. **TCP đảm bảo tính toàn vẹn**: Mọi byte đều được đánh số và xác nhận
2. **Segmentation tự động**: TCP tự động chia nhỏ data > MSS
3. **Ordering**: Packets được sắp xếp đúng thứ tự
4. **Flow Control**: Window mechanism điều chỉnh tốc độ
5. **Error Recovery**: Retransmission khi mất packet

Với line-based protocol như KVSS, TCP đảm bảo rằng application layer luôn nhận được dòng hoàn chỉnh, bất kể data được chia thành bao nhiêu segments.
