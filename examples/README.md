# STDIN Example

Most fuzzers permit passing data from a file or through stdin. `main.c` can be
compiled to show both methods of providing input.

## The Example Program

The program just checks the first 255 bytes passed into the stdin/file for the
characters `a`, `b`, `c`, and `d`. Each character calls a mapped function:

- `a`: calls `a(void)`, simply `puts` and returns.
- `b`: calls `b(void)`, simply `puts` and returns.
- `c`: calls `c(void)`, simply `puts` and returns.
- `d`: calls `d(void)`, calls `abort` to simulate a crash.

Seems innocuous enough, right? Because of the way AFL handles uniqueness, AFL
will report up to four unique crashes to cover all four functions. However,
there's just one bug and triggering it is path-agnostic (okay, you do have to
*call* `d`, but that's it).

For our purposes, it would be helpful and simplify triaging if we just had one
test case to examine. This is a simple case, but you could see how it would
scale for much, much larger projects.

## Fuzzing

```shell
# `make` will compile `main.c` into `file and `stdin`.
$ make
# Start fuzzing stdin.
$ afl-fuzz -i ./input -o ./output stdin
# ...or fuzz argv[1].
$ afl-fuzz -i ./input -o ./output file @@
```

You should immediately wind up with four crashes in
[output](./output/default/crashes/). I left mine for you if you want to skip
this step.

## Dedeuplicating

Now we want to go from four test cases down to one. The syntax is really similar
to `afl-fuzz`. Notice however, that the output directory from `afl-fuzz` is now
the *input* to `crash-bucket`.

```shell
# Look in the input directory for the crashing test cases.
# Deduplicate this crashes and place the results in ./deduplicated-crashes.
$ crash-bucket --input ./output/default/crashes --output ./deduplicated-crashes ./stdin
# ...or deduplicate for `file`.
# Deduplicate this crashes and place the results in ./deduplicated-crashes.
$ crash-bucket --input ./output/default/crashes --output ./deduplicated-crashes ./file @@
```
