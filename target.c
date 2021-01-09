#include <stdio.h>
#include <string.h>

#define LOG(fmt, ...) do { \
	fprintf(stderr, "%s: " fmt "\n", __func__, ## __VA_ARGS__); \
} while (0)

void patchcrash(void)
{
	/* Control should be patched here... */
	LOG("Patch Failed!");
}

void forcecrash(void)
{
	int *bad = (int *)0;
	*bad = 0xbadc0de;
	LOG("Should not reach here!");
}

int main(int argc, char const *argv[])
{
	LOG("Start");

	if (argc > 1) {
		if (!strcmp(argv[1], "force")) {
			forcecrash();
		}
	}
	patchcrash();

	LOG("Terminating");
	return 0;
}
