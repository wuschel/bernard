#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "cache.h"
#include "platform.hpp"

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
