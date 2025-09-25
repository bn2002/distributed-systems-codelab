#!/bin/bash

echo "=== COMPREHENSIVE COMPARISON: NO-LOCK vs NAIVE-LOCK vs MUTEX-LOCK ==="
echo "Testing bank simulation with 20 threads, 10 runs each"
echo

# Test parameters
THREADS=20
RUNS=10

echo "--- 1. WITHOUT LOCKING (Race Condition Expected) ---"
success_count=0
for i in $(seq 1 $RUNS); do
    result=$(./without-lock-heavy $THREADS 2>/dev/null)
    shared=$(echo "$result" | grep "Actual Balance:" | awk '{print $3}')
    expected=$(echo "$result" | grep "Expected Balance:" | awk '{print $8}')
    
    if [ "$shared" = "$expected" ]; then
        echo "Run $i: ✅ $shared/$expected"
        success_count=$((success_count + 1))
    else
        echo "Run $i: ❌ $shared/$expected (diff: $((shared - expected)))"
    fi
done
echo "Success rate: $success_count/$RUNS ($(( success_count * 100 / RUNS ))%)"
echo

echo "--- 2. NAIVE LOCK (Intermittent Failures Expected) ---"
success_count=0
for i in $(seq 1 $RUNS); do
    result=$(./naive-lock $THREADS)
    shared=$(echo "$result" | grep "Shared:" | cut -d' ' -f2)
    expected=$(echo "$result" | grep "Expect:" | cut -d' ' -f2)
    
    if [ "$shared" = "$expected" ]; then
        echo "Run $i: ✅ $shared/$expected"
        success_count=$((success_count + 1))
    else
        echo "Run $i: ❌ $shared/$expected (lost: $((expected - shared)))"
    fi
done
echo "Success rate: $success_count/$RUNS ($(( success_count * 100 / RUNS ))%)"
echo

echo "--- 3. MUTEX LOCK (100% Success Expected) ---"
success_count=0
total_time=0
for i in $(seq 1 $RUNS); do
    start_time=$(date +%s%N)
    result=$(./mutex-lock-banking $THREADS)
    end_time=$(date +%s%N)
    
    execution_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    total_time=$((total_time + execution_time))
    
    if echo "$result" | grep -q "CONSISTENT"; then
        echo "Run $i: ✅ PERFECT (${execution_time}ms)"
        success_count=$((success_count + 1))
    else
        echo "Run $i: ❌ FAILED (${execution_time}ms)"
    fi
done
avg_time=$((total_time / RUNS))
echo "Success rate: $success_count/$RUNS ($(( success_count * 100 / RUNS ))%)"
echo "Average execution time: ${avg_time}ms"
echo

echo "=== SUMMARY COMPARISON ==="
echo "┌─────────────────┬─────────────┬─────────────┬─────────────────────┐"
echo "│ Approach        │ Correctness │ Performance │ Use Case            │"
echo "├─────────────────┼─────────────┼─────────────┼─────────────────────┤"
echo "│ No Lock         │ ❌ 0%        │ ⚡ Fastest   │ 🚫 Never use        │"
echo "│ Naive Lock      │ ⚠️ ~90%      │ 🐌 Slowest   │ 🚫 Educational only │"
echo "│ Mutex Lock      │ ✅ 100%      │ 🚀 Good      │ ✅ Production ready │"
echo "└─────────────────┴─────────────┴─────────────┴─────────────────────┘"
echo
echo "🎯 CONCLUSION: Use pthread_mutex for reliable thread synchronization!"