#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

int a = 0, b = 0;
pthread_mutex_t lock_a, lock_b;
int thread1_iterations = 0;
int thread2_iterations = 0;

void * fun_1(void * arg){
    int i;
    printf("Thread 1 started: Lock order A → B\n");
    
    for (i = 0; i < 10000; i++){
        if (i % 1000 == 0) {
            printf("Thread 1: iteration %d\n", i);
        }
        
        printf("Thread 1: Acquiring lock_a...\n");
        pthread_mutex_lock(&lock_a); // lock a then b
        printf("Thread 1: Got lock_a, trying lock_b...\n");
        
        pthread_mutex_lock(&lock_b);
        printf("Thread 1: Got both locks, updating variables\n");
        
        // CRITICAL SECTION
        a++;
        b++;
        thread1_iterations = i + 1;
        
        pthread_mutex_unlock(&lock_a);
        pthread_mutex_unlock(&lock_b);
        
        // Small delay to increase chance of deadlock
        if (i % 100 == 0) usleep(1);
    }
    
    printf("Thread 1 completed successfully\n");
    return NULL;
}

void * fun_2(void * arg){
    int i;
    printf("Thread 2 started: Lock order B → A\n");
    
    for (i = 0; i < 10000; i++){
        if (i % 1000 == 0) {
            printf("Thread 2: iteration %d\n", i);
        }
        
        printf("Thread 2: Acquiring lock_b...\n");
        pthread_mutex_lock(&lock_b); // lock b then a
        printf("Thread 2: Got lock_b, trying lock_a...\n");
        
        pthread_mutex_lock(&lock_a);
        printf("Thread 2: Got both locks, updating variables\n");
        
        // CRITICAL SECTION
        a++;
        b++;
        thread2_iterations = i + 1;
        
        pthread_mutex_unlock(&lock_b);
        pthread_mutex_unlock(&lock_a);
        
        // Small delay to increase chance of deadlock
        if (i % 100 == 0) usleep(1);
    }
    
    printf("Thread 2 completed successfully\n");
    return NULL;
}

int main(){
    pthread_t thread_1, thread_2;
    
    printf("=== DETAILED DEADLOCK ANALYSIS ===\n");
    printf("This program demonstrates the classic deadlock scenario\n");
    printf("Thread 1 locks: A → B\n");
    printf("Thread 2 locks: B → A\n");
    printf("Deadlock occurs when:\n");
    printf("  - Thread 1 holds A, waits for B\n");
    printf("  - Thread 2 holds B, waits for A\n");
    printf("Starting execution...\n\n");
    
    pthread_mutex_init(&lock_a, NULL);
    pthread_mutex_init(&lock_b, NULL);
    
    pthread_create(&thread_1, NULL, fun_1, NULL);
    pthread_create(&thread_2, NULL, fun_2, NULL);
    
    // Wait with timeout simulation
    printf("Main thread waiting for completion...\n");
    
    pthread_join(thread_1, NULL);
    pthread_join(thread_2, NULL);
    
    printf("\n=== FINAL RESULTS ===\n");
    printf("a = %d, b = %d\n", a, b);
    printf("Thread 1 completed %d iterations\n", thread1_iterations);
    printf("Thread 2 completed %d iterations\n", thread2_iterations);
    printf("Expected: a = b = 20000 if no deadlock\n");
    
    pthread_mutex_destroy(&lock_a);
    pthread_mutex_destroy(&lock_b);
    
    return 0;
}