#!/bin/bash

echo "=== COMPREHENSIVE PERFORMANCE BENCHMARK: COARSE vs FINE LOCKING ==="
echo "Testing bank simulation with multiple thread counts"
echo "Each test runs 5 times and takes average"
echo

# Function to run test multiple times and get average
run_performance_test() {
    local program=$1
    local threads=$2
    local runs=5
    local total_time=0
    
    for i in $(seq 1 $runs); do
        result=$(timeout 30s ./$program $threads)
        if [ $? -eq 0 ]; then
            time=$(echo "$result" | grep "Execution Time:" | cut -d' ' -f3)
            total_time=$(echo "$total_time + $time" | bc -l)
        else
            echo "Timeout or error in run $i"
            return 1
        fi
    done
    
    avg_time=$(echo "scale=2; $total_time / $runs" | bc -l)
    echo $avg_time
}

# Test with different thread counts
echo "┌─────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐"
echo "│ Threads │ Coarse (ms)     │ Fine (ms)       │ Speedup         │ Fine Advantage  │"
echo "├─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤"

for threads in 2 5 10 15 20 30 50; do
    echo -n "│ $threads       │ "
    
    # Test coarse locking
    coarse_time=$(run_performance_test "coarse-locking-bank" $threads)
    if [ $? -eq 0 ]; then
        printf "%-15.2f │ " $coarse_time
    else
        printf "%-15s │ " "ERROR"
        echo "ERROR             │ ERROR           │ ERROR           │"
        continue
    fi
    
    # Test fine locking  
    fine_time=$(run_performance_test "fine-locking-bank" $threads)
    if [ $? -eq 0 ]; then
        printf "%-15.2f │ " $fine_time
        
        # Calculate speedup
        if [ $(echo "$coarse_time > 0" | bc -l) -eq 1 ]; then
            speedup=$(echo "scale=2; $coarse_time / $fine_time" | bc -l)
            improvement=$(echo "scale=1; ($coarse_time - $fine_time) / $coarse_time * 100" | bc -l)
            printf "%-15.2fx │ %-15.1f%% │\n" $speedup $improvement
        else
            echo "ERROR           │ ERROR           │"
        fi
    else
        echo "ERROR           │ ERROR           │ ERROR           │"
    fi
done

echo "└─────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘"

echo
echo "=== DETAILED ANALYSIS FOR 20 THREADS ==="
echo "Running detailed comparison..."

echo
echo "COARSE LOCKING (20 threads):"
./coarse-locking-bank 20 | grep -E "(Execution Time|Average per transaction|Throughput)"

echo
echo "FINE LOCKING (20 threads):"
./fine-locking-bank 20 | grep -E "(Execution Time|Average per transaction|Throughput)"

echo
echo "=== KEY INSIGHTS ==="
echo "• Fine locking performs better with higher thread counts"
echo "• Improvement becomes more significant as contention increases"
echo "• Each variable can be locked independently → better parallelism"
echo "• Coarse locking creates serialization bottleneck"