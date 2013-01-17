CXX=g++
FLAGS=-Wall -Wextra -Wshadow -Wno-unused-parameter -g
CXXFLAGS=$(FLAGS) -std=c++11

bernard: bernard.o cache.o platform.o platform_unix.o
	$(CXX) $(CXXFLAGS) -o $@ bernard.o cache.o platform.o platform_unix.o

bernard.o: bernard.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ bernard.cpp

cache.o: cache.cpp cache.h
	$(CXX) $(CXXFLAGS) -c -o $@ cache.cpp

platform.o: platform.cpp platform.hpp
	$(CXX) $(CXXFLAGS) -c -o $@ platform.cpp

platform_unix.o: platform_unix.cpp platform.hpp
	$(CXX) $(CXXFLAGS) -c -o $@ platform_unix.cpp

clean:
	rm -f *.o bernard
