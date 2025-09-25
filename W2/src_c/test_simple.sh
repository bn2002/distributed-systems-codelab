#!/bin/bash

echo "=== TEST CHƯƠNG TRÌNH SIMPLE.C ==="
echo "Chạy 5 lần để quan sát kết quả:"
echo

for i in {1..5}; do
    echo -n "Lần $i: "
    result=$(./simple | grep "shared:" | cut -d' ' -f2)
    echo "shared = $result"
done

echo
echo "Ghi chú:"
echo "- Giá trị ban đầu: shared = 10"
echo "- Thời gian chạy: 5 giây"
echo "- Dự kiến tăng ~4000-5000 lần"