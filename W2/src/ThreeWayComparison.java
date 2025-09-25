/**
 * Demo so sánh 3 cách tiếp cận đồng bộ hóa:
 * 1. KHÔNG có đồng bộ hóa (Race condition)
 * 2. Sử dụng synchronized
 * 3. Sử dụng ReentrantLock
 */
public class ThreeWayComparison {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🧪 === SO SÁNH 3 CÁCH TIẾP CẬN ĐỒNG BỘ HÓA ===");
        System.out.println("Thực hiện: 3 threads × 1000 operations = 3000 (expected)\n");
        
        // 1. Test WITHOUT Synchronization
        System.out.println("🚫 1. KHÔNG CÓ ĐỒNG BỘ HÓA (Race Condition):");
        testWithoutSync();
        
        System.out.println("\n" + "=".repeat(60) + "\n");
        
        // 2. Test WITH Synchronized
        System.out.println("🔒 2. SỬ DỤNG SYNCHRONIZED:");
        testWithSync();
        
        System.out.println("\n" + "=".repeat(60) + "\n");
        
        // 3. Test WITH ReentrantLock
        System.out.println("🔐 3. SỬ DỤNG REENTRANTLOCK:");
        testWithLock();
        
        System.out.println("\n🎯 TỔNG KẾT:");
        System.out.println("┌─────────────────┬──────────────┬─────────────┬─────────────┐");
        System.out.println("│ Phương pháp     │ Độ chính xác │ Hiệu suất   │ Phức tạp    │");
        System.out.println("├─────────────────┼──────────────┼─────────────┼─────────────┤");
        System.out.println("│ Không đồng bộ   │ ❌ Không ổn  │ ⚡ Nhanh    │ 😊 Đơn giản │");
        System.out.println("│ Synchronized    │ ✅ Hoàn hảo  │ 🐌 Chậm hơn │ 😊 Đơn giản │");
        System.out.println("│ ReentrantLock   │ ✅ Hoàn hảo  │ 🚀 Nhanh   │ 🤔 Phức tạp │");
        System.out.println("└─────────────────┴──────────────┴─────────────┴─────────────┘");
    }
    
    private static void testWithoutSync() throws InterruptedException {
        int correctResults = 0;
        long totalTime = 0;
        
        for (int test = 1; test <= 5; test++) {
            ResourcesExploiter resource = new ResourcesExploiter(0);
            
            ThreadedWorkerWithoutSync worker1 = new ThreadedWorkerWithoutSync(resource);
            ThreadedWorkerWithoutSync worker2 = new ThreadedWorkerWithoutSync(resource);  
            ThreadedWorkerWithoutSync worker3 = new ThreadedWorkerWithoutSync(resource);
            
            long startTime = System.currentTimeMillis();
            
            worker1.start();
            worker2.start();
            worker3.start();
            
            worker1.join();
            worker2.join();
            worker3.join();
            
            long duration = System.currentTimeMillis() - startTime;
            totalTime += duration;
            int result = resource.getRsc();
            
            if (result == 3000) correctResults++;
            
            String status = (result == 3000) ? "✅" : "❌";
            System.out.printf("  Test %d: %4d/3000 (%2dms) %s%n", test, result, duration, status);
        }
        
        System.out.printf("  📊 Tổng kết: %d/5 đúng (%.0f%%), Thời gian TB: %.1fms%n", 
                         correctResults, (correctResults * 100.0 / 5), (totalTime / 5.0));
    }
    
    private static void testWithSync() throws InterruptedException {
        int correctResults = 0;
        long totalTime = 0;
        
        for (int test = 1; test <= 5; test++) {
            ResourcesExploiter resource = new ResourcesExploiter(0);
            
            ThreadedWorkerWithSync worker1 = new ThreadedWorkerWithSync(resource);
            ThreadedWorkerWithSync worker2 = new ThreadedWorkerWithSync(resource);
            ThreadedWorkerWithSync worker3 = new ThreadedWorkerWithSync(resource);
            
            long startTime = System.currentTimeMillis();
            
            worker1.start();
            worker2.start();
            worker3.start();
            
            worker1.join();
            worker2.join();
            worker3.join();
            
            long duration = System.currentTimeMillis() - startTime;
            totalTime += duration;
            int result = resource.getRsc();
            
            if (result == 3000) correctResults++;
            
            String status = (result == 3000) ? "✅" : "❌";
            System.out.printf("  Test %d: %4d/3000 (%2dms) %s%n", test, result, duration, status);
        }
        
        System.out.printf("  📊 Tổng kết: %d/5 đúng (%.0f%%), Thời gian TB: %.1fms%n", 
                         correctResults, (correctResults * 100.0 / 5), (totalTime / 5.0));
    }
    
    private static void testWithLock() throws InterruptedException {
        int correctResults = 0;
        long totalTime = 0;
        
        for (int test = 1; test <= 5; test++) {
            ResourcesExploiterWithLock resource = new ResourcesExploiterWithLock(0);
            
            ThreadedWorkerWithLock worker1 = new ThreadedWorkerWithLock(resource);
            ThreadedWorkerWithLock worker2 = new ThreadedWorkerWithLock(resource);
            ThreadedWorkerWithLock worker3 = new ThreadedWorkerWithLock(resource);
            
            // Tắt debug output
            worker1.setName("W1");
            worker2.setName("W2");
            worker3.setName("W3");
            
            long startTime = System.currentTimeMillis();
            
            worker1.start();
            worker2.start();
            worker3.start();
            
            worker1.join();
            worker2.join();
            worker3.join();
            
            long duration = System.currentTimeMillis() - startTime;
            totalTime += duration;
            int result = resource.getRsc();
            
            if (result == 3000) correctResults++;
            
            String status = (result == 3000) ? "✅" : "❌";
            System.out.printf("  Test %d: %4d/3000 (%2dms) %s%n", test, result, duration, status);
        }
        
        System.out.printf("  📊 Tổng kết: %d/5 đúng (%.0f%%), Thời gian TB: %.1fms%n", 
                         correctResults, (correctResults * 100.0 / 5), (totalTime / 5.0));
    }
}