CC=buildroot-2020.02.9/output/host/bin/arm-buildroot-linux-uclibcgnueabi-cc

.PHONY: all
all: target crasher.so

target: target.c
	$(CC) -o $@ -O0 -g $^

crasher.so: crasher.c
	$(CC) -o $@ -O0 -g -shared -fPIC $^
