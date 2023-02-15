#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
import magic
from pathlib import Path
from pwn import ELF, log, context
from elftools.common.exceptions import ELFError
import lldb
import shutil
import os

context.terminal = ['gnome-terminal', '-e']
context.delete_corefiles = True

def deduplicate(input: Path, output: Path, executable: ELF, args: list[str]):
    '''Deduplicate the crashing inputs.'''

    faulting_lines: set[str] = set()

    # If @@ is not in the args, we pass in files via stdin.
    stdin = '@@' not in args

    if stdin:
        log.info('Configured to pass in files via stdin. If this is incorrect, '
                 'please use @@ in the arguments to the executable or file an '
                 'issue on GitHub.')
    else:
        log.info('Configured to pass in files via arguments. If this is '
                 'incorrect, please remove the @@ in the arguments to the '
                 'or file an issue on GitHub.')


    # For each file in the input directory.
    for file in input.iterdir():

        log.debug(f'Checking file: {file}')

        # If @@ is in the args, replace it with the input file.
        if '@@' in args:
            args[args.index('@@')] = str(file)
            stdin = False

        # Create the debugger.
        debugger: lldb.SBDebugger = lldb.SBDebugger.Create()
        debugger.SetAsync(True)

        # Create the target.
        target: lldb.SBTarget = debugger.CreateTargetWithFileAndArch(filename=executable.path, archname=lldb.LLDB_ARCH_DEFAULT)

        # Check that the target is valid.
        if not target.IsValid():
            log.error('Target is invalid')

        # Create LaunchOptions to pass to the target.
        launch_info = target.GetLaunchInfo()
        launch_info.SetArguments(args, append=True)
        launch_info.SetExecutableFile(exe_file=lldb.SBFileSpec(executable.path), add_as_first_arg=True)


        # Create an empty SBError to pass to the target.
        error: lldb.SBError = lldb.SBError()

        # Launch the process.
        process: lldb.SBProcess = target.Launch(launch_info, error)
        log.debug(f'Launched process: {process.GetProcessID()}')

        # Check that the process launched successfully.
        if error.Fail():
            log.failure(f'Failed to launch process: {error.GetCString()}')
            # Suggest a common fix.
            if 'unable to locate lldb-server' in error.GetCString():
                log.info('This is an Ubuntu package error. Create a symlink for lldb-server-X.0.0 that points to lldb-server-X. Replace X with the version numbers.')
            exit(1)

        # If the process reads from stdin, open the file and pass it in.
        if stdin:
            with open(file, 'rb') as f:
                process.PutSTDIN(f.read())

        # Get the crashing frame.
        frame: lldb.SBFrame = process.GetThreadAtIndex(0).GetFrameAtIndex(0)
        line: lldb.SBLineEntry = frame.GetLineEntry()

        # Check if we've seen this line before.
        if str(line) not in faulting_lines:
            faulting_lines.add(str(line))
            log.success(f'Found new faulting line: {line.GetLine()} with input: {file}')

            # Copy the file to the output directory.
            shutil.copy(src=file, dst=output)


def main() -> None:
    '''Parse arguments and ensure that directories and the executable exist.'''
    parser: ArgumentParser = ArgumentParser(
                    prog = 'AFL Deduplicator',
                    description = 'Runs all of the crashing input with the \
                                   program and removes duplicate crashes.')
    # Input directory of crashing inputs.
    parser.add_argument('--input', '-i',
                        required=True,
                        help="Input directory containing crashing inputs.",
                        type=Path)
    # Output directory of deduplicated crashing inputs.
    parser.add_argument('--output', '-o',
                        required=True,
                        help="Output directory to store deduplicated crashing. \
                              Will not overwrite existing directory.",
                        type=Path)
    # Path to the executable and how to call it.
    parser.add_argument('executable', type=str, nargs='+')
    # Parse the user arguments.
    args: Namespace = parser.parse_args()

    # Check that the executable exists.
    try:
        target: ELF = ELF(args.executable[0])
    except FileNotFoundError:
        log.error('The target executable does not exist.')
    except IsADirectoryError:
        log.error('The target executable is a directory.')
    except ELFError:
        log.error(f'Executable is of type: '
                  f'{magic.from_file(args.executable[0])}; not an ELF.')


    # Check that the input directory exists.
    if not args.input.exists():
        log.error('The input directory does not exist.')

    # Check that the output directory exists.
    if not args.output.exists():
        os.mkdir(args.output)

    # Get the list of arguments to the executable.
    arguments: list[str] = args.executable[1:]

    # Start deduplicating.
    log.info('Starting deduplication.')
    deduplicate(args.input, args.output, target, arguments)


if __name__ == '__main__':
    main()
