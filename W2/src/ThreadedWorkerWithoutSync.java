/**
 * Lớp ThreadedWorkerWithoutSync kế thừa từ Thread
 * Thực hiện công việc trên tài nguyên chia sẻ mà KHÔNG có đồng bộ hóa
 */
public class ThreadedWorkerWithoutSync extends Thread {
    // Biến private chứa tham chiếu đến tài nguyên chia sẻ
    private ResourcesExploiter rExp;
    
    /**
     * Phương thức khởi tạo
     * @param resource tài nguyên chia sẻ
     */
    public ThreadedWorkerWithoutSync(ResourcesExploiter resource) {
        this.rExp = resource;
    }
    
    /**
     * Phương thức run() được override từ lớp Thread
     * Thực hiện 1000 lần gọi exploit() trên tài nguyên chia sẻ
     */
    @Override
    public void run() {
        // Thực hiện 1000 lần exploit()
        for (int i = 0; i < 1000; i++) {
            rExp.exploit();
        }
    }
}