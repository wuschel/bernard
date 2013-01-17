#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include "platform.hpp"

static void null_file_handler(const char* path, void* ctx) {}
static void null_dir_handler(const char* path, void* ctx) {}
static void null_error_handler(const char* path, void* ctx) {}

int walk(char const* root,
         void(*file_handler)(const char* path, void* ctx),
         void(*dir_handler)(const char* path, void* ctx),
         void(*error_handler)(const char* path, void* ctx),
         void* ctx) {
    // Set up default handlers
    if(file_handler == NULL) file_handler = null_file_handler;
    if(dir_handler == NULL) dir_handler = null_dir_handler;
    if(error_handler == NULL) error_handler = null_error_handler;

    DIR* root_dir = opendir(root);
    if(root_dir == NULL) {
        return -1;
    }

    // Reasonable default for most usage
    size_t full_path_allocated = 255;
    size_t full_path_len = 0;
    char* full_path_buf = (char*)malloc(full_path_allocated);

    struct dirent* ent = readdir(root_dir);
    while(ent != NULL) {
        const size_t ent_name_len = strlen(ent->d_name);

        // Fill in the full path, including path sep and nul character.
        const size_t required_len = strlen(root) + ent_name_len + 2;
        if(full_path_allocated < (required_len)) {
            char* new_buf = (char*)realloc(full_path_buf, required_len);
            if(new_buf == NULL) goto cleanup;
            full_path_buf = new_buf;
        }
        full_path_len = snprintf(full_path_buf, full_path_allocated,
                                 "%s/%s", root, ent->d_name);
        full_path_buf[full_path_len] = '\0';

        // Is it a file or a directory?
        struct stat info;
        if(stat(full_path_buf, &info) < 0) error_handler(full_path_buf, ctx);
        if(S_ISREG(info.st_mode)) {
            file_handler(full_path_buf, ctx);
        }
        else if(S_ISDIR(info.st_mode)) {
            if(strcmp(ent->d_name, ".") != 0 &&
               strcmp(ent->d_name, "..") != 0) {
                int status = walk(full_path_buf, file_handler,
                                  dir_handler, error_handler, ctx);
                if(status < 0) error_handler(full_path_buf, ctx);
            }
        }

        ent = readdir(root_dir);
    }

  cleanup:
    free(full_path_buf);
    closedir(root_dir);

    return 0;
}
