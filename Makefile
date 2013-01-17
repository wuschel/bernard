CC=gcc
CXX=g++
FLAGS=-Wall -Wextra -Wshadow -Wno-unused-parameter -g
CFLAGS=$(FLAGS) -std=c99
CXXFLAGS=$(FLAGS) -std=c++11

bernard: bernard.o cache.o
	$(CXX) $(CXXFLAGS) -o $@ cache.o bernard.o

bernard.o: bernard.c
	$(CC) $(CFLAGS) -c -o $@ bernard.c

cache.o: cache.cpp cache.h
	$(CXX) $(CXXFLAGS) -c -o $@ cache.cpp

clean:
	rm -f *.o bernard
