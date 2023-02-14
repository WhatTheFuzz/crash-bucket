# AFL LLDB Deduplicator

Iterates over a directory of crashing inputs and deduplicates the crashes. The
current algorithm just uses the source file, function name, and line number to
determine uniqueness. The intent to add additional algorithms in the future
(as the need arises).

## Usage

It requires three arguments:

- `-i` or `--input`: the input directory of crashing inputs.
- `-o` or `--output`: the output directory where the minimized corpus will be
  copied. If the directory does not exist, it will be created.
- The program and it's arguments. `@@` should be used to indicate that a program
  accepts input via a file read through the command-line arguments.

An example:

```shell
$ python3 ./deduplicator.py -i ./output/default/crashes -o ./min/ <path-to-target> @@

[*] '<path to program>'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
    ASAN:     Enabled
[*] Starting deduplication.
[+] Found new faulting line: 415
```

By default, the `pwn` package logging level is set to `log`. You can increase
the verbosity by turning on debug messages by setting the environment variable
`PWNLIB_DEBUG=1`. Debugging messages will show you what input the deduplicator
is currently checking.

## Limitations

- Requires symbols and debug symbols (`-glldb` for the best experience, though
  other levels should work fine).
- The above implies, in most cases, that you have source code.
