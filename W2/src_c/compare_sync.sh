#!/bin/bash

echo "=== SO SÁNH HIỆU SUẤT VÀ ĐỘ CHÍNH XÁC ==="
echo "Testing: 3 threads x 1000 operations = 3000 (expected)"
echo ""

cd /root/Work/HPT/W2/src

echo "📊 KHÔNG CÓ SYNCHRONIZATION (ThreadedWorkerWithoutSync):"
correct_without=0
total_time_without=0

for i in {1..10}
do
    start_time=$(date +%s%N)
    result=$(java Main | grep "Giá trị cuối cùng của resource:" | sed 's/.*: //')
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 ))
    total_time_without=$((total_time_without + duration))
    
    if [ "$result" = "3000" ]; then
        status="✓ ĐÚNG"
        correct_without=$((correct_without + 1))
    else
        status="✗ SAI"
    fi
    echo "  Lần $i: $result/3000 ($duration ms) - $status"
done

echo ""
echo "📊 CÓ SYNCHRONIZATION (ThreadedWorkerWithSync):"
correct_with=0
total_time_with=0

for i in {1..10}
do
    start_time=$(date +%s%N)
    result=$(java MainWithSync | grep "Giá trị cuối cùng của resource:" | sed 's/.*: //')
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 ))
    total_time_with=$((total_time_with + duration))
    
    if [ "$result" = "3000" ]; then
        status="✓ ĐÚNG"
        correct_with=$((correct_with + 1))
    else
        status="✗ SAI"
    fi
    echo "  Lần $i: $result/3000 ($duration ms) - $status"
done

echo ""
echo "=== TỔNG KẾT ==="
echo "🎯 ĐỘ CHÍNH XÁC:"
echo "  - KHÔNG Sync: $correct_without/10 lần đúng ($(( correct_without * 10 ))%)"
echo "  - CÓ Sync:    $correct_with/10 lần đúng ($(( correct_with * 10 ))%)"

avg_time_without=$((total_time_without / 10))
avg_time_with=$((total_time_with / 10))

echo ""
echo "⏱️  THỜI GIAN TRUNG BÌNH:"
echo "  - KHÔNG Sync: $avg_time_without ms"
echo "  - CÓ Sync:    $avg_time_with ms"

if [ $avg_time_with -gt $avg_time_without ]; then
    overhead=$(( ((avg_time_with - avg_time_without) * 100) / avg_time_without ))
    echo "  - Overhead của Sync: +$overhead%"
fi