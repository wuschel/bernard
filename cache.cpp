#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include <set>
#include <string>
#include <map>
#include "cache.h"
#include "platform.hpp"

#define MAPFILE_VERSION 1

struct cache {
    std::map<std::string, file_attrs_t> cache;
    std::set<std::string> unmarked;
};

cache_t* cache_new(void) {
    return new cache();
}

int cache_load_map(cache_t* self, const char* path) {
    FILE* f = fopen(path, "rb");
    if(f == NULL) return 1;

    std::string line;
    // First line should contain general format information
    getline(f, line);

    fclose(f);
    return 0;
}

void cache_add(cache_t* self, const char* path, file_t* f) {
    std::string cpppath(path);
    memcpy(&self->cache[cpppath], &f->attrs, sizeof(file_attrs_t));
    self->unmarked.insert(cpppath);
}

void cache_mark(cache_t* self, const char* path) {
    self->unmarked.erase(std::string(path));
}

int cache_retrieve(cache_t* self, const char* path, file_t* out) {
    auto it = self->cache.find(path);
    if(it == self->cache.end()) {
        return 0;
    }

    memcpy(out, &*it, sizeof(file_t));
    return 1;
}

void cache_iterate_unmarked(cache_t* self,
                            void (handler)(const char* path, file_attrs_t* f, void* ctx),
                            void* ctx) {
    auto it = self->unmarked.begin();
    for(; it != self->unmarked.end(); ++it) {
        handler(it->c_str(), &self->cache[*it], ctx);
    }
}

int cache_save_map(cache_t* self, const char* path) {
    // Don't overwrite the mapfile until we're done.
    const size_t tmppath_len = strlen(path) + 4;
    char* tmppath = (char*)malloc(tmppath_len+1);
    if(tmppath == NULL) {
        free(tmppath);
        return 1;
    }
    snprintf(tmppath, tmppath_len+1, "%s.tmp", path);

    FILE* f = fopen(tmppath, "wb");
    if(f == NULL) {
        free(tmppath);
        return 1;
    }
    fclose(f);

    if(rename(tmppath, path) < 0) {
        free(tmppath);
        return 2;
    }
    free(tmppath);

    return 0;
}

void cache_free(cache_t* self) {
    delete self;
}
