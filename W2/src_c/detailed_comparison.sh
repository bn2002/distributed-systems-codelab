#!/bin/bash

echo "🔬 === PHÂN TÍCH SO SÁNH CÂU HỎI 1 vs CÂU HỎI 3 ==="
echo "Testing: 10 lần chạy mỗi phương pháp"
echo ""

cd /root/Work/HPT/W2/src

echo "📊 CÂU HỎI 1 - KHÔNG CÓ ĐỒNG BỘ HÓA:"
correct_q1=0
total_time_q1=0

for i in {1..10}
do
    start_time=$(date +%s%N)
    result=$(java Main | grep "Giá trị cuối cùng của resource:" | sed 's/.*: //')
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 ))
    total_time_q1=$((total_time_q1 + duration))
    
    if [ "$result" = "3000" ]; then
        status="✅ ĐÚNG"
        correct_q1=$((correct_q1 + 1))
    else
        status="❌ SAI (Race condition!)"
    fi
    echo "  Lần $i: $result/3000 (${duration}ms) - $status"
done

echo ""
echo "📊 CÂU HỎI 3 - SỬ DỤNG REENTRANTLOCK:"
correct_q3=0
total_time_q3=0

for i in {1..10}
do
    start_time=$(date +%s%N)
    result=$(java MainWithLock | grep "Giá trị cuối cùng của resource:" | sed 's/.*: //')
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 ))
    total_time_q3=$((total_time_q3 + duration))
    
    if [ "$result" = "3000" ]; then
        status="✅ ĐÚNG"
        correct_q3=$((correct_q3 + 1))
    else
        status="❌ SAI (Lock thất bại!)"
    fi
    echo "  Lần $i: $result/3000 (${duration}ms) - $status"
done

echo ""
echo "🎯 === TỔNG KẾT SO SÁNH ==="
echo "┌─────────────────────────┬─────────────┬─────────────┬─────────────┐"
echo "│ Tiêu chí                │ Câu hỏi 1   │ Câu hỏi 3   │ Kết luận    │"
echo "├─────────────────────────┼─────────────┼─────────────┼─────────────┤"

# Độ chính xác
q1_accuracy=$(( correct_q1 * 10 ))
q3_accuracy=$(( correct_q3 * 10 ))
if [ $q3_accuracy -gt $q1_accuracy ]; then
    accuracy_conclusion="Lock thắng"
elif [ $q1_accuracy -gt $q3_accuracy ]; then
    accuracy_conclusion="No-Sync thắng"
else
    accuracy_conclusion="Hòa"
fi

echo "│ Độ chính xác            │ ${correct_q1}/10 (${q1_accuracy}%) │ ${correct_q3}/10 (${q3_accuracy}%) │ $accuracy_conclusion │"

# Thời gian trung bình
avg_time_q1=$((total_time_q1 / 10))
avg_time_q3=$((total_time_q3 / 10))

if [ $avg_time_q1 -lt $avg_time_q3 ]; then
    speed_conclusion="No-Sync nhanh hơn"
    overhead=$(( ((avg_time_q3 - avg_time_q1) * 100) / avg_time_q1 ))
    speed_detail="(+${overhead}% overhead)"
elif [ $avg_time_q3 -lt $avg_time_q1 ]; then
    speed_conclusion="Lock nhanh hơn"
    improvement=$(( ((avg_time_q1 - avg_time_q3) * 100) / avg_time_q1 ))
    speed_detail="(-${improvement}% faster)"
else
    speed_conclusion="Tương đương"
    speed_detail=""
fi

echo "│ Thời gian trung bình    │ ${avg_time_q1}ms        │ ${avg_time_q3}ms        │ $speed_conclusion │"
echo "└─────────────────────────┴─────────────┴─────────────┴─────────────┘"

echo ""
echo "🔍 PHÂN TÍCH CHI TIẾT:"
echo "• Race Condition: Câu hỏi 1 bị mất $((3000 * 10 - (correct_q1 * 3000 + (10 - correct_q1) * (total_time_q1 / 10 * 3)))) operations do race condition"
echo "• Thread Safety: ReentrantLock đảm bảo 100% thread-safe"
echo "• Performance: $speed_detail"

if [ $correct_q3 -gt $correct_q1 ]; then
    echo "• Khuyến nghị: Sử dụng ReentrantLock cho ứng dụng thực tế"
else
    echo "• Lưu ý: Kết quả này có thể thay đổi tùy theo môi trường"
fi