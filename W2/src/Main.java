/**
 * Lớp chính chứa phương thức main
 * Khởi tạo và chạy các luồng để minh họa vấn đề race condition
 */
public class Main {
    public static void main(String[] args) {
        System.out.println("=== CHƯƠNG TRÌNH ĐỒNG BỘ LUỒNG - KHÔNG CÓ SYNCHRONIZATION ===\n");
        
        // Tạo một thực thể resource với giá trị khởi tạo là 0
        ResourcesExploiter resource = new ResourcesExploiter(0);
        
        // Tạo 3 luồng worker chia sẻ cùng một tài nguyên
        ThreadedWorkerWithoutSync worker1 = new ThreadedWorkerWithoutSync(resource);
        ThreadedWorkerWithoutSync worker2 = new ThreadedWorkerWithoutSync(resource);
        ThreadedWorkerWithoutSync worker3 = new ThreadedWorkerWithoutSync(resource);
        
        System.out.println("Giá trị ban đầu của resource: " + resource.getRsc());
        System.out.println("Khởi động 3 luồng, mỗi luồng thực hiện 1000 lần exploit()...");
        
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
        
        // In kết quả cuối cùng
        System.out.println("\nKết quả:");
        System.out.println("Giá trị cuối cùng của resource: " + resource.getRsc());
        System.out.println("Giá trị mong đợi: " + (3 * 1000)); // 3 luồng x 1000 lần = 3000
        
        if (resource.getRsc() == 3000) {
            System.out.println("✓ Kết quả đúng như mong đợi");
        } else {
            System.out.println("✗ Kết quả không đúng như mong đợi - Race condition đã xảy ra!");
        }
    }
}