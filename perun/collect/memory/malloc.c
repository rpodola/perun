/*
 * File:        malloc.c
 * Project:     Library for Profiling and Visualization of Memory Consumption
 *              of C/C++ Programs, Bachelor's thesis
 * Date:        29.2.2017
 * Author:      Podola Radim, xpodol06@stud.fit.vutbr.cz
 * Description: File contains implementations of injected allocation functions.
 */
#define _GNU_SOURCE
#include <dlfcn.h> //dlsym()
#include <stdio.h>
#include <time.h> //clock()

#include "backtrace.h"

#define LOG_FILE_NAME "MemoryLog"

static FILE *logFile = NULL;
static int profiling = 0;

/*
GCC destructor attribute provides finalizing function which close log file properly
after main program's execution finished
*/
__attribute__((destructor)) void finalize (void){

   profiling = 1;

   if(logFile != NULL){
      fprintf(logFile, "EXIT %fs\n", clock() / (double)CLOCKS_PER_SEC);
      fclose(logFile);
   }
}

void *malloc(size_t size){

   static void *(*real_malloc)(size_t) = NULL;
   if(!real_malloc){
      real_malloc = dlsym(RTLD_NEXT, "malloc");

      profiling = 1;
      if(!logFile)
         logFile = fopen(LOG_FILE_NAME, "w");
      profiling = 0;
   }

   void *ptr = real_malloc(size);

   if(!profiling && ptr != NULL){
      profiling = 1;

      fprintf(logFile, "time %fs\n", clock() / (double)CLOCKS_PER_SEC);
      fprintf(logFile, "malloc %liB %li\n", size, (long int)ptr);
      backtrace(logFile);

      profiling = 0;
   }

   return ptr;
}

void free(void *ptr){

   static void(*real_free)(void*) = NULL;
   if(!real_free){
      real_free = dlsym(RTLD_NEXT, "free");

      profiling = 1;
      if(!logFile)
         logFile = fopen(LOG_FILE_NAME, "w");
      profiling = 0;
   }

   real_free(ptr);
  
   if(!profiling){
      profiling = 1;

      fprintf(logFile, "time %fs\n", clock() / (double)CLOCKS_PER_SEC);
      fprintf(logFile, "free 0B %li\n", (long int)ptr);
      backtrace(logFile);

      profiling = 0;
   }
}

void *realloc(void *ptr, size_t size){
   
   static void *(*real_realloc)(void*, size_t) = NULL;
   if(!real_realloc){
      real_realloc = dlsym(RTLD_NEXT, "realloc");

      profiling = 1;
      if(!logFile)
         logFile = fopen(LOG_FILE_NAME, "w");
      profiling = 0;
   }

   void *nptr = real_realloc(ptr, size);

   if(!profiling && ptr != NULL){
      profiling = 1;
    
      fprintf(logFile, "time %fs\n", clock() / (double)CLOCKS_PER_SEC);  
      fprintf(logFile, "realloc %liB %li\n", size, (long int)nptr);
      backtrace(logFile);

      profiling = 0;
   }

   return nptr;
}

void *calloc(size_t nmemb, size_t size){

   static void *(*real_calloc)(size_t, size_t)= NULL;
   if(!real_calloc){
      real_calloc = dlsym(RTLD_NEXT, "calloc");

      profiling = 1;
      if(!logFile)
         logFile = fopen(LOG_FILE_NAME, "w");
      profiling = 0;
   }

   void *ptr = real_calloc(nmemb, size);

   if(!profiling && ptr != NULL){
      profiling = 1;

      fprintf(logFile, "time %fs\n", clock() / (double)CLOCKS_PER_SEC);
      fprintf(logFile, "calloc %liB %li\n", size*nmemb, (long int)ptr);
      backtrace(logFile);

      profiling = 0;
   }

   return ptr;
}

void *memalign(size_t alignment, size_t size){

   static void *(*real_memalign)(size_t, size_t) = NULL;
   if(!real_memalign){
      real_memalign = dlsym(RTLD_NEXT, "memalign");

      profiling = 1;
      if(!logFile)
         logFile = fopen(LOG_FILE_NAME, "w");
      profiling = 0;
   }

   void *ptr = real_memalign(alignment, size);

   if(!profiling && ptr != NULL){
      profiling = 1;

      fprintf(logFile, "time %fs\n", clock() / (double)CLOCKS_PER_SEC);
      fprintf(logFile, "memalign %liB %li\n", size, (long int)ptr);
      backtrace(logFile);

      profiling = 0;
   }

   return ptr;
}

int posix_memalign(void** memptr, size_t alignment, size_t size){

   static int (*real_posix_memalign)(void**, size_t, size_t) = NULL;
   if(!real_posix_memalign){
      real_posix_memalign = dlsym(RTLD_NEXT, "posix_memalign");

      profiling = 1;
      if(!logFile)
         logFile = fopen(LOG_FILE_NAME, "w");
      profiling = 0;
   }

   int ret = real_posix_memalign(memptr, alignment, size);

   if(!profiling && ret == 0){
      profiling = 1;

      fprintf(logFile, "time %fs\n", clock() / (double)CLOCKS_PER_SEC);
      fprintf(logFile, "posix_memalign %liB %li\n", size, (long int)*memptr);
      backtrace(logFile);

      profiling = 0;
   }

   return ret;
}

void *valloc(size_t size){

   static void *(*real_valloc)(size_t) = NULL;
   if(!real_valloc){
      real_valloc = dlsym(RTLD_NEXT, "valloc");

      profiling = 1;
      if(!logFile)
         logFile = fopen(LOG_FILE_NAME, "w");
      profiling = 0;
   }

   void *ptr = real_valloc(size);

   if(!profiling && ptr != NULL){
      profiling = 1;

      fprintf(logFile, "time %fs\n", clock() / (double)CLOCKS_PER_SEC);
      fprintf(logFile, "valloc %liB %li\n", size, (long int)ptr);
      backtrace(logFile);

      profiling = 0;
   }

   return ptr;
}

void *aligned_alloc(size_t alignment, size_t size){

   static void *(*real_aligned_alloc)(size_t, size_t) = NULL;
   if(!real_aligned_alloc){
      real_aligned_alloc = dlsym(RTLD_NEXT, "aligned_alloc");

      profiling = 1;
      if(!logFile)
         logFile = fopen(LOG_FILE_NAME, "w");
      profiling = 0;
   }

   void *ptr = real_aligned_alloc(alignment, size);

   if(!profiling && ptr != NULL){
      profiling = 1;

      fprintf(logFile, "time %fs\n", clock() / (double)CLOCKS_PER_SEC);
      fprintf(logFile, "aligned_alloc %liB %li\n", size, (long int)ptr);
      backtrace(logFile);

      profiling = 0;
   }

   return ptr;
}