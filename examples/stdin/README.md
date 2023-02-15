# STDIN Example

Most fuzzers permit passing data from a file or through stdin. This example
shows how to deduplicate crashing input given through stdin.

## The Example Program

The program just checks the first 255 bytes passed into the stdin for the
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
# Compile the program with AFL's clang-fast or clang-lto
$ afl-clang-fast -glldb -Og -fno-omit-frame-pointer -fno-inline-functions main.c -std=c17 -o main
# Start fuzzing.
$ afl-fuzz -i ./input -o ./output main
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
# The program is called `main`, takes no arguments, and reads from `stdin`.
$ crash-bucket --input ./output/default/crashes --output ./deduplicated-crashes ./main
```
