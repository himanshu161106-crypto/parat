/* gen_random3: seeded uniform random 3-SAT generator (the one used for the big random results).
 *   gcc -O2 -o gen_random3 gen_random3.c
 *   ./gen_random3 N RATIO SEED > file.cnf
 * Each clause: 3 distinct variables chosen uniformly, each negated with probability 1/2.
 * M = round(N * RATIO). The same N, RATIO, SEED always give the same file (xoshiro256** seeded by splitmix64). */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

static uint64_t rs[4];
static inline uint64_t rotl(uint64_t x, int k) { return (x << k) | (x >> (64 - k)); }
static inline uint64_t rnd(void) {
    uint64_t r = rotl(rs[1] * 5, 7) * 9, t = rs[1] << 17;
    rs[2] ^= rs[0]; rs[3] ^= rs[1]; rs[1] ^= rs[2]; rs[0] ^= rs[3]; rs[2] ^= t; rs[3] = rotl(rs[3], 45); return r;
}
static void seed_rng(uint64_t s) {
    for (int i = 0; i < 4; i++) { s += 0x9e3779b97f4a7c15ULL; uint64_t z = s;
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; rs[i] = z ^ (z >> 31); }
}
static inline uint32_t rbelow(uint32_t n) { return (uint32_t)(((rnd() >> 32) * (uint64_t)n) >> 32); }

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: gen_random3 N RATIO SEED > file.cnf\n"); return 1; }
    int N = atoi(argv[1]); double ratio = atof(argv[2]); uint64_t seed = strtoull(argv[3], 0, 10);
    int M = (int)llround(N * ratio); seed_rng(seed);
    static char buf[1 << 22]; setvbuf(stdout, buf, _IOFBF, sizeof buf);
    printf("p cnf %d %d\n", N, M);
    for (int c = 0; c < M; c++) {
        int a, b, d; a = 1 + rbelow(N); do b = 1 + rbelow(N); while (b == a); do d = 1 + rbelow(N); while (d == a || d == b);
        int la = (rnd() >> 63) ? a : -a, lb = (rnd() >> 63) ? b : -b, ld = (rnd() >> 63) ? d : -d;
        printf("%d %d %d 0\n", la, lb, ld);
    }
    return 0;
}
