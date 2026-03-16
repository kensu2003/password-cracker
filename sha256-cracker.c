// Made by : Leo Wei

#include <stdio.h>
#include <string.h>
#include <openssl/sha.h>

static char alphabet[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";

/* Low-level SHA256 (no EVP, no heap): one context, Init/Update/Final per hash. */
static void compute_sha256(SHA256_CTX *ctx, const char *input, size_t len, unsigned char *out) {
  SHA256_Init(ctx);
  SHA256_Update(ctx, (const unsigned char *)input, len);
  SHA256_Final(out, ctx);
}

static void brute_force(SHA256_CTX *ctx, const unsigned char *hash, char *buffer, int position, int total_len) {
  if (position == total_len) {
    buffer[position] = '\0';
    unsigned char computed_hash[32];
    compute_sha256(ctx, buffer, (size_t)position, computed_hash);
    if (memcmp(computed_hash, hash, 32) == 0) {
      printf("%s\n", buffer);
    }
    return;
  }
  for (int i = 0; i < 62; i++) {
    buffer[position] = alphabet[i];
    brute_force(ctx, hash, buffer, position + 1, total_len);
  }
}

void hex_to_bytes(const char *hex, unsigned char *bytes) {
  for (int i = 0; i < 32; i++) {
    sscanf(hex + 2 * i, "%02hhx", &bytes[i]);
  }
}

int main() {
  SHA256_CTX ctx;

  /* 4-char (c0de) */
  const char * hash4 = "3803b47609a2a464054659b14a0cdfba92830fb46ee70c03a336d5554b9acad4";
  /* 6-char */
  const char * hash6 = "9994a0007e4271061b671424371f3f04dce63520b25ef9036fa45f3439e2f062";
  unsigned char target_bin[32];

  char buf4[5];
  char buf6[7];

  hex_to_bytes(hash4, target_bin);
  brute_force(&ctx, target_bin, buf4, 0, 4);

  /* Uncomment to also crack 6-char (slow): */
  /* hex_to_bytes(hash6, target_bin); brute_force(&ctx, target_bin, buf6, 0, 6); */

  return 0;
}
