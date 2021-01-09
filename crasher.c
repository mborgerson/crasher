/*
 * App Crasher 1: A simple LD_PRELOAD library to read a desired crash address
 * from environment variable CRASHADDR and poke an invalid instruction into this
 * location. Assumes the given address is actual address when loaded.
 *
 * Run with: CRASHADDR=%x LD_PRELOAD=$PWD/crasher.so ./target
 *
 * FIXME: calling execve might run this again
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/mman.h>

#define LOG(fmt, ...) do { \
	fprintf(stderr, "%s: " fmt "\n", __func__, ## __VA_ARGS__); \
} while (0)

__attribute__((constructor)) void crasher(void) {
	const char *env_addr;
	uintptr_t addr;

	LOG("loaded");

	/* Read out target address from environment variable */
	if ((env_addr = getenv("CRASHADDR")) == NULL) {
		LOG("crash address not provided (set CRASHADDR)");
		return;
	}
	if (sscanf(env_addr, "%lx", &addr) != 1) {
		LOG("invalid crash address");
		return;
	}

	LOG("patching at %p", addr);

	/* Mark desired page as writable */
	int pagesize = getpagesize();
	uintptr_t aligned_addr = addr & ~(pagesize-1);
	if (mprotect((void*)aligned_addr, pagesize,
		         PROT_READ | PROT_WRITE | PROT_EXEC) == -1) {
		LOG("failed to mark target page writable");
		return;
	}

	/* Patch in illegal instruction */
	LOG("before: %p = %08x", addr, *(uint32_t *)addr);
	*(uint32_t *)addr = 0xffffffff;
	LOG("after:  %p = %08x", addr, *(uint32_t *)addr);
}
