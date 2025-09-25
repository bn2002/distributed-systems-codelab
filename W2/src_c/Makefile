CC = gcc
CFLAGS = -pthread -Wall
TARGET = simple
SOURCE = simple.c

$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) $(SOURCE) -o $(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: clean