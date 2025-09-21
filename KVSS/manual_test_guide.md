# Hướng dẫn Test thủ công với nc/telnet

## 1. Khởi động Server

```bash
# Terminal 1: Khởi động server
python3 kvss_server.py
```

Server sẽ chạy trên `127.0.0.1:5050` và ghi log vào file `kvss_server.log`.

## 2. Test với netcat (nc)

### Mở Terminal 2 và kết nối:
```bash
nc 127.0.0.1 5050
```

### Các lệnh test:

#### Test PUT (tạo mới):
```
KV/1.0 PUT name John
```
**Kết quả mong đợi:** `201 CREATED`

#### Test PUT (cập nhật):
```
KV/1.0 PUT name Jane
```
**Kết quả mong đợi:** `200 OK`

#### Test GET (key tồn tại):
```
KV/1.0 GET name
```
**Kết quả mong đợi:** `200 OK Jane`

#### Test GET (key không tồn tại):
```
KV/1.0 GET nonexistent
```
**Kết quả mong đợi:** `404 NOT_FOUND`

#### Test DEL (key tồn tại):
```
KV/1.0 DEL name
```
**Kết quả mong đợi:** `204 NO_CONTENT`

#### Test DEL (key không tồn tại - idempotent):
```
KV/1.0 DEL name
```
**Kết quả mong đợi:** `404 NOT_FOUND`

#### Test STATS:
```
KV/1.0 STATS
```
**Kết quả mong đợi:** `200 OK` + thống kê

#### Test QUIT:
```
KV/1.0 QUIT
```
**Kết quả mong đợi:** `200 OK` (sau đó kết nối đóng)

### Test các trường hợp lỗi:

#### Thiếu version:
```
PUT name John
```
**Kết quả mong đợi:** `426 UPGRADE_REQUIRED`

#### Version sai:
```
KV/2.0 PUT name John
```
**Kết quả mong đợi:** `426 UPGRADE_REQUIRED`

#### PUT thiếu value:
```
KV/1.0 PUT name
```
**Kết quả mong đợi:** `400 BAD_REQUEST`

#### GET thiếu key:
```
KV/1.0 GET
```
**Kết quả mong đợi:** `400 BAD_REQUEST`

#### Command không hợp lệ:
```
KV/1.0 INVALID
```
**Kết quả mong đợi:** `400 BAD_REQUEST`

## 3. Test với telnet

### Kết nối:
```bash
telnet 127.0.0.1 5050
```

### Sử dụng tương tự như nc, gõ các lệnh và nhấn Enter.

## 4. Test với curl

### PUT:
```bash
echo "KV/1.0 PUT testkey testvalue" | nc 127.0.0.1 5050
```

### GET:
```bash
echo "KV/1.0 GET testkey" | nc 127.0.0.1 5050
```

### STATS:
```bash
echo "KV/1.0 STATS" | nc 127.0.0.1 5050
```

## 5. Test đồng thời nhiều client

### Mở nhiều terminal và chạy:
```bash
# Terminal 2
nc 127.0.0.1 5050

# Terminal 3  
nc 127.0.0.1 5050

# Terminal 4
nc 127.0.0.1 5050
```

Mỗi terminal có thể thực hiện các lệnh độc lập để test khả năng xử lý đa client của server.

## 6. Quan sát Log

Server ghi log vào file `kvss_server.log` và console. Quan sát log để thấy:
- Timestamp của mỗi request/response
- Địa chỉ IP của client
- Nội dung request và response

## 7. Test Performance

### Test với nhiều request liên tiếp:
```bash
for i in {1..100}; do
    echo "KV/1.0 PUT key$i value$i" | nc 127.0.0.1 5050
done
```

### Test với value lớn:
```bash
echo "KV/1.0 PUT bigkey $(python3 -c "print('A'*10000)")" | nc 127.0.0.1 5050
```
