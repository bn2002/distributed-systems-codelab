/**
 * Lớp chính chứa phương thức main - PHIÊN BẢN CÓ REENTRANTLOCK
 * Khởi tạo và chạy các luồng với cơ chế ReentrantLock
 */
public class MainWithLock {
    public static void main(String[] args) {
        System.out.println("=== CHƯƠNG TRÌNH ĐỒNG BỘ LUỒNG - SỬ DỤNG REENTRANTLOCK ===\n");
        
        // Tạo một thực thể resource với ReentrantLock, giá trị khởi tạo là 0
        ResourcesExploiterWithLock resource = new ResourcesExploiterWithLock(0);
        
        // Tạo 3 luồng worker chia sẻ cùng một tài nguyên - SỬ DỤNG LOCK
        ThreadedWorkerWithLock worker1 = new ThreadedWorkerWithLock(resource);
        ThreadedWorkerWithLock worker2 = new ThreadedWorkerWithLock(resource);
        ThreadedWorkerWithLock worker3 = new ThreadedWorkerWithLock(resource);
        
        // Đặt tên cho các thread để dễ debug
        worker1.setName("Worker-1");
        worker2.setName("Worker-2");
        worker3.setName("Worker-3");
        
        System.out.println("Giá trị ban đầu của resource: " + resource.getRsc());
        System.out.println("Khởi động 3 luồng với ReentrantLock, mỗi luồng thực hiện 1000 lần exploit()...");
        
        // Ghi lại thời gian bắt đầu
        long startTime = System.currentTimeMillis();
        
        // Khởi động 3 luồng
        worker1.start();
        worker2.start();
        worker3.start();
        
        try {
            // Chờ tất cả các luồng hoàn thành công việc
            worker1.join();
            worker2.join();
            worker3.join();
        } catch (InterruptedException e) {
            System.out.println("Luồng chính bị ngắt: " + e.getMessage());
        }
        
        // Ghi lại thời gian kết thúc
        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;
        
        // In kết quả cuối cùng
        System.out.println("\nKết quả:");
        System.out.println("Giá trị cuối cùng của resource: " + resource.getRsc());
        System.out.println("Giá trị mong đợi: " + (3 * 1000)); // 3 luồng x 1000 lần = 3000
        System.out.println("Thời gian thực hiện: " + duration + " ms");
        System.out.println("Lock status - Locked: " + resource.isLocked() + 
                          ", Queue length: " + resource.getQueueLength());
        
        if (resource.getRsc() == 3000) {
            System.out.println("✓ Kết quả ĐÚNG - ReentrantLock hoạt động!");
        } else {
            System.out.println("✗ Kết quả SAI - Có lỗi trong ReentrantLock implementation!");
        }
    }
}