#!/bin/bash

echo "=== TESTING RACE CONDITION WITH INCREASING THREADS ==="
echo "Mục tiêu: Tìm số luồng tối thiểu để xuất hiện race condition"
echo

# Test với số luồng tăng dần
for threads in 2 5 10 15 20 25 30; do
    echo "--- Testing with $threads threads ---"
    
    # Chạy 3 lần để tăng cơ hội phát hiện race condition
    consistent_count=0
    
    for run in 1 2 3; do
        echo -n "Run $run: "
        
        # Chạy và lấy kết quả
        result=$(./without-lock-heavy $threads)
        difference=$(echo "$result" | grep "Difference:" | cut -d' ' -f2)
        
        if [ "$difference" == "0" ]; then
            echo "✅ CONSISTENT"
            consistent_count=$((consistent_count + 1))
        else
            echo "❌ INCONSISTENT (diff: $difference)"
        fi
    done
    
    echo "Consistency: $consistent_count/3 runs"
    echo
    
    # Nếu có inconsistency, dừng để phân tích
    if [ $consistent_count -lt 3 ]; then
        echo "🎯 RACE CONDITION DETECTED with $threads threads!"
        echo "Running detailed analysis..."
        echo
        
        echo "=== DETAILED ANALYSIS ==="
        ./without-lock-heavy $threads
        break
    fi
done

echo
echo "=== CONCLUSION ==="
if [ $consistent_count -eq 3 ]; then
    echo "Cần tăng số luồng hoặc số giao dịch để tạo ra race condition"
    echo "Thử chạy manual với số luồng cao hơn (>30)"
else
    echo "Race condition xuất hiện khi có $threads luồng trở lên"
fi