#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>
#include <sys/time.h>

#define INIT_BALANCE 50
#define NUM_TRANS 1000

int balance = INIT_BALANCE;
int credits = 0;
int debits = 0;

// Fine Locking - 3 mutex riêng biệt
pthread_mutex_t b_lock; // cho biến balance
pthread_mutex_t c_lock; // cho biến credits  
pthread_mutex_t d_lock; // cho biến debits

void * transactions(void * args){
    int i, v;
    for(i = 0; i < NUM_TRANS; i++){
        // choose a random value
        srand(time(NULL) + pthread_self() + i);
        v = rand() % 50 + 1;
        
        // randomly choose to credit or debit
        if(rand() % 2){
            // CREDIT TRANSACTION - Fine Locking cho từng biến
            
            // Lock balance và cập nhật
            pthread_mutex_lock(&b_lock);
            balance = balance + v;
            pthread_mutex_unlock(&b_lock);
            
            // Lock credits và cập nhật
            pthread_mutex_lock(&c_lock);
            credits = credits + v;
            pthread_mutex_unlock(&c_lock);
            
        } else {
            // DEBIT TRANSACTION - Fine Locking cho từng biến
            
            // Lock balance và cập nhật
            pthread_mutex_lock(&b_lock);
            balance = balance - v;
            pthread_mutex_unlock(&b_lock);
            
            // Lock debits và cập nhật
            pthread_mutex_lock(&d_lock);
            debits = debits + v;
            pthread_mutex_unlock(&d_lock);
        }
    }
    return 0;
}

// Hàm đo thời gian execution
long long get_time_microseconds() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000000LL + tv.tv_usec;
}

int main(int argc, char * argv[]){
    int n_threads, i;
    pthread_t * threads;
    long long start_time, end_time, execution_time;
    
    // error check
    if(argc < 2){
        fprintf(stderr, "ERROR: Require number of threads\n");
        exit(1);
    }
    
    // convert string to int
    n_threads = atol(argv[1]);
    
    // error check
    if(n_threads <= 0){
        fprintf(stderr, "ERROR: Invalid value for number of threads\n");
        exit(1);
    }
    
    // Khởi tạo 3 mutex locks
    pthread_mutex_init(&b_lock, NULL);
    pthread_mutex_init(&c_lock, NULL);
    pthread_mutex_init(&d_lock, NULL);
    
    // allocate array of thread identifiers
    threads = calloc(n_threads, sizeof(pthread_t));
    
    printf("=== BANK SIMULATION WITH FINE LOCKING ===\n");
    printf("Initial Balance: %d\n", INIT_BALANCE);
    printf("Number of threads: %d\n", n_threads);
    printf("Transactions per thread: %d\n", NUM_TRANS);
    printf("Total transactions: %d\n", n_threads * NUM_TRANS);
    printf("Locking strategy: Fine Locking (3 separate mutexes)\n\n");
    
    // Bắt đầu đo thời gian
    start_time = get_time_microseconds();
    
    // start all threads
    for(i = 0; i < n_threads; i++){
        pthread_create(&threads[i], NULL, transactions, NULL);
    }
    
    // wait for all threads finish its jobs
    for(i = 0; i < n_threads; i++){
        pthread_join(threads[i], NULL);
    }
    
    // Kết thúc đo thời gian
    end_time = get_time_microseconds();
    execution_time = end_time - start_time;
    
    printf("=== RESULTS ===\n");
    printf("\tCredits:\t%d\n", credits);
    printf("\tDebits:\t\t%d\n", debits);
    printf("\nExpected Balance: %d + %d - %d = %d\n", 
           INIT_BALANCE, credits, debits, INIT_BALANCE + credits - debits);
    printf("Actual Balance:\t\t\t    %d\n", balance);
    
    int difference = balance - (INIT_BALANCE + credits - debits);
    printf("\nDifference: %d\n", difference);
    
    if(difference == 0) {
        printf("✅ CONSISTENT - Perfect thread synchronization with fine locking!\n");
    } else {
        printf("❌ INCONSISTENT - Fine locking failed unexpectedly!\n");
    }
    
    // Hiển thị thông tin timing
    printf("\n=== PERFORMANCE METRICS ===\n");
    printf("Execution Time: %lld microseconds (%.2f ms)\n", 
           execution_time, execution_time / 1000.0);
    printf("Average per transaction: %.2f microseconds\n", 
           (double)execution_time / (n_threads * NUM_TRANS));
    printf("Throughput: %.0f transactions/second\n", 
           (n_threads * NUM_TRANS * 1000000.0) / execution_time);
    
    // Hủy và giải phóng 3 mutex locks
    pthread_mutex_destroy(&b_lock);
    pthread_mutex_destroy(&c_lock);
    pthread_mutex_destroy(&d_lock);
    
    // free array
    free(threads);
    return 0;
}