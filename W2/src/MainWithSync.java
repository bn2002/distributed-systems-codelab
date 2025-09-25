/**
 * Lớp chính chứa phương thức main - PHIÊN BẢN CÓ SYNCHRONIZATION
 * Khởi tạo và chạy các luồng với cơ chế đồng bộ hóa
 */
public class MainWithSync {
    public static void main(String[] args) {
        System.out.println("=== CHƯƠNG TRÌNH ĐỒNG BỘ LUỒNG - CÓ SYNCHRONIZATION ===\n");
        
        // Tạo một thực thể resource với giá trị khởi tạo là 0
        ResourcesExploiter resource = new ResourcesExploiter(0);
        
        // Tạo 3 luồng worker chia sẻ cùng một tài nguyên - SỬ DỤNG SYNC
        ThreadedWorkerWithSync worker1 = new ThreadedWorkerWithSync(resource);
        ThreadedWorkerWithSync worker2 = new ThreadedWorkerWithSync(resource);
        ThreadedWorkerWithSync worker3 = new ThreadedWorkerWithSync(resource);
        
        System.out.println("Giá trị ban đầu của resource: " + resource.getRsc());
        System.out.println("Khởi động 3 luồng ĐỒNG BỘ, mỗi luồng thực hiện 1000 lần exploit()...");
        
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
        
        if (resource.getRsc() == 3000) {
            System.out.println("✓ Kết quả ĐÚNG - Synchronization hoạt động!");
        } else {
            System.out.println("✗ Kết quả SAI - Có lỗi trong synchronization!");
        }
    }
}