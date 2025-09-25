#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>

#define INIT_BALANCE 50
#define NUM_TRANS 100

int balance = INIT_BALANCE;
int credits = 0;
int debits = 0;

void * transactions(void * args){
    int i, v;
    for(i = 0; i < NUM_TRANS; i++){
        // choose a random value
        srand(time(NULL) + pthread_self()); // Thêm thread ID để tạo seed khác nhau
        v = rand() % NUM_TRANS;
        
        // randomly choose to credit or debit
        if(rand() % 2){
            // credit
            balance = balance + v;
            credits = credits + v;
        } else {
            // debit
            balance = balance - v;
            debits = debits + v;
        }
    }
    return 0;
}

int main(int argc, char * argv[]){
    int n_threads, i;
    pthread_t * threads;
    
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
    
    // allocate array of thread identifiers
    threads = calloc(n_threads, sizeof(pthread_t));
    
    printf("=== BANK SIMULATION WITHOUT LOCKING ===\n");
    printf("Initial Balance: %d\n", INIT_BALANCE);
    printf("Number of threads: %d\n", n_threads);
    printf("Transactions per thread: %d\n", NUM_TRANS);
    printf("Total transactions: %d\n\n", n_threads * NUM_TRANS);
    
    // start all threads
    for(i = 0; i < n_threads; i++){
        pthread_create(&threads[i], NULL, transactions, NULL);
    }
    
    // wait for all threads finish its jobs
    for(i = 0; i < n_threads; i++){
        pthread_join(threads[i], NULL);
    }
    
    printf("=== RESULTS ===\n");
    printf("\tCredits:\t%d\n", credits);
    printf("\tDebits:\t\t%d\n", debits);
    printf("\nExpected Balance: %d + %d - %d = %d\n", 
           INIT_BALANCE, credits, debits, INIT_BALANCE + credits - debits);
    printf("Actual Balance:\t\t\t    %d\n", balance);
    
    int difference = balance - (INIT_BALANCE + credits - debits);
    printf("\nDifference: %d\n", difference);
    
    if(difference == 0) {
        printf("✅ CONSISTENT - No race condition detected\n");
    } else {
        printf("❌ INCONSISTENT - Race condition detected!\n");
    }
    
    // free array
    free(threads);
    return 0;
}