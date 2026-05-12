#!/usr/bin/env python3
# Copyright (c) 2023-2026 Orange. All rights reserved.
# This software is distributed under the BSD 3-Clause-clear License, the text of which is available
# at https://spdx.org/licenses/BSD-3-Clause-Clear.html or see the "LICENSE" file for more details.

"""
KNIRecodeFile: Recode an input file to an output file using a Khiops dictionary.

This script demonstrates the use of the Khiops Native Interface (KNI) from Python
to deploy a Khiops model for real-time scoring without temporary files.
"""

import sys
import argparse
from KNI import KNI, KNIError


def recode_file(
    dictionary_file_name,
    dictionary_name,
    input_file_name,
    output_file_name,
    error_file_name="",
):
    """
    Recode an input file to an output file using a Khiops dictionary.

    Args:
        dictionary_file_name: Path to the dictionary file
        dictionary_name: Name of the dictionary to use
        input_file_name: Path to input file (must have header line)
        output_file_name: Path to output file
        error_file_name: Optional path to error log file (empty for no logging)

    Raises:
        KNIError: If any KNI operation fails
        FileNotFoundError: If input file is not found
        ValueError: If input file is empty or invalid
    """
    # Initialize KNI
    kni = KNI()

    # Set error log file
    if error_file_name:
        kni.set_log_file_name(error_file_name)

    print(f"\nRecode records of {input_file_name} to {output_file_name}")

    # Open input and output files
    with open(input_file_name, "r", encoding="utf-8") as input_file, open(
        output_file_name, "w", encoding="utf-8"
    ) as output_file:

        # Read header line
        header_line = input_file.readline().rstrip()
        if not header_line:
            raise ValueError("Empty input file")

        # Open KNI stream
        stream_handle = kni.open_stream(
            dictionary_file_name, dictionary_name, header_line, "\t"
        )

        try:
            # Process all records
            record_number = 0
            for line_number, line in enumerate(input_file, start=2):
                # Remove trailing whitespace
                input_record = line.rstrip()

                # Skip empty lines
                if not input_record:
                    continue

                # Recode the record
                output_record = kni.recode_stream_record(stream_handle, input_record)

                # Write output record
                output_file.write(f"{output_record}\n")
                record_number += 1
        finally:
            # Close stream
            kni.close_stream(stream_handle)

        print(f"{record_number} records recoded")


def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(
        description="Recode an input file to an output file using a Khiops dictionary.",
        epilog="The input file must have a header line, describing the structure of all its instances. "
        "The input and output files have a tabular format. "
        "The error file may be useful for debugging purposes.",
    )

    parser.add_argument(
        "dictionary_file",
        help="Path to the dictionary file",
    )
    parser.add_argument(
        "dictionary_name",
        help="Name of the dictionary to use",
    )
    parser.add_argument(
        "input_file",
        help="Path to input file (must have header line)",
    )
    parser.add_argument(
        "output_file",
        help="Path to output file",
    )
    parser.add_argument(
        "error_file",
        nargs="?",
        default="",
        help="Optional path to error log file (empty for no logging)",
    )

    args = parser.parse_args()

    # Execute recoding
    try:
        recode_file(
            args.dictionary_file,
            args.dictionary_name,
            args.input_file,
            args.output_file,
            args.error_file,
        )
        return 0
    except KNIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: File not found: {e.filename}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
