#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

int a = 0, b = 0;
pthread_mutex_t lock_a, lock_b;

void * fun_1_fixed(void * arg){
    int i;
    printf("Thread 1 (FIXED): Always lock A → B\n");
    
    for (i = 0; i < 10000; i++){
        // CONSISTENT ORDER: Always A then B
        pthread_mutex_lock(&lock_a);
        pthread_mutex_lock(&lock_b);
        
        // CRITICAL SECTION
        a++;
        b++;
        
        pthread_mutex_unlock(&lock_a);
        pthread_mutex_unlock(&lock_b);
        
        if (i % 2000 == 0) {
            printf("Thread 1: iteration %d, a=%d, b=%d\n", i, a, b);
        }
    }
    printf("Thread 1 completed successfully\n");
    return NULL;
}

void * fun_2_fixed(void * arg){
    int i;
    printf("Thread 2 (FIXED): Always lock A → B (same order)\n");
    
    for (i = 0; i < 10000; i++){
        // CONSISTENT ORDER: Always A then B (same as Thread 1)
        pthread_mutex_lock(&lock_a);
        pthread_mutex_lock(&lock_b);
        
        // CRITICAL SECTION
        a++;
        b++;
        
        pthread_mutex_unlock(&lock_a);
        pthread_mutex_unlock(&lock_b);
        
        if (i % 2000 == 0) {
            printf("Thread 2: iteration %d, a=%d, b=%d\n", i, a, b);
        }
    }
    printf("Thread 2 completed successfully\n");
    return NULL;
}

int main(){
    pthread_t thread_1, thread_2;
    
    printf("=== DEADLOCK SOLUTION: CONSISTENT LOCK ORDERING ===\n");
    printf("Both threads now use same lock order: A → B\n");
    printf("This prevents deadlock completely\n\n");
    
    pthread_mutex_init(&lock_a, NULL);
    pthread_mutex_init(&lock_b, NULL);
    
    pthread_create(&thread_1, NULL, fun_1_fixed, NULL);
    pthread_create(&thread_2, NULL, fun_2_fixed, NULL);
    
    pthread_join(thread_1, NULL);
    pthread_join(thread_2, NULL);
    
    printf("\n=== FINAL RESULTS ===\n");
    printf("a = %d, b = %d\n", a, b);
    printf("Expected: a = b = 20000\n");
    
    if (a == 20000 && b == 20000) {
        printf("✅ SUCCESS: No deadlock, correct results!\n");
    } else {
        printf("❌ Something went wrong\n");
    }
    
    pthread_mutex_destroy(&lock_a);
    pthread_mutex_destroy(&lock_b);
    
    return 0;
}