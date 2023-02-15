# Crash Bucket

Iterates over a directory of crashing inputs and deduplicates the crashes. The
current algorithm just uses the source file, function name, and line number to
determine uniqueness. The intent to add additional algorithms in the future
(as the need arises). For more detail on the algorithm and it's pros/cons, see
[Crash Bucketing](#crash-bucketing).

## Usage

It requires three arguments:

- `-i` or `--input`: the input directory of crashing inputs.
- `-o` or `--output`: the output directory where the minimized corpus will be
  copied. If the directory does not exist, it will be created.
- The program and it's arguments. `@@` should be used to indicate that a program
  accepts input via a file read through the command-line arguments.

An example:

```shell
$ crash-bucket -i ./output/default/crashes -o ./min/ <path-to-target> @@

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

## Crash Bucketing

Crash bucketing is the processes of grouping crashing inputs that lead to the
same defective output. There are a few ways to do bucketing:

- Crash Sites - Location of instruction pointer; source code function/line
  number. Sensitive to a program's runtime behavior. If the program address
  space is randomized, your program counter might be different. If you don't
  have source code or debug symbols, you probably can't get line-level
  granularity.
- Coverage Profiles - Determines uniqueness based on edge coverage. Sensitive to
  changes in the path en-route to the root vulnerability. For example, consider
  two test cases. One results in the edge tuples AB→BD. The other results in the
  edge tuples AB→BC→CD. Both cause the same crash (potentially, stack trace as
  well). This will lead to two test cases that are "unique" but actually trigger
  the same bug. Sometimes you want this, sometime you don't.
- Stack Hashing - Similar to Coverage Profiles. Records the last *n* stack
  frames leading up to the crash. This provides a path to the crash and is
  similarly sensitive to differences in execution path.

The current algorithm in this project utilizes crash sites. This is pretty
naive, but fairly effective for simple bugs. It may not work well with
use-after-frees or other bug classes that can be triggered far beyond their
scope.

AFL uses Coverage Profiles to determine uniqueness.

### Limitations

- Requires symbols and debug symbols (`-glldb` for the best experience, though
  other levels should work fine).
- The above implies, in most cases, that you have source code.

## Comparison to Existing Work

- [Igor][igor]: Maintained; forked AFL source (not sync'ed with upstream);
  requires fitting.
- [SemanticCrashBucketing][semanticcrashbucketing]: Unmaintained (2019), unclear
  examples.

In comparison, this project is *fuzzer-independent*. You don't need a fuzzer at
all. You just need crashing input, a program, and lldb. It'll do the
minimization for you.

[igor]: https://github.com/HexHive/Igor
[semanticcrashbucketing]: https://github.com/squaresLab/SemanticCrashBucketing
