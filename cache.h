#ifndef CACHE_H
#define CACHE_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

typedef struct {
    uint64_t mtime;
    char sha256[65];
    uint16_t sequence;
} file_attrs_t;

typedef struct {
    file_attrs_t attrs;
    char* path;
} file_t;

typedef struct cache cache_t;
cache_t* cache_new(void);
int cache_load_map(cache_t* self, const char* path);
void cache_add(cache_t* self, const char* path, file_t* f);
void cache_mark(cache_t* self, const char* path);
int cache_retrieve(cache_t* self, const char* path, file_t* out);
void cache_iterate_unmarked(cache_t* self,
                            void (handler)(const char* path, file_attrs_t* f, void* ctx),
                            void* ctx);
int cache_save_map(cache_t* self, const char* path);
void cache_free(cache_t* self);

/*// Handle changed files
    Handle in filesystem and cache
// Handle new files
    Find in filesystem but not in cache
// Handle deleted files
    Find in cache but not in filesystem

For each file on filesystem:
    If in cache:
        if changed:
            back up
    else:
        back up
    mark in cache
Unmarked entries in cache are marked as deleted in mapfile
Back up mapfile*/

#ifdef __cplusplus
}
#endif

#endif
