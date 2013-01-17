#include "platform.hpp"

int getline(FILE* f, std::string& outstr) {
    outstr.erase();

    char buf[256];
    while(1) {
        if(fgets(buf, sizeof(buf), f) == NULL) return -1;
        outstr.append(buf);
        if(buf[sizeof(buf)-1] == '\n') break;
    }

    return 0;
}
