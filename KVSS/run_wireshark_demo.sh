#!/bin/bash

# Script để chạy demo Wireshark cho KVSS
# Sử dụng: ./run_wireshark_demo.sh

echo "=========================================="
echo "KVSS Wireshark Demo Script"
echo "=========================================="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3."
    exit 1
fi

# Kiểm tra Wireshark
if ! command -v wireshark &> /dev/null; then
    echo "Warning: Wireshark not found. Please install Wireshark first."
    echo "Ubuntu/Debian: sudo apt install wireshark"
    echo "Windows: Download from https://www.wireshark.org/"
fi

echo "Starting KVSS Server in background..."
python3 kvss_server.py &
SERVER_PID=$!

# Đợi server khởi động
echo "Waiting for server to start..."
sleep 2

# Kiểm tra server có chạy không
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "Error: Server failed to start"
    exit 1
fi

echo "Server started with PID: $SERVER_PID"
echo "Server is running on 127.0.0.1:5050"

echo ""
echo "=========================================="
echo "WIRESHARK INSTRUCTIONS:"
echo "=========================================="
echo "1. Open Wireshark"
echo "2. Select interface 'lo' (loopback) or 'any'"
echo "3. Apply filter: tcp.port == 5050"
echo "4. Click 'Start capturing'"
echo "5. Press Enter here to continue with demo..."
echo "=========================================="

read -p "Press Enter when Wireshark is ready..."

echo ""
echo "Running demo tests..."

# Test 1: Short messages
echo "Test 1: Short messages"
python3 demo_wireshark.py short
sleep 1

# Test 2: Long messages  
echo "Test 2: Long messages"
python3 demo_wireshark.py long
sleep 1

# Test 3: Multiple requests
echo "Test 3: Multiple requests"
python3 demo_wireshark.py multiple
sleep 1

# Test 4: Error cases
echo "Test 4: Error cases"
python3 demo_wireshark.py error
sleep 1

# Test 5: Concurrent clients
echo "Test 5: Concurrent clients"
python3 demo_wireshark.py concurrent
sleep 1

echo ""
echo "=========================================="
echo "DEMO COMPLETED!"
echo "=========================================="
echo "Check Wireshark for packet analysis:"
echo "- TCP handshake (SYN, SYN-ACK, ACK)"
echo "- Data transmission with line-based protocol"
echo "- TCP segmentation for long messages"
echo "- Error handling"
echo "- Concurrent client handling"
echo ""
echo "Press Enter to stop server and exit..."

read -p ""

# Dừng server
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo "Server stopped. Demo completed!"
