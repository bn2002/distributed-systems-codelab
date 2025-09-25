# Hướng dẫn sử dụng Wireshark phân tích TCP Line-based Protocol

## Tổng quan

Project KVSS sử dụng **line-based protocol** với TCP, trong đó mỗi thông điệp kết thúc bằng ký tự `\n`. Tài liệu này hướng dẫn cách sử dụng Wireshark để quan sát cách TCP chia nhỏ và truyền tải các thông điệp này.

## Cấu trúc Files

```
KVSS/
├── kvss_server.py              # Server implementation
├── kvss_client.py              # Client implementation
├── demo_wireshark.py           # Demo script tạo traffic
├── run_wireshark_demo.sh       # Script tự động chạy demo
├── wireshark_analysis_guide.md # Hướng dẫn phân tích cơ bản
├── tcp_segmentation_analysis.md # Phân tích chi tiết TCP segmentation
└── WIRESHARK_GUIDE.md          # File này
```

## Cài đặt và Chuẩn bị

### 1. Cài đặt Wireshark

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install wireshark
```

**Windows:**
- Tải từ https://www.wireshark.org/
- Cài đặt với quyền administrator

### 2. Cấu hình Wireshark

1. Mở Wireshark với quyền admin/sudo
2. Chọn interface:
   - **Linux**: `lo` (loopback) hoặc `any`
   - **Windows**: `Loopback` hoặc `Ethernet`
3. Áp dụng filter: `tcp.port == 5050`

## Cách sử dụng

### Phương pháp 1: Tự động (Khuyến nghị)

```bash
# Cấp quyền thực thi cho script
chmod +x run_wireshark_demo.sh

# Chạy demo tự động
./run_wireshark_demo.sh
```

Script sẽ:
1. Khởi động server KVSS
2. Hướng dẫn setup Wireshark
3. Chạy các test cases
4. Dừng server khi hoàn thành

### Phương pháp 2: Thủ công

**Bước 1: Khởi động Server**
```bash
python3 kvss_server.py
```

**Bước 2: Setup Wireshark**
1. Mở Wireshark
2. Chọn interface `lo` hoặc `any`
3. Áp dụng filter `tcp.port == 5050`
4. Click "Start capturing"

**Bước 3: Chạy Demo**
```bash
# Test cơ bản
python3 demo_wireshark.py

# Test cụ thể
python3 demo_wireshark.py short    # Thông điệp ngắn
python3 demo_wireshark.py long     # Thông điệp dài
python3 demo_wireshark.py multiple # Nhiều requests
python3 demo_wireshark.py error    # Test lỗi
python3 demo_wireshark.py concurrent # Nhiều client
```

## Các Test Cases

### 1. Short Messages (≤ MSS)
- **Mục đích**: Quan sát TCP với thông điệp nhỏ
- **Kích thước**: ~25 bytes
- **Kết quả**: 1 packet duy nhất

### 2. Long Messages (> MSS)
- **Mục đích**: Quan sát TCP segmentation
- **Kích thước**: 2000+ bytes
- **Kết quả**: Nhiều packets với PSH flag

### 3. Multiple Requests
- **Mục đích**: Quan sát TCP windowing
- **Số lượng**: 5 requests liên tiếp
- **Kết quả**: ACK batching

### 4. Error Cases
- **Mục đích**: Quan sát error handling
- **Các lỗi**: Thiếu version, version sai, thiếu parameters
- **Kết quả**: Error responses

### 5. Concurrent Clients
- **Mục đích**: Quan sát multi-threading
- **Số client**: 3 clients đồng thời
- **Kết quả**: Multiple TCP connections

## Phân tích trong Wireshark

### 1. TCP Handshake
Tìm kiếm packets với:
- **SYN**: `tcp.flags.syn == 1`
- **SYN-ACK**: `tcp.flags.syn == 1 and tcp.flags.ack == 1`
- **ACK**: `tcp.flags.ack == 1 and tcp.flags.syn == 0`

### 2. Data Transmission
Tìm kiếm packets với:
- **PSH flag**: `tcp.flags.push == 1`
- **Có payload**: `tcp.len > 0`
- **Chứa line ending**: `tcp.payload contains "0a"`

### 3. Sequence Numbers
Quan sát:
- **Sequence Number**: Số thứ tự byte đầu tiên
- **Acknowledgment Number**: Số thứ tự byte tiếp theo mong đợi
- **Length**: Số bytes trong segment

### 4. Window Management
Quan sát:
- **Window Size**: Số bytes receiver có thể nhận
- **Window Scaling**: Mở rộng window size
- **Zero Window**: Receiver buffer đầy

## Các Filter hữu ích

### Filter cơ bản
```
tcp.port == 5050
```

### Filter theo hướng
```
# Client → Server
tcp.port == 5050 and tcp.dstport == 5050

# Server → Client
tcp.port == 5050 and tcp.srcport == 5050
```

### Filter theo loại packet
```
# Data packets
tcp.port == 5050 and tcp.len > 0

# ACK packets
tcp.port == 5050 and tcp.len == 0

# PSH packets
tcp.port == 5050 and tcp.flags.push == 1
```

### Filter theo nội dung
```
# PUT requests
tcp.port == 5050 and tcp.payload contains "PUT"

# Error responses
tcp.port == 5050 and tcp.payload contains "400"

# Line endings
tcp.port == 5050 and tcp.payload contains "0a"
```

## Quan sát TCP Segmentation

### 1. Thông điệp ngắn (≤ 1460 bytes)
```
Client → Server: 1 packet với PSH flag
Server → Client: ACK + Response
```

### 2. Thông điệp dài (> 1460 bytes)
```
Client → Server: Nhiều packets, mỗi packet ≤ 1460 bytes
Server → Client: ACK cho mỗi segment
Server → Client: Response (có thể cũng bị chia nhỏ)
```

### 3. Đặc điểm quan trọng
- **PSH flag**: Báo hiệu cần đẩy data lên application
- **Sequence numbers**: Đảm bảo thứ tự bytes
- **ACK numbers**: Xác nhận đã nhận data
- **Window size**: Điều chỉnh tốc độ truyền

## Debugging Tips

### 1. Follow TCP Stream
- Right-click packet → Follow → TCP Stream
- Xem toàn bộ conversation
- Quan sát line-based protocol

### 2. Statistics
- Statistics → TCP Stream Graphs
- Quan sát throughput, RTT, window size
- Phát hiện bottlenecks

### 3. Export Data
- File → Export Objects → HTTP
- Lưu captured data để phân tích offline

### 4. Color Coding
- Setup color rules cho different packet types
- Dễ dàng phân biệt SYN, ACK, DATA, RST

## Troubleshooting

### 1. Không thấy packets
- Kiểm tra filter: `tcp.port == 5050`
- Kiểm tra interface: `lo` hoặc `any`
- Kiểm tra server có chạy không

### 2. Packets bị mất
- Kiểm tra duplicate ACKs
- Kiểm tra retransmissions
- Kiểm tra network interface

### 3. Performance issues
- Quan sát window size
- Kiểm tra RTT
- Phân tích throughput

## Kết luận

Qua việc phân tích TCP segmentation với Wireshark, chúng ta hiểu rõ:

1. **TCP đảm bảo tính toàn vẹn**: Mọi byte đều được đánh số và xác nhận
2. **Segmentation tự động**: TCP tự động chia nhỏ data > MSS
3. **Ordering**: Packets được sắp xếp đúng thứ tự
4. **Flow Control**: Window mechanism điều chỉnh tốc độ
5. **Error Recovery**: Retransmission khi mất packet

Với line-based protocol như KVSS, TCP đảm bảo rằng application layer luôn nhận được dòng hoàn chỉnh, bất kể data được chia thành bao nhiêu segments.

## Tài liệu tham khảo

- [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html/)
- [TCP RFC 793](https://tools.ietf.org/html/rfc793)
- [Line-based Protocol Best Practices](https://tools.ietf.org/html/rfc862)
