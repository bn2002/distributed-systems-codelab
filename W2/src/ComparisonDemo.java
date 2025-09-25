/**
 * Chương trình demo tích hợp so sánh KHÔNG SYNC vs CÓ SYNC
 */
public class ComparisonDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🧪 === DEMO SO SÁNH SYNCHRONIZATION ===");
        System.out.println("Thực hiện: 3 threads × 1000 operations = 3000 (expected)\n");
        
        // Test WITHOUT Synchronization
        System.out.println("🚫 KHÔNG CÓ SYNCHRONIZATION:");
        testWithoutSync();
        
        System.out.println("\n" + "=".repeat(50) + "\n");
        
        // Test WITH Synchronization  
        System.out.println("🔒 CÓ SYNCHRONIZATION:");
        testWithSync();
        
        System.out.println("\n🎯 KẾT LUẬN:");
        System.out.println("- KHÔNG Sync: Kết quả không đoán trước, có race condition");
        System.out.println("- CÓ Sync: Luôn đúng 3000, an toàn thread-safe");
    }
    
    private static void testWithoutSync() throws InterruptedException {
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
            int result = resource.getRsc();
            
            String status = (result == 3000) ? "✅ ĐÚNG" : "❌ SAI";
            System.out.printf("  Test %d: %d/3000 (%dms) - %s%n", test, result, duration, status);
        }
    }
    
    private static void testWithSync() throws InterruptedException {
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
            int result = resource.getRsc();
            
            String status = (result == 3000) ? "✅ ĐÚNG" : "❌ SAI";
            System.out.printf("  Test %d: %d/3000 (%dms) - %s%n", test, result, duration, status);
        }
    }
}