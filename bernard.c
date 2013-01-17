#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include "cache.h"

#define PATH_SEP '/'

void null_file_handler(const char* path, void* ctx) {}
void null_dir_handler(const char* path, void* ctx) {}
void null_error_handler(const char* path, void* ctx) {}

int walk_unix(char const* root,
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
    char* full_path_buf = malloc(full_path_allocated);

    struct dirent* ent = readdir(root_dir);
    while(ent != NULL) {
        const size_t ent_name_len = strlen(ent->d_name);

        // Fill in the full path, including path sep and nul character.
        const size_t required_len = strlen(root) + ent_name_len + 2;
        if(full_path_allocated < (required_len)) {
            char* new_buf = realloc(full_path_buf, required_len);
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
                int status = walk_unix(full_path_buf, file_handler,
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
#define walk walk_unix

typedef struct {
    cache_t* cache;
} bernard_t;

void handle_file(const char* path, void* ctx) {
    bernard_t* bernard = (bernard_t*)ctx;
    file_t cache_entry;
    cache_retrieve(bernard->cache, path, &cache_entry);

    printf("%s\n", path);
}

int main(int argc, char** argv) {
    if(argc == 1) {
        return 1;
    }

    bernard_t bernard;
    bernard.cache = cache_new(); // XX MAY RETURN ERROR
    cache_load_map(bernard.cache, argv[1]); // XXX MAY RETURN ERROR

    char* root = argv[argc-1];
    walk(root, &handle_file, NULL, NULL, &bernard); // XXX MAY RETURN ERROR

    cache_save_map(bernard.cache, argv[1]);

    cache_free(bernard.cache);

    return 0;
}
