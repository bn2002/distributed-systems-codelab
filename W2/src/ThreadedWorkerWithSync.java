/**
 * Lớp ThreadedWorkerWithSync kế thừa từ Thread
 * Thực hiện công việc trên tài nguyên chia sẻ với cơ chế ĐỒNG BỘ HÓA
 * Sử dụng synchronized để bảo vệ vùng găng (critical section)
 */
public class ThreadedWorkerWithSync extends Thread {
    // Biến private chứa tham chiếu đến tài nguyên chia sẻ
    private ResourcesExploiter rExp;
    
    /**
     * Phương thức khởi tạo
     * @param resource tài nguyên chia sẻ
     */
    public ThreadedWorkerWithSync(ResourcesExploiter resource) {
        this.rExp = resource;
    }
    
    /**
     * Phương thức run() được override từ lớp Thread
     * Thực hiện 1000 lần gọi exploit() trên tài nguyên chia sẻ
     * SỬ DỤNG SYNCHRONIZED để đảm bảo chỉ một luồng truy cập tại một thời điểm
     */
    @Override
    public void run() {
        // Sử dụng synchronized trên đối tượng rExp
        // Đảm bảo toàn bộ vòng lặp được thực hiện nguyên tử (atomically)
        synchronized(rExp) {
            for (int i = 0; i < 1000; i++) {
                rExp.exploit();
            }
        }
    }
}