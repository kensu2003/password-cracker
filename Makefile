OPENSSL_PREFIX := $(shell brew --prefix openssl@3 2>/dev/null || brew --prefix openssl 2>/dev/null || echo "/usr")

sha256-cracker: sha256-cracker.c
	gcc sha256-cracker.c -o sha256-cracker -I$(OPENSSL_PREFIX)/include -L$(OPENSSL_PREFIX)/lib -lssl -lcrypto -O3
