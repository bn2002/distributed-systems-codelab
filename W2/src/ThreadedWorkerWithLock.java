/**
 * Lớp ThreadedWorkerWithLock kế thừa từ Thread
 * Thực hiện công việc trên tài nguyên chia sẻ với cơ chế ReentrantLock
 * Tương tự ThreadedWorkerWithoutSync nhưng sử dụng ResourcesExploiterWithLock
 */
public class ThreadedWorkerWithLock extends Thread {
    // Biến private chứa tham chiếu đến tài nguyên chia sẻ với Lock
    private ResourcesExploiterWithLock rExp;
    
    /**
     * Phương thức khởi tạo
     * @param resource tài nguyên chia sẻ có hỗ trợ Lock
     */
    public ThreadedWorkerWithLock(ResourcesExploiterWithLock resource) {
        this.rExp = resource;
    }
    
    /**
     * Phương thức run() được override từ lớp Thread
     * Thực hiện 1000 lần gọi exploit() trên tài nguyên chia sẻ
     * Lock được handle bởi ResourcesExploiterWithLock.exploit()
     */
    @Override
    public void run() {
        // Thực hiện 1000 lần exploit()
        // Mỗi lần gọi exploit() sẽ acquire và release lock tự động
        for (int i = 0; i < 1000; i++) {
            rExp.exploit();
        }
        
        // In thông tin debug khi thread hoàn thành (chỉ khi tên thread dài)
        if (Thread.currentThread().getName().length() > 2) {
            System.out.println("Thread " + Thread.currentThread().getName() + " completed 1000 operations");
        }
    }
}