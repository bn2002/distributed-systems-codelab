#!/bin/bash

echo "=== TESTING NAIVE LOCK WITH MULTIPLE RUNS ==="
echo "Tìm kiếm race condition trong naive lock implementation"
echo

# Test với số luồng và số lần chạy khác nhau
for threads in 2 5 10 15 20; do
    echo "--- Testing with $threads threads ---"
    
    success_count=0
    total_runs=10
    
    for run in $(seq 1 $total_runs); do
        # Chạy và lấy kết quả
        result=$(./naive-lock $threads)
        shared=$(echo "$result" | grep "Shared:" | cut -d' ' -f2)
        expected=$(echo "$result" | grep "Expect:" | cut -d' ' -f2)
        
        if [ "$shared" = "$expected" ]; then
            echo -n "✅"
            success_count=$((success_count + 1))
        else
            echo -n "❌"
            echo " (Run $run: $shared/$expected)"
        fi
    done
    
    echo
    echo "Success rate: $success_count/$total_runs ($(( success_count * 100 / total_runs ))%)"
    
    if [ $success_count -lt $total_runs ]; then
        echo "🎯 RACE CONDITION DETECTED with $threads threads!"
        echo
        echo "=== DETAILED ANALYSIS ==="
        ./naive-lock $threads
        echo
        echo "=== ROOT CAUSE ANALYSIS ==="
        echo "Naive lock có race condition trong chính việc kiểm tra và set lock:"
        echo "1. Thread A: while(lock > 0) -> lock = 0, OK"
        echo "2. Thread B: while(lock > 0) -> lock = 0, OK (cùng lúc!)"  
        echo "3. Thread A: lock = 1"
        echo "4. Thread B: lock = 1 (ghi đè!)"
        echo "5. Cả hai thread đều vào critical section!"
        break
    fi
    
    echo
done

if [ $success_count -eq $total_runs ]; then
    echo "=== STRESS TEST ===  "
    echo "Thử với nhiều threads hơn và chạy liên tục..."
    
    for threads in 50 100; do
        echo "Testing $threads threads:"
        for i in {1..5}; do
            result=$(./naive-lock $threads)
            shared=$(echo "$result" | grep "Shared:" | cut -d' ' -f2)  
            expected=$(echo "$result" | grep "Expect:" | cut -d' ' -f2)
            
            if [ "$shared" != "$expected" ]; then
                echo "❌ FOUND RACE CONDITION with $threads threads!"
                echo "   Shared: $shared, Expected: $expected"
                break 2
            else
                echo "✅ Run $i: $shared/$expected"
            fi
        done
    done
fi