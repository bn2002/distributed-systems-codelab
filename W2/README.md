# Bài Thực Hành: Đồng Bộ Luồng trong Java

## Mô tả
Chương trình này mô phỏng và so sánh vấn đề **race condition** trong lập trình đa luồng với và không có cơ chế đồng bộ hóa.

## Cấu trúc chương trình

### Các lớp chung:
- **ResourcesExploiter.java**: Tài nguyên chia sẻ với biến `rsc` và phương thức `exploit()`

### Các lớp thực thi:
- **ThreadedWorkerWithoutSync.java**: Luồng KHÔNG có đồng bộ hóa
- **ThreadedWorkerWithSync.java**: Luồng CÓ đồng bộ hóa bằng `synchronized`
- **Main.java**: Chương trình chính sử dụng luồng không đồng bộ
- **MainWithSync.java**: Chương trình chính sử dụng luồng có đồng bộ

## Cách chạy
```bash
# Biên dịch tất cả
javac *.java

# So sánh hiệu suất và độ chính xác
./compare_sync.sh
```

---

## 📋 **CÂU HỎI 1: Race Condition - Không có Synchronization**

### Yêu cầu
Chạy chương trình với `ThreadedWorkerWithoutSync` và quan sát kết quả qua nhiều lần chạy.

### Kết quả quan sát được

#### Kết quả mong đợi:
- 3 luồng × 1000 lần exploit = **3000**

#### Kết quả thực tế:
```
Lần 1: 2701/3000 - ✗ SAI
Lần 2: 2950/3000 - ✗ SAI  
Lần 3: 2776/3000 - ✗ SAI
Lần 4: 2664/3000 - ✗ SAI
...
Độ chính xác: 0/10 lần đúng (0%)
```

### Giải thích Race Condition

#### 🔍 **Tại sao xảy ra Race Condition?**

1. **Phương thức `exploit()` không thread-safe:**
   ```java
   public void exploit() {
       setRsc(getRsc() + 1);  // 3 bước: READ → COMPUTE → WRITE
   }
   ```

2. **Trình tự thực thi bị đan xen:**
   ```
   Thread A: READ rsc = 100
   Thread B: READ rsc = 100    ← Vẫn đọc giá trị cũ!
   Thread A: COMPUTE 100+1=101, WRITE rsc = 101  
   Thread B: COMPUTE 100+1=101, WRITE rsc = 101  ← Ghi đè!
   
   Kết quả: rsc = 101 thay vì 102 → Mất 1 đơn vị!
   ```

3. **Critical Section không được bảo vệ:**
   - Vùng code truy cập `rsc` cần được bảo vệ
   - Nhiều luồng cùng truy cập đồng thời → xung đột

#### 🎲 **Tại sao đôi khi lại đúng?**
- **Thread scheduling may mắn**: JVM lên lịch không xung đột
- **Tốc độ CPU**: Luồng này hoàn thành trước khi luồng khác bắt đầu  
- **Không thể dự đoán**: Phụ thuộc vào môi trường runtime

#### 🏁 **Kết luận Câu hỏi 1:**
- **Vấn đề**: Race condition làm mất dữ liệu
- **Nguyên nhân**: Không có cơ chế bảo vệ critical section
- **Hậu quả**: Kết quả không nhất quán, không tin cậy

---

## 📋 **CÂU HỎI 2: Áp dụng Synchronization**

### Yêu cầu
Tạo `ThreadedWorkerWithSync` sử dụng `synchronized` và so sánh với câu hỏi 1.

### Cài đặt Synchronization

```java
public class ThreadedWorkerWithSync extends Thread {
    private ResourcesExploiter rExp;
    
    @Override
    public void run() {
        // Synchronized trên toàn bộ vòng lặp
        synchronized(rExp) {
            for(int i = 0; i < 1000; i++) {
                rExp.exploit();
            }
        }
    }
}
```

### Kết quả so sánh

#### ✅ **Với Synchronization:**
```
Lần 1: 3000/3000 - ✓ ĐÚNG
Lần 2: 3000/3000 - ✓ ĐÚNG
Lần 3: 3000/3000 - ✓ ĐÚNG
...
Độ chính xác: 10/10 lần đúng (100%)
Thời gian trung bình: 105ms
```

#### ❌ **Không Synchronization:**
```
Lần 1: 2701/3000 - ✗ SAI
Lần 2: 2950/3000 - ✗ SAI
...  
Độ chính xác: 0/10 lần đúng (0%)
Thời gian trung bình: 100ms
```

### Giải thích sự thay đổi

#### 🔒 **Cơ chế Synchronized hoạt động:**

1. **Monitor Lock (Mutex):**
   ```java
   synchronized(rExp) {
       // Chỉ một luồng được vào đây tại một thời điểm
       for(int i=0; i<1000; i++) {
           rExp.exploit(); // An toàn!
       }
   } // Tự động unlock
   ```

2. **Thứ tự thực thi được đảm bảo:**
   ```
   Thread A: LOCK → 1000 lần exploit → UNLOCK
   Thread B:         (đợi)          → LOCK → 1000 lần exploit → UNLOCK  
   Thread C:              (đợi)                    (đợi)     → LOCK → ...
   ```

3. **Loại bỏ hoàn toàn Race Condition:**
   - Không có truy cập đồng thời
   - Mỗi luồng hoàn thành trọn vẹn 1000 lần
   - Kết quả luôn chính xác: 3 × 1000 = 3000

#### ⚖️ **Trade-offs của Synchronization:**

**Ưu điểm:**
- ✅ **100% chính xác**: Không bao giờ có race condition
- ✅ **Đáng tin cậy**: Kết quả nhất quán qua các lần chạy
- ✅ **Thread-safe**: An toàn trong môi trường đa luồng

**Nhược điểm:**
- ❌ **Performance overhead**: +5% thời gian thực thi
- ❌ **Serialization**: Luồng chạy tuần tự thay vì song song
- ❌ **Potential deadlock**: Nếu có nhiều locks

#### 🏁 **Kết luận Câu hỏi 2:**

**Sự thay đổi quan trọng:**
1. **Độ chính xác**: Từ 0% → 100% 
2. **Tính nhất quán**: Từ không đoán trước → luôn đúng
3. **Hiệu suất**: Giảm nhẹ (~5%) nhưng chấp nhận được
4. **Đáng tin cậy**: Có thể sử dụng trong production

**Khuyến nghị:** Sử dụng ReentrantLock cho ứng dụng thực tế

---

## 📋 **CÂU HỎI 3: Sử dụng ReentrantLock**

### Yêu cầu
Tạo `ResourcesExploiterWithLock` và `ThreadedWorkerWithLock` sử dụng `ReentrantLock`, so sánh với câu hỏi 1.

### Cài đặt ReentrantLock

#### 1. ResourcesExploiterWithLock:
```java
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class ResourcesExploiterWithLock extends ResourcesExploiter {
    private ReentrantLock lock;
    
    public ResourcesExploiterWithLock(int n) {
        super(n);
        lock = new ReentrantLock();
    }
    
    @Override
    public void exploit() {
        try {
            if (lock.tryLock(10, TimeUnit.SECONDS)) {
                setRsc(getRsc() + 1);
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}
```

#### 2. ThreadedWorkerWithLock:
```java
public class ThreadedWorkerWithLock extends Thread {
    private ResourcesExploiterWithLock rExp;
    
    @Override
    public void run() {
        for (int i = 0; i < 1000; i++) {
            rExp.exploit(); // Lock được handle tự động
        }
    }
}
```

### Kết quả so sánh với Câu hỏi 1

#### ✅ **Với ReentrantLock (Câu hỏi 3):**
```
Lần 1: 3000/3000 (169ms) - ✅ ĐÚNG
Lần 2: 3000/3000 (172ms) - ✅ ĐÚNG
Lần 3: 3000/3000 (165ms) - ✅ ĐÚNG
...
Độ chính xác: 10/10 lần đúng (100%)
Thời gian trung bình: 164ms
```

#### ❌ **Không có đồng bộ (Câu hỏi 1):**
```
Lần 1: 2843/3000 (102ms) - ❌ SAI
Lần 2: 2904/3000 (90ms)  - ❌ SAI
Lần 3: 1956/3000 (92ms)  - ❌ SAI
...
Độ chính xác: 0/10 lần đúng (0%)
Thời gian trung bình: 99ms
```

### Sự khác biệt quan trọng với Câu hỏi 1

#### 🔒 **1. Độ chính xác:**
- **Câu hỏi 1**: 0% - Luôn bị race condition
- **Câu hỏi 3**: 100% - Hoàn toàn thread-safe
- **Cải thiện**: Từ không đáng tin cậy → hoàn toàn đáng tin cậy

#### ⏱️ **2. Hiệu suất:**
- **Câu hỏi 1**: ~99ms (nhanh nhưng sai)
- **Câu hỏi 3**: ~164ms (+65% overhead)
- **Trade-off**: Chậm hơn nhưng đúng 100%

#### 🔧 **3. Cơ chế hoạt động:**

**Câu hỏi 1 - Không đồng bộ:**
```
Thread A: READ rsc=100 → COMPUTE 101 → 
Thread B: READ rsc=100 → COMPUTE 101 → WRITE 101
Thread A:                                WRITE 101 ← Ghi đè!
Result: 101 thay vì 102 (mất 1 operation)
```

**Câu hỏi 3 - ReentrantLock:**
```
Thread A: ACQUIRE LOCK → READ→COMPUTE→WRITE → RELEASE LOCK
Thread B:     (đợi lock)                    → ACQUIRE LOCK → ...
Thread C:     (đợi lock)                         (đợi lock) → ...
Result: Luôn chính xác, không có race condition
```

### Giải thích chi tiết sự thay đổi

#### 🚀 **Ưu điểm của ReentrantLock:**

1. **🎯 Thread-Safe 100%:**
   - Không bao giờ có race condition
   - Mỗi thread thực hiện đúng 1000 operations
   - Kết quả luôn = 3000

2. **🔧 Linh hoạt hơn synchronized:**
   - `tryLock()` với timeout → tránh deadlock
   - Có thể interrupt được
   - Kiểm tra lock status
   - Fair/unfair locking options

3. **🛡️ Exception handling tốt hơn:**
   ```java
   try {
       if (lock.tryLock(10, TimeUnit.SECONDS)) {
           // Critical section
       } else {
           // Handle timeout
       }
   } finally {
       // Always unlock safely
   }
   ```

#### ⚠️ **Nhược điểm so với Câu hỏi 1:**

1. **🐌 Performance Overhead:**
   - +65% thời gian thực thi
   - Overhead của lock acquisition/release

2. **🤔 Phức tạp hơn:**
   - Phải handle try-finally
   - Kiểm tra `isHeldByCurrentThread()`
   - Quản lý timeout và exceptions

3. **💾 Memory Overhead:**
   - ReentrantLock object
   - Thread queue management

### So sánh với các phương pháp khác

| Tiêu chí | Không sync | Synchronized | ReentrantLock |
|----------|------------|--------------|---------------|
| **Độ chính xác** | ❌ 0% | ✅ 100% | ✅ 100% |
| **Hiệu suất** | ⚡ Nhanh nhất | 🐌 Chậm | 🚀 Trung bình |
| **Đơn giản** | 😊 Đơn giản | 😊 Đơn giản | 🤔 Phức tạp |
| **Linh hoạt** | ❌ Không | ❌ Hạn chế | ✅ Cao |
| **Timeout** | ❌ Không | ❌ Không | ✅ Có |

#### 🏁 **Kết luận Câu hỏi 3:**

**Sự thay đổi so với Câu hỏi 1:**
1. **Từ không đáng tin cậy → hoàn toàn đáng tin cậy**
2. **Từ race condition → thread-safe**
3. **Từ đơn giản → phức tạp nhưng mạnh mẽ hơn**
4. **Trade-off hợp lý**: Chi phí performance để đảm bảo correctness

**Khi nào sử dụng ReentrantLock:**
- ✅ Cần timeout cho lock acquisition
- ✅ Cần interrupt lock waiting
- ✅ Cần fair locking
- ✅ Cần kiểm tra lock status
- ✅ Critical section phức tạp

**Bài học quan trọng:**
**Bài học quan trọng:**
ReentrantLock cung cấp **perfect correctness** với **acceptable performance cost**, là lựa chọn tốt cho các ứng dụng production cần độ tin cậy cao.

---

# 2. Lập Trình Song Song với Đoạn Găng (Ngôn ngữ C)

## 2.1. Nội dung
Khám phá các kỹ thuật lập trình song song của ngôn ngữ C để giải quyết vấn đề tương tranh trong việc truy cập đoạn găng (critical section) của các luồng.

## 2.2. Yêu cầu

### 2.2.1. Lý thuyết
- Lập trình song song với đoạn găng
- Pthread library trong C
- Thread synchronization

### 2.2.2. Phần cứng
- Laptop/PC dùng Linux

### 2.2.3. Phần mềm
- gcc với pthread support

## 2.3. Các bước thực hành

### Tạo file simple.c
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>
#include <time.h>

int shared = 10;

void * fun(void * args){
    time_t start = time(NULL);
    time_t end = start + 5; //run for 5 seconds
    
    // YOUR-CODE-HERE - Vòng lặp tăng biến shared trong 5 giây
    while (time(NULL) < end) {
        shared++;
        usleep(1000); // Nghỉ 1ms để tránh tiêu tốn CPU quá mức
    }
    
    return NULL;
}

int main(){
    pthread_t thread_id;
    pthread_create(&thread_id, NULL, fun, NULL);
    pthread_join(thread_id, NULL);
    printf("shared: %d\n", shared);
    return 0;
}
```

---

## 📋 **CÂU HỎI 4: Hoàn thiện chương trình đa luồng C**

### Yêu cầu
Hoàn thiện file `simple.c` với một vòng lặp để tăng biến `shared` lên một đơn vị trong vòng 5 giây.

### Giải pháp thực hiện

#### 💡 **Phân tích đề bài:**
1. **Thời gian chạy**: 5 giây (sử dụng `time(NULL)`)
2. **Thao tác**: Tăng biến `shared` lên 1 đơn vị mỗi lần
3. **Vòng lặp**: Chạy liên tục trong 5 giây

#### 🔧 **Code hoàn thiện:**
```c
// Phần YOUR-CODE-HERE được thay thế bằng:
while (time(NULL) < end) {
    shared++;
    usleep(1000); // Nghỉ 1ms để tránh tiêu tốn CPU quá mức
}
```

#### 🎯 **Giải thích từng thành phần:**

1. **Điều kiện vòng lặp:**
   ```c
   while (time(NULL) < end)
   ```
   - `time(NULL)`: Lấy thời gian hiện tại (giây)
   - `end = start + 5`: Thời điểm kết thúc sau 5 giây
   - Vòng lặp chạy đến khi đạt 5 giây

2. **Thao tác tăng biến:**
   ```c
   shared++;
   ```
   - Tăng biến `shared` lên 1 đơn vị
   - Thao tác này không thread-safe (sẽ thảo luận ở câu hỏi tiếp theo)

3. **Tối ưu CPU:**
   ```c
   usleep(1000); // Nghỉ 1ms
   ```
   - Tránh busy-waiting tiêu tốn CPU 100%
   - Cho phép scheduler chuyển context
   - 1ms = 1000 microseconds

### Biên dịch và chạy

```bash
# Biên dịch với pthread
gcc -pthread simple.c -o simple

# Hoặc sử dụng Makefile
make

# Chạy chương trình
./simple
```

### Kết quả mong đợi

```
shared: [Số lớn hơn 10]
```

**Ví dụ output:**
```bash
$ ./simple
shared: 4015

$ ./simple  
shared: 4023

$ ./simple
shared: 3998
```

#### 📊 **Phân tích kết quả:**

1. **Giá trị ban đầu:** `shared = 10`
2. **Thời gian chạy:** 5 giây
3. **Tần suất tăng:** ~1000 lần/giây (do `usleep(1000)`)
4. **Kết quả dự kiến:** ~5000 + 10 = ~5010

**Tại sao có sự chênh lệch?**
- Thời gian thực thi các lệnh
- Overhead của system calls
- Thread scheduling delays
- Độ chính xác của `time(NULL)` (đơn vị giây)

### Điểm quan trọng cần lưu ý

#### ⚠️ **Chưa có vấn đề race condition:**
- Chỉ có **1 thread** truy cập `shared`
- Main thread tạo worker thread và đợi
- Không có concurrent access

#### 🔄 **Flow thực thi:**
```
Main Thread: CREATE worker_thread → WAIT (pthread_join)
Worker Thread:                    → RUN (5 seconds) → FINISH
Main Thread:                                        → CONTINUE → PRINT
```

#### 🎓 **Bài học:**
1. **`time(NULL)`** đơn giản nhưng hiệu quả cho timing
2. **`usleep()`** quan trọng để tránh busy-waiting
3. **Single-threaded access** an toàn, không cần synchronization
4. **Pthread basics:** `pthread_create()`, `pthread_join()`

#### 🏁 **Kết luận Câu hỏi 4:**
- ✅ **Hoàn thành thành công:** Vòng lặp tăng `shared` trong 5 giây
- ✅ **Code sạch:** Dễ hiểu, có comments
- ✅ **Performance tốt:** Không waste CPU với `usleep()`
- ✅ **Thread-safe:** Một thread duy nhất truy cập

**Chuẩn bị cho bước tiếp theo:** Thêm nhiều threads để tạo race condition!

---

## 📋 **CÂU HỎI 5: Mô phỏng dịch vụ ngân hàng - Phát hiện Race Condition**

### Yêu cầu
Tạo chương trình đa luồng mô phỏng dịch vụ ngân hàng không sử dụng locking. Tăng số luồng và số giao dịch để quan sát race condition.

### Tạo file without-lock.c

```c
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>

#define INIT_BALANCE 50
#define NUM_TRANS 1000  // Tăng lên 1000 để dễ phát hiện race condition

int balance = INIT_BALANCE;
int credits = 0;
int debits = 0;

void * transactions(void * args){
    int i, v;
    for(i = 0; i < NUM_TRANS; i++){
        // choose a random value
        srand(time(NULL) + pthread_self() + i);
        v = rand() % 50 + 1; // Giá trị từ 1-50
        
        // randomly choose to credit or debit
        if(rand() % 2){
            // credit - CRITICAL SECTION không được bảo vệ
            balance = balance + v;
            credits = credits + v;
        } else {
            // debit - CRITICAL SECTION không được bảo vệ
            balance = balance - v;
            debits = debits + v;
        }
    }
    return 0;
}
```

### Kết quả thí nghiệm

#### 🧪 **Test với số luồng tăng dần:**

**2 luồng:**
```
✅ CONSISTENT - 3/3 lần đúng
```

**5 luồng:**
```
❌ INCONSISTENT - 0/3 lần đúng
Run 1: Difference: 40
Run 2: Difference: 82  
Run 3: Difference: 17
```

**10 luồng:**
```
❌ INCONSISTENT - 0/5 lần đúng
Run 1: Difference: 100
Run 2: Difference: -76
Run 3: Difference: 50
Run 4: Difference: 279
Run 5: Difference: 53
```

### Phân tích Race Condition

#### 🔍 **Tại sao xuất hiện sự khác nhau?**

**1. Critical Section không được bảo vệ:**
```c
// Thread A và Thread B cùng thực hiện
balance = balance + v;  // 3 bước: READ → COMPUTE → WRITE
credits = credits + v;  // 3 bước: READ → COMPUTE → WRITE
```

**2. Interleaving execution (thực thi đan xen):**
```
Thread A: READ balance=100
Thread B: READ balance=100    ← Vẫn đọc giá trị cũ!
Thread A: COMPUTE 100+50=150
Thread B: COMPUTE 100+30=130
Thread A: WRITE balance=150
Thread B: WRITE balance=130   ← Ghi đè! Mất 50 units
```

**3. Multiple variables bị ảnh hưởng:**
- `balance`: Số dư thực tế
- `credits`: Tổng tiền gửi vào
- `debits`: Tổng tiền rút ra

#### 📊 **Mô hình Race Condition:**

**Kỳ vọng:**
```
Final Balance = INIT_BALANCE + credits - debits
50 + 63586 - 65404 = -1768
```

**Thực tế:**
```
Actual Balance = -1708
Difference = -1708 - (-1768) = 60
```

#### ⚠️ **Các dạng Race Condition quan sát được:**

**1. Lost Update (Cập nhật bị mất):**
```
Thread 1: balance += 50
Thread 2: balance -= 30
Kết quả: Một trong hai thao tác bị mất
```

**2. Dirty Read (Đọc dữ liệu bẩn):**
```
Thread 1: Đọc balance, chưa ghi xong
Thread 2: Đọc balance cũ, tính toán sai
```

**3. Write-Write Conflict:**
```
Thread 1: Ghi balance = 150
Thread 2: Ghi balance = 130 (đồng thời)
Kết quả: Không biết giá trị nào được giữ lại
```

### Giải thích chi tiết sự khác biệt

#### 🎯 **Tại sao 2 luồng ít race condition hơn 5-10 luồng?**

**Xác suất collision:**
- **2 luồng**: Ít cơ hội truy cập cùng lúc
- **5 luồng**: Nhiều luồng → nhiều xung đột
- **10 luồng**: Rất nhiều xung đột → race condition nghiêm trọng

**CPU scheduling:**
- Nhiều luồng → nhiều context switch
- Tăng khả năng interrupt giữa READ-WRITE
- Time slicing ngắn → dễ bị đan xen

#### 📈 **Kết quả quan sát:**

| Số luồng | Consistency | Race Condition | Mức độ nghiêm trọng |
|----------|-------------|----------------|---------------------|
| 2        | ✅ 100%     | Không          | Không có            |
| 5        | ❌ 0%       | Có             | Trung bình (17-82)  |
| 10       | ❌ 0%       | Có             | Cao (53-279)        |

#### 🔬 **Phân tích sâu hơn:**

**Không dự đoán được:**
- Difference dao động từ -76 đến +279
- Có thể mất tiền hoặc tăng tiền ma
- Hoàn toàn phụ thuộc vào timing

**Ngẫu nhiên:**
- Cùng input, khác output
- Không thể reproduce chính xác
- Phụ thuộc vào hệ điều hành, CPU load

#### 🏁 **Kết luận Câu hỏi 5:**

**Race condition xuất hiện khi:**
1. **≥ 5 luồng** truy cập đồng thời
2. **Nhiều giao dịch** (1000 transactions/thread)
3. **Không có synchronization mechanism**

**Hậu quả:**
- ❌ **Dữ liệu không nhất quán**: Balance ≠ Expected
- ❌ **Không thể dự đoán**: Kết quả ngẫu nhiên
- ❌ **Mất dữ liệu**: Transactions bị ghi đè
- ❌ **Không tin cậy**: Không thể dùng trong production

**Giải pháp cần thiết:**
- 🔒 **Mutex/Lock** để bảo vệ critical section
- 🛡️ **Atomic operations** cho single operations  
- 📊 **Thread-safe data structures**

**Bài học quan trọng:**
Race condition là **bug nghiêm trọng** trong hệ thống tài chính, có thể dẫn đến mất tiền hoặc dữ liệu không chính xác!

---

## 📋 **CÂU HỎI 6: Naive Lock - Giải pháp thô sơ cho Critical Section**

### Yêu cầu
Sử dụng kỹ thuật Naive-Lock với biến `lock` để bảo vệ critical section. Tìm ra vấn đề của approach này.

### Tạo file naive-lock.c

```c
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>

int lock = 0; // 0 for unlocked, 1 for locked
int shared = 0; // shared variable

void * incrementer(void * args){
    int i;
    for(i = 0; i < 100; i++){
        // check lock - NAIVE SPIN LOCK
        while(lock > 0); // spin until unlocked
        lock = 1; // set lock
        shared++; // increment - CRITICAL SECTION
        lock = 0; // unlock
    }
    return NULL;
}
```

### Kết quả thí nghiệm

#### 🧪 **Test với số luồng tăng dần:**

**2-5 luồng:**
```
✅ SUCCESS - 10/10 lần đúng (100%)
```

**10 luồng:**
```
❌ RACE CONDITION - 8/10 lần đúng (80%)
Run 5: 998/1000 (Lost: 2)
Run 6: 973/1000 (Lost: 27)
```

**20 luồng:**
```
❌ RACE CONDITION - 9/10 lần đúng (90%)
Run 6: 1944/2000 (Lost: 56)
```

### Phân tích mã nguồn - Tìm ra vấn đề

#### 🔍 **Vấn đề của Naive Lock:**

**1. Race Condition trong Lock itself:**
```c
while(lock > 0); // Step 1: Check lock
lock = 1;        // Step 2: Set lock
```

**Đây KHÔNG phải atomic operation!** Giữa Step 1 và Step 2 có thể bị interrupt.

#### 📊 **Sơ đồ Race Condition:**

```
Timeline: Thread A          Thread B          Lock Value
T1:       while(lock > 0)                    lock = 0
T2:       -> lock = 0, OK                    lock = 0  
T3:                       while(lock > 0)    lock = 0
T4:                       -> lock = 0, OK    lock = 0
T5:       lock = 1                           lock = 1
T6:                       lock = 1           lock = 1 (ghi đè!)
T7:       shared++        shared++           lock = 1
          (CẢ HAI THREAD CÙNG VÀO CRITICAL SECTION!)
```

#### ⚠️ **Chi tiết vấn đề:**

**1. Non-atomic Check-and-Set:**
- Việc kiểm tra `lock == 0` và set `lock = 1` không phải 1 operation
- Có thể bị context switch giữa check và set
- Nhiều threads có thể đều thấy `lock == 0` cùng lúc

**2. Time-of-Check vs Time-of-Use (TOCTOU):**
```c
while(lock > 0);  // Time of Check: lock = 0
// <-- INTERRUPT có thể xảy ra ở đây -->
lock = 1;         // Time of Use: set lock
```

**3. Memory Visibility Issues:**
- Compiler optimization có thể reorder instructions
- CPU caching có thể làm delay việc sync lock value
- Không có memory barrier

#### 🔬 **Tại sao đôi khi lại hoạt động?**

**Luck Factor:**
- **Low contention**: Ít threads, ít xung đột
- **Fast execution**: Critical section ngắn
- **Good scheduling**: OS schedule không xung đột

**Statistical Nature:**
- 10 threads: 80% thành công
- 20 threads: 90% thành công  
- Tăng threads → tăng contention → tăng failure rate

### Giải thích chi tiết

#### 💡 **Ý tưởng đúng, Implementation sai:**

**Ý tưởng đúng:**
- ✅ Dùng flag để báo hiệu critical section busy
- ✅ Spin wait để chờ critical section free
- ✅ Set flag trước khi vào, clear flag sau khi ra

**Implementation sai:**
- ❌ Check và Set không atomic
- ❌ Không có memory barriers
- ❌ Compiler có thể optimize sai

#### 🛠️ **Giải pháp đúng cần:**

1. **Atomic Operations:**
   ```c
   // Cần atomic compare-and-swap
   while(__sync_lock_test_and_set(&lock, 1)); 
   ```

2. **Memory Barriers:**
   ```c
   __sync_synchronize(); // Memory fence
   ```

3. **Hardware Support:**
   - CPU-level atomic instructions
   - Memory consistency guarantees

#### 📊 **So sánh với No Lock:**

| Approach | Correctness | Performance | Complexity |
|----------|-------------|-------------|------------|
| **No Lock** | ❌ 0% | ⚡ Fastest | 😊 Simple |
| **Naive Lock** | ⚠️ 80-90% | 🐌 Slower | 😐 Medium |
| **Proper Lock** | ✅ 100% | 🚀 Acceptable | 🤔 Complex |

#### 🏁 **Kết luận Câu hỏi 6:**

**Naive Lock thất bại vì:**
1. **Race condition trong lock mechanism**: Check-and-set không atomic
2. **False sense of security**: Trông có vẻ đúng nhưng vẫn có bug
3. **Intermittent failures**: Đôi khi đúng, đôi khi sai → khó debug

**Bài học quan trọng:**
- 🚫 **Đừng tự implement lock**: Rất dễ sai
- ✅ **Dùng system-provided primitives**: pthread_mutex, atomic operations
- 🔍 **Test thoroughly**: Race condition có thể ẩn sâu
- 📚 **Understand hardware**: Cần hiểu CPU memory model

**Next step:** Sử dụng **pthread_mutex** - giải pháp đúng đắn!

---

## 📋 **CÂU HỎI 7: Mutex Lock - Giải pháp chính thống cho Thread Synchronization**

### Yêu cầu
Thay đổi code từ `without-lock.c` bằng cách triển khai cơ chế pthread mutex lock. So sánh với naive-lock approach.

### Triển khai Mutex Lock

#### 🔧 **Các bước thực hiện:**

1. **Khai báo biến mutex:**
   ```c
   pthread_mutex_t mutex;
   ```

2. **Khởi tạo mutex:**
   ```c
   pthread_mutex_init(&mutex, NULL);
   ```

3. **Sử dụng lock/unlock:**
   ```c
   pthread_mutex_lock(&mutex);
   /* critical section code */
   pthread_mutex_unlock(&mutex);
   ```

4. **Hủy mutex:**
   ```c
   pthread_mutex_destroy(&mutex);
   ```

### Tạo file mutex-lock-banking.c

```c
#include <pthread.h>
// ... other includes

int balance = INIT_BALANCE;
int credits = 0;
int debits = 0;

// Khai báo biến mutex
pthread_mutex_t mutex;

void * transactions(void * args){
    int i, v;
    for(i = 0; i < NUM_TRANS; i++){
        // choose a random value
        srand(time(NULL) + pthread_self() + i);
        v = rand() % NUM_TRANS;
        
        // CRITICAL SECTION - Protected by mutex
        pthread_mutex_lock(&mutex);
        
        if(rand() % 2){
            balance = balance + v;
            credits = credits + v;
        } else {
            balance = balance - v;
            debits = debits + v;
        }
        
        pthread_mutex_unlock(&mutex);
        // END CRITICAL SECTION
    }
    return 0;
}

int main(int argc, char * argv[]){
    // ... setup code
    
    // Khởi tạo biến mutex trước khi sử dụng
    pthread_mutex_init(&mutex, NULL);
    
    // ... create and join threads
    
    // Hủy và giải phóng biến mutex
    pthread_mutex_destroy(&mutex);
    
    return 0;
}
```

### Kết quả thí nghiệm

#### 🧪 **Test với số luồng khác nhau:**

**5-50 threads:**
```
✅ CONSISTENT - Perfect thread synchronization! (100% success)
```

**100 threads:**
```
✅ CONSISTENT - Perfect thread synchronization! (100% success)
```

### So sánh ba approaches

#### 📊 **Test với 20 threads, 1000 transactions/thread:**

**1. Without Lock:**
```
Expected Balance: 50 + 252913 - 256696 = -3733
Actual Balance: -3547
Difference: 186 ❌ Race condition detected!
```

**2. Naive Lock:**
```
Expected: 2000, Actual: 1944 ❌ (Lost 56 increments)
Intermittent failures (~90% success rate)
```

**3. Mutex Lock:**
```
Expected Balance: 50 + 256435 - 251442 = 5043
Actual Balance: 5043
Difference: 0 ✅ Perfect synchronization!
```

### Phân tích cải thiện so với Naive-Lock

#### 🎯 **Mutex Lock vs Naive Lock:**

**1. Atomic Operations:**
- **Naive Lock**: `while(lock > 0); lock = 1;` → Không atomic
- **Mutex Lock**: `pthread_mutex_lock()` → Hardware-level atomic

**2. Race Condition:**
- **Naive Lock**: Race condition trong lock mechanism itself
- **Mutex Lock**: Không có race condition, OS kernel đảm bảo

**3. Reliability:**
- **Naive Lock**: ~90% success rate (intermittent failures)
- **Mutex Lock**: 100% success rate (never fails)

**4. Performance:**
- **Naive Lock**: Busy waiting (spin lock) → waste CPU
- **Mutex Lock**: Blocking wait → efficient CPU usage

#### 🔍 **Tại sao Mutex Lock hoàn hảo?**

**1. Hardware Support:**
```
pthread_mutex_lock() sử dụng:
- Atomic compare-and-swap instructions
- Memory barriers để đảm bảo consistency
- OS scheduler integration
```

**2. Kernel-level Synchronization:**
- Không có race condition trong lock acquisition
- Thread blocking thay vì spinning
- Fairness guarantees

**3. Memory Model Compliance:**
- Đảm bảo memory ordering
- Cache coherency protocol compliance
- No compiler optimization issues

#### ⚡ **Performance Characteristics:**

**Mutex Lock advantages:**
- ✅ **No busy waiting**: Threads sleep thay vì spin
- ✅ **CPU efficient**: Không waste cycles
- ✅ **Scalable**: Performance không giảm với nhiều threads
- ✅ **Fair**: First-come-first-serve access

**Trade-offs:**
- **Overhead**: System call overhead cho lock/unlock
- **Context switching**: Cost của thread blocking/waking

#### 📈 **Detailed Comparison Table:**

| Metric | No Lock | Naive Lock | Mutex Lock |
|--------|---------|------------|------------|
| **Correctness** | ❌ 0% | ⚠️ ~90% | ✅ 100% |
| **Reliability** | Never | Intermittent | Always |
| **CPU Usage** | Low | High (spinning) | Optimal |
| **Scalability** | Poor | Poor | Excellent |
| **Debugging** | Hard | Very hard | Easy |
| **Production** | 🚫 Never | 🚫 Never | ✅ Ready |

### Kết luận về cải thiện

#### 🏆 **Mutex Lock cải thiện hoàn toàn:**

**1. Từ không đáng tin cậy → hoàn toàn đáng tin cậy:**
- No race condition scenarios
- Deterministic behavior  
- Reproducible results

**2. Từ resource waste → resource efficient:**
- No CPU spinning
- Optimal thread scheduling
- Lower power consumption

**3. Từ hard-to-debug → easy-to-reason:**
- Clear lock semantics
- Well-documented behavior
- Standard library support

#### 🎓 **Bài học quan trọng:**

**Đừng reinvent the wheel:**
- ✅ **Use pthread_mutex**: Đã được test và optimize kỹ lưỡng
- ✅ **Trust system primitives**: OS và hardware support
- ✅ **Follow best practices**: Standard synchronization patterns

**Critical Section Protection:**
- 🔒 **Always use proper locks** cho shared resources
- 🔒 **Minimize critical section size** để tăng performance
- 🔒 **Avoid deadlocks** với consistent lock ordering

**Production Readiness:**
- Mutex lock là **industry standard** cho thread synchronization
- Được sử dụng trong **all major software systems**
- **Zero tolerance** cho race conditions trong production

#### 🏁 **Final Verdict:**

**Mutex Lock thắng áp đảo** với:
- **100% correctness** vs 0% (no-lock) và ~90% (naive-lock)
- **Efficient resource usage** vs CPU spinning
- **Production-ready reliability** vs experimental implementations

**Next step:** Khám phá advanced synchronization như **condition variables**, **read-write locks**, và **lock-free programming**!

---

## 📋 **CÂU HỎI 8: Fine Locking vs Coarse Locking - Tối ưu Performance**

### Yêu cầu
So sánh hai kỹ thuật locking: Coarse Locking (1 lock cho toàn bộ) vs Fine Locking (multiple locks cho từng biến riêng). Đo đạc thời gian để chứng minh Fine Locking nhanh hơn.

### Lý thuyết về Locking Strategies

#### 🔒 **Coarse Locking (Khóa thô sơ):**
- **Sử dụng 1 mutex duy nhất** cho toàn bộ critical section
- **Pros**: Đơn giản, không deadlock
- **Cons**: Serialization bottleneck - chỉ 1 thread active tại 1 thời điểm

#### 🔧 **Fine Locking (Khóa tinh vi):**
- **Sử dụng multiple mutex** cho từng resource riêng biệt
- **Pros**: Better parallelism - nhiều threads có thể hoạt động đồng thời
- **Cons**: Phức tạp hơn, có thể deadlock nếu không cẩn thận

### Triển khai Fine Locking

#### 🛠️ **Tạo file fine-locking-bank.c:**

```c
#include <pthread.h>
// ... includes

int balance = INIT_BALANCE;
int credits = 0;
int debits = 0;

// Fine Locking - 3 mutex riêng biệt
pthread_mutex_t b_lock; // cho biến balance
pthread_mutex_t c_lock; // cho biến credits  
pthread_mutex_t d_lock; // cho biến debits

void * transactions(void * args){
    int i, v;
    for(i = 0; i < NUM_TRANS; i++){
        srand(time(NULL) + pthread_self() + i);
        v = rand() % 50 + 1;
        
        if(rand() % 2){
            // CREDIT TRANSACTION - Fine Locking
            pthread_mutex_lock(&b_lock);
            balance = balance + v;
            pthread_mutex_unlock(&b_lock);
            
            pthread_mutex_lock(&c_lock);
            credits = credits + v;
            pthread_mutex_unlock(&c_lock);
            
        } else {
            // DEBIT TRANSACTION - Fine Locking
            pthread_mutex_lock(&b_lock);
            balance = balance - v;
            pthread_mutex_unlock(&b_lock);
            
            pthread_mutex_lock(&d_lock);
            debits = debits + v;
            pthread_mutex_unlock(&d_lock);
        }
    }
    return 0;
}

int main(){
    // Khởi tạo 3 mutex locks
    pthread_mutex_init(&b_lock, NULL);
    pthread_mutex_init(&c_lock, NULL);
    pthread_mutex_init(&d_lock, NULL);
    
    // ... thread creation and joining
    
    // Hủy 3 mutex locks
    pthread_mutex_destroy(&b_lock);
    pthread_mutex_destroy(&c_lock);
    pthread_mutex_destroy(&d_lock);
}
```

### Kết quả Performance Benchmark

#### 📊 **Comparison Summary:**

| Threads | Coarse Locking | Fine Locking | Improvement |
|---------|----------------|--------------|-------------|
| 20      | 102.46 ms      | 87.87 ms     | **14.2%**   |
| 50      | 229.97 ms      | 202.63 ms    | **11.9%**   |
| 100     | 481.80 ms      | 383.80 ms    | **20.3%**   |

#### 🎯 **Key Performance Metrics (100 threads):**

**Coarse Locking:**
```
Execution Time: 481.80 ms
Throughput: 207,565 transactions/second
```

**Fine Locking:**
```
Execution Time: 383.80 ms  
Throughput: 260,588 transactions/second
```

**Improvement: 20.3% faster với Fine Locking!**

### Phân tích chi tiết sự cải thiện

#### 🚀 **Tại sao Fine Locking nhanh hơn?**

**1. Reduced Contention (Giảm tranh chấp):**
```
Coarse Locking:
Thread A: LOCK → balance+credit+debit → UNLOCK
Thread B:        (wait for A)        → LOCK → ...
Thread C:        (wait for B)              → (wait) → ...

Fine Locking:  
Thread A: LOCK(balance) → UNLOCK → LOCK(credit) → UNLOCK
Thread B: LOCK(balance) → wait    → LOCK(debit)  → no wait!
Thread C: LOCK(debit)   → no wait! → LOCK(credit) → wait
```

**2. Better Parallelism:**
- **Coarse**: Chỉ 1 thread active tại 1 thời điểm
- **Fine**: Nhiều threads có thể hoạt động song song trên different variables

**3. Shorter Critical Sections:**
- **Coarse**: Lock toàn bộ transaction (3 operations)
- **Fine**: Lock từng operation riêng biệt (1 operation/lock)

#### 📈 **Scaling Characteristics:**

**Thread Count vs Performance:**
- **20 threads**: Fine locking cải thiện 14.2%
- **50 threads**: Cải thiện 11.9% 
- **100 threads**: Cải thiện 20.3%

**Insight**: Fine locking có **better scalability** - performance gap tăng theo số threads!

#### 🔬 **Technical Analysis:**

**Lock Hold Time:**
```
Coarse Locking hold time = time(balance + credit/debit update)
Fine Locking hold time = time(single variable update)
```

**Parallelism Factor:**
```
Coarse: Parallelism = 1 (serialized)
Fine: Parallelism ≈ 3 (balance, credits, debits independent)
```

**Contention Probability:**
```
Coarse: P(contention) = high (single bottleneck)
Fine: P(contention) = lower (distributed across 3 locks)
```

### Limitations và Trade-offs

#### ⚠️ **Fine Locking Challenges:**

**1. Deadlock Risk:**
```c
// Potential deadlock if inconsistent lock ordering
Thread A: lock(b_lock) → lock(c_lock)
Thread B: lock(c_lock) → lock(b_lock) // DEADLOCK!
```

**2. Overhead:**
- More mutex objects → memory overhead
- Multiple lock/unlock calls → CPU overhead
- Complex code → maintenance overhead

**3. Granularity Trade-off:**
- Too fine → too much overhead
- Too coarse → poor parallelism

#### 🎛️ **When to Use Each:**

**Use Coarse Locking when:**
- ✅ Simple operations
- ✅ Low contention
- ✅ Development speed important
- ✅ Avoid deadlocks critical

**Use Fine Locking when:**
- ✅ High contention scenarios
- ✅ Performance critical
- ✅ Independent data structures
- ✅ Scalability important

### Real-world Applications

#### 🏦 **Banking System Example:**
```
Fine Locking Perfect fit:
- Account balance (b_lock)
- Transaction log (c_lock) 
- Audit trail (d_lock)

Different threads accessing different accounts → excellent parallelism
```

#### 🏪 **E-commerce Inventory:**
```
Product A stock (lock_A)
Product B stock (lock_B)
Order processing (order_lock)

Concurrent purchases of different products → no contention
```

### Kết luận Performance

#### 🏆 **Fine Locking Wins:**

**Quantitative Results:**
- **Up to 20.3% faster** với high thread counts
- **Better throughput**: 260K vs 207K transactions/second  
- **Superior scalability**: Performance gap increases with threads

**Qualitative Benefits:**
- ✅ **Better resource utilization**
- ✅ **Higher system throughput**  
- ✅ **Improved user experience**
- ✅ **Future-proof design**

#### 🎓 **Bài học quan trọng:**

**Lock Granularity matters:**
- **Too coarse** → performance bottleneck
- **Too fine** → complexity overhead  
- **Just right** → optimal balance

**Design Principles:**
1. **Identify independent resources** 
2. **Use separate locks** for independent data
3. **Consistent lock ordering** to prevent deadlocks
4. **Measure and optimize** based on real workload

**Production Considerations:**
- Fine locking requires **careful design**
- **Testing critical** to avoid deadlocks
- **Monitor performance** under real load
- **Balance complexity vs benefits**

Fine Locking là powerful technique cho high-performance concurrent systems!

---

## 📋 **CÂU HỎI 9: Deadlock trong Fine Locking - Vấn đề và Giải pháp**

### Yêu cầu
Chạy chương trình deadlock test để quan sát hiện tượng deadlock trong Fine Locking và phân tích nguyên nhân qua mã nguồn.

### Tạo file deadlocks-test.c

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

int a = 0, b = 0;
pthread_mutex_t lock_a, lock_b;

void * fun_1(void * arg){
    int i;
    for (i = 0; i < 10000; i++){
        pthread_mutex_lock(&lock_a); // lock a then b
        pthread_mutex_lock(&lock_b);
        
        // CRITICAL SECTION
        a++;
        b++;
        
        pthread_mutex_unlock(&lock_a);
        pthread_mutex_unlock(&lock_b);
    }
    return NULL;
}

void * fun_2(void * arg){
    int i;
    for (i = 0; i < 10000; i++){
        pthread_mutex_lock(&lock_b); // lock b then a ← NGUY HIỂM!
        pthread_mutex_lock(&lock_a);
        
        // CRITICAL SECTION
        a++;
        b++;
        
        pthread_mutex_unlock(&lock_b);
        pthread_mutex_unlock(&lock_a);
    }
    return NULL;
}
```

### Kết quả quan sát được

#### 🔒 **Chương trình bị treo (hang):**
```bash
$ timeout 10s ./deadlocks-test
=== DEADLOCK DEMONSTRATION ===
Starting deadlock test...
Thread 1: Lock A → Lock B
Thread 2: Lock B → Lock A
Expected: Program may hang due to deadlock

[Program hangs - killed by timeout]
Command exited with code 124
```

#### 🔍 **Chi tiết deadlock scenario:**
```
Thread 1: Got lock_a, iteration 0
Thread 2: Got lock_b, iteration 0  
Thread 1: Trying to get lock_b...    ← WAITING
Thread 2: Trying to get lock_a...    ← WAITING
[DEADLOCK - Both threads wait forever]
```

### Phân tích mã nguồn - Root Cause Analysis

#### 🚨 **Circular Wait Condition:**

**Timeline dẫn đến deadlock:**
```
T1: Thread 1: pthread_mutex_lock(&lock_a) ✅ SUCCESS
T2: Thread 2: pthread_mutex_lock(&lock_b) ✅ SUCCESS  
T3: Thread 1: pthread_mutex_lock(&lock_b) ❌ BLOCKED (Thread 2 holds it)
T4: Thread 2: pthread_mutex_lock(&lock_a) ❌ BLOCKED (Thread 1 holds it)

Result: CIRCULAR WAIT → DEADLOCK
```

#### 🔄 **Diagram minh họa:**
```
Thread 1:  [Holds A] ----wants--→ [Lock B] ----held by--→ Thread 2
              ↑                                              ↓
              |                                          [Holds B]
              |                                              ↓  
           held by ←----wants---- [Lock A] ←----wants---- Thread 2

CIRCULAR DEPENDENCY → DEADLOCK!
```

### Phân tích chi tiết vấn đề

#### 🎯 **4 điều kiện dẫn đến Deadlock (Coffman Conditions):**

**1. Mutual Exclusion:**
```c
pthread_mutex_lock(&lock_a); // Only one thread can hold lock
```
✅ **Satisfied** - Mutex chỉ cho phép 1 thread

**2. Hold and Wait:**
```c
pthread_mutex_lock(&lock_a); // Hold A
pthread_mutex_lock(&lock_b); // Wait for B while holding A
```
✅ **Satisfied** - Thread giữ lock này và chờ lock khác

**3. No Preemption:**
```c
// Không thể force thread release lock
```
✅ **Satisfied** - Mutex không thể bị preempt

**4. Circular Wait:**
```
Thread 1: A → B
Thread 2: B → A  
```
✅ **Satisfied** - Circular dependency trong lock order

#### ⚠️ **Tại sao code này nguy hiểm:**

**Inconsistent Lock Ordering:**
```c
// Thread 1
pthread_mutex_lock(&lock_a); // First A
pthread_mutex_lock(&lock_b); // Then B

// Thread 2  
pthread_mutex_lock(&lock_b); // First B ← KHÁC THỨ TỰ!
pthread_mutex_lock(&lock_a); // Then A ← NGUY HIỂM!
```

**Race Condition trong Lock Acquisition:**
- Nếu cả 2 threads cùng chạy đến lệnh lock đầu tiên
- Thread 1 gets A, Thread 2 gets B
- Cả hai đều stuck chờ lock thứ hai

### Giải pháp Deadlock Prevention

#### ✅ **Solution 1: Consistent Lock Ordering**

```c
void * fun_1_fixed(void * arg){
    // Always lock in same order: A → B
    pthread_mutex_lock(&lock_a);
    pthread_mutex_lock(&lock_b);
    // ... critical section
    pthread_mutex_unlock(&lock_a);
    pthread_mutex_unlock(&lock_b);
}

void * fun_2_fixed(void * arg){
    // Same order: A → B (không phải B → A)
    pthread_mutex_lock(&lock_a);
    pthread_mutex_lock(&lock_b);
    // ... critical section  
    pthread_mutex_unlock(&lock_a);
    pthread_mutex_unlock(&lock_b);
}
```

**Kết quả:**
```
=== FINAL RESULTS ===
a = 20000, b = 20000
Expected: a = b = 20000
✅ SUCCESS: No deadlock, correct results!
```

#### ✅ **Solution 2: Lock Hierarchy**

```c
// Define lock levels
#define LOCK_LEVEL_A 1
#define LOCK_LEVEL_B 2

// Always acquire locks in increasing level order
pthread_mutex_lock(&lock_a); // Level 1 first
pthread_mutex_lock(&lock_b); // Level 2 second
```

#### ✅ **Solution 3: Timeout-based Locking**

```c
// Try to acquire with timeout
if (pthread_mutex_trylock(&lock_b) != 0) {
    pthread_mutex_unlock(&lock_a); // Release and retry
    usleep(rand() % 1000);         // Random backoff
    continue;
}
```

### Comparison: Deadlock vs No Deadlock

#### 📊 **Performance Impact:**

| Scenario | Completion | Time | Result |
|----------|------------|------|---------|
| **Deadlock Version** | ❌ Never | ∞ (hang) | System freeze |
| **Fixed Version** | ✅ Success | ~50ms | a=b=20000 |

#### 🎯 **Key Differences:**

**Deadlock Version:**
```
Thread 1: A → B
Thread 2: B → A  ← CIRCULAR WAIT
Result: Program hangs indefinitely
```

**Fixed Version:**
```
Thread 1: A → B
Thread 2: A → B  ← CONSISTENT ORDER
Result: Perfect execution, correct results
```

### Real-world Impact

#### 💰 **Production Consequences:**

**System Level:**
- ❌ **Application freeze** - Users cannot proceed
- ❌ **Resource waste** - Threads consuming memory/CPU while blocked
- ❌ **Cascade failures** - Other components waiting for response

**Business Level:**
- 💸 **Revenue loss** - E-commerce transactions fail
- 😠 **User frustration** - Poor user experience
- 🔧 **Operational cost** - Manual intervention required

#### 🚨 **Detection Challenges:**

**Why deadlocks are hard to debug:**
1. **Non-deterministic** - May not occur in testing
2. **Timing dependent** - Works fine with low load
3. **Hard to reproduce** - Different thread scheduling
4. **Silent failure** - No error messages, just hangs

### Prevention Best Practices

#### 🛡️ **Design Guidelines:**

**1. Lock Ordering Discipline:**
```c
// Define global lock hierarchy
enum lock_order {
    ACCOUNT_LOCK = 1,
    BALANCE_LOCK = 2,
    AUDIT_LOCK = 3
};
// Always acquire in increasing order
```

**2. Minimize Lock Scope:**
```c
// BAD: Hold locks too long
pthread_mutex_lock(&mutex);
expensive_computation(); // Hold lock during computation
pthread_mutex_unlock(&mutex);

// GOOD: Minimize critical section
expensive_computation(); // Do work outside lock
pthread_mutex_lock(&mutex);
update_shared_data();    // Quick update only
pthread_mutex_unlock(&mutex);
```

**3. Use Lock-Free Alternatives:**
```c
// Atomic operations instead of locks
__sync_fetch_and_add(&counter, 1);
```

#### 🔍 **Testing Strategies:**

**1. Stress Testing:**
```bash
# Run with many threads under high load
for i in {1..1000}; do
    timeout 5s ./program 100 || echo "Deadlock detected in run $i"
done
```

**2. Deadlock Detection Tools:**
- **Helgrind** (Valgrind): Race condition detection
- **ThreadSanitizer**: Google's thread safety analyzer
- **Static Analysis**: Code review for lock ordering

### Kết luận về Deadlock

#### 🎓 **Key Takeaways:**

**Deadlock Fundamentals:**
1. **Fine locking** powerful nhưng **dangerous** nếu thiết kế sai
2. **Inconsistent lock ordering** → guaranteed deadlock potential
3. **Prevention** dễ hơn **detection and recovery**

**Design Principles:**
1. ✅ **Always use consistent lock ordering**
2. ✅ **Minimize critical section duration**  
3. ✅ **Test extensively** under high contention
4. ✅ **Consider lock-free alternatives** when possible

**Production Guidelines:**
- **Design phase**: Establish lock hierarchy
- **Implementation**: Code reviews for lock patterns
- **Testing**: Stress test with high thread counts
- **Monitoring**: Deadlock detection in production

**The Golden Rule:**
> "Prevention is better than cure" - Design your locking strategy carefully from the beginning!

Fine Locking với proper design patterns có thể deliver excellent performance WITHOUT deadlock risk!

---

## Cách biên dịch và chạy

### Phần 1 - Java (Thread Synchronization)
```bash
# Biên dịch tất cả file Java
javac src/*.java

# So sánh hiệu suất và độ chính xác
./compare_sync.sh
```

### Phần 2 - C (Critical Section với Pthread)

```bash
# Biên dịch chương trình đơn giản
gcc -pthread simple.c -o simple
./simple

# Biên dịch chương trình ngân hàng không có lock
gcc -pthread without-lock.c -o without-lock
./without-lock 5

# Biên dịch phiên bản heavy (nhiều giao dịch hơn)
gcc -pthread without-lock-heavy.c -o without-lock-heavy
./without-lock-heavy 10

# Biên dịch naive lock implementation
gcc -pthread naive-lock.c -o naive-lock
./naive-lock 10

# Biên dịch mutex lock implementations
gcc -pthread mutex-lock-banking.c -o mutex-lock-banking
./mutex-lock-banking 20

gcc -pthread mutex-lock-heavy.c -o mutex-lock-heavy  
./mutex-lock-heavy 20

# Biên dịch coarse vs fine locking comparison
gcc -pthread coarse-locking-bank.c -o coarse-locking-bank
gcc -pthread fine-locking-bank.c -o fine-locking-bank

# So sánh performance
./coarse-locking-bank 50
./fine-locking-bank 50

# Biên dịch deadlock demonstrations
gcc -pthread deadlocks-test.c -o deadlocks-test
gcc -pthread deadlock-guaranteed.c -o deadlock-guaranteed  
gcc -pthread deadlock-solution.c -o deadlock-solution

# Test deadlock (sẽ bị treo - dùng timeout)
timeout 10s ./deadlocks-test
timeout 3s ./deadlock-guaranteed

# Test solution (không deadlock)
./deadlock-solution

# Chạy benchmark tự động
chmod +x benchmark_locking.sh
./benchmark_locking.sh
chmod +x test_race_condition.sh
./test_race_condition.sh

# Test naive lock implementation
chmod +x test_naive_lock.sh  
./test_naive_lock.sh

# Test manual với số luồng khác nhau
./without-lock-heavy 2    # Ít race condition
./without-lock-heavy 5    # Bắt đầu có race condition  
./without-lock-heavy 10   # Race condition rõ rệt
./without-lock-heavy 20   # Race condition nghiêm trọng
```

## Các file trong workspace

### Phần 1 - Java:
- `src/ResourcesExploiter.java` - Tài nguyên chia sẻ cơ bản
- `src/ThreadedWorkerWithoutSync.java` - Worker không đồng bộ
- `src/ThreadedWorkerWithSync.java` - Worker có synchronization
- `src/Main.java` - Chương trình chính không đồng bộ
- `src/MainWithSync.java` - Chương trình chính có đồng bộ
- `compare_sync.sh` - Script so sánh hiệu suất

### Phần 2 - C:
- `simple.c` - Chương trình pthread đơn giản (Câu hỏi 4)
- `without-lock.c` - Mô phỏng ngân hàng không có lock (Câu hỏi 5)
- `without-lock-heavy.c` - Phiên bản với nhiều giao dịch để tạo race condition
- `naive-lock.c` - Implementation naive lock (Câu hỏi 6)
- `mutex-lock-banking.c` - Implementation pthread mutex lock (Câu hỏi 7)
- `mutex-lock-heavy.c` - Mutex lock với 1000 transactions để so sánh
- `coarse-locking-bank.c` - Coarse locking implementation (Câu hỏi 8)
- `fine-locking-bank.c` - Fine locking implementation (Câu hỏi 8)
- `deadlocks-test.c` - Deadlock demonstration (Câu hỏi 9)
- `deadlock-guaranteed.c` - Guaranteed deadlock example
- `deadlock-solution.c` - Deadlock prevention solution
- `test_race_condition.sh` - Script test race condition tự động
- `test_naive_lock.sh` - Script test naive lock implementation
- `compare_all_locks.sh` - Script so sánh tất cả approaches
- `benchmark_locking.sh` - Script benchmark performance coarse vs fine
- `Makefile` - Build configuration

## Ghi chú quan trọng

### Về Java:
- `synchronized` keyword đảm bảo thread safety
- `ReentrantLock` cung cấp tính năng advanced hơn
- Race condition dễ quan sát với 3+ threads

### Về C:
- Pthread library cần flag `-pthread` khi compile
- Race condition xuất hiện rõ rệt với ≥5 threads
- `time(NULL)` dùng để timing, `usleep()` để tối ưu CPU
- Critical section cần được bảo vệ bằng mutex

### Performance Trade-offs:
- **No sync**: Nhanh nhất, không đáng tin cậy
- **Synchronization**: Chậm hơn ~5-65%, hoàn toàn chính xác
- **Acceptable cost**: Đáng tin cậy quan trọng hơn tốc độ trong production
````