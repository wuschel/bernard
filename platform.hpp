#ifndef PLATFORM_H
#define PLATFORM_H

#include <stdio.h>
#include <string>

int getline(FILE* f, std::string& outstr);

int walk(char const* root,
         void(*file_handler)(const char* path, void* ctx),
         void(*dir_handler)(const char* path, void* ctx),
         void(*error_handler)(const char* path, void* ctx),
         void* ctx);

#endif
