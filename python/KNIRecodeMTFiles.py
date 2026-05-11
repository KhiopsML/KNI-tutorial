#!/usr/bin/env python3
# Copyright (c) 2023-2026 Orange. All rights reserved.
# This software is distributed under the BSD 3-Clause-clear License, the text of which is available
# at https://spdx.org/licenses/BSD-3-Clause-Clear.html or see the "LICENSE" file for more details.

"""
KNIRecodeMTFiles: Recode multi-table input files using a Khiops dictionary.

This script demonstrates multi-table recoding with the Khiops Native Interface (KNI)
from Python. It supports secondary tables and external tables.
"""

import sys
import argparse
from KNI import KNI


class KNIError(Exception):
    """Exception raised for KNI errors."""

    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code


def recode_mt_files(
    dictionary_file,
    dictionary_name,
    input_specs,
    secondary_specs,
    external_specs,
    output_file,
    field_separator="\t",
    error_file="",
    max_memory=None,
):
    """
    Recode multi-table input files to a single output file.

    Args:
        dictionary_file: Path to the dictionary file
        dictionary_name: Name of the dictionary to use
        input_specs: Dict with 'file': input file path, 'keys': list of key column indices (1-based)
        secondary_specs: List of dicts with 'path': data path, 'file': file path, 'keys': key indices
        external_specs: List of dicts with 'root': data root, 'path': data path, 'file': file path
        output_file: Path to output file
        field_separator: Character to separate fields
        error_file: Optional path to error log file
        max_memory: Optional maximum memory in MB

    Raises:
        KNIError: If any KNI operation fails
        FileNotFoundError: If input file is not found
    """
    # Initialize KNI
    kni = KNI()

    # Set error log file
    if error_file:
        ret_code = kni.set_log_file_name(error_file)
        if ret_code != KNI.KNI_OK:
            print(
                f"Warning: Failed to set log file: {kni.get_error_message(ret_code)}",
                file=sys.stderr,
            )

    # Set max memory if specified
    if max_memory:
        actual_memory = kni.set_stream_max_memory(max_memory)
        print(f"Stream max memory set to {actual_memory} MB")

    print(f"\nRecode multi-table data to {output_file}")

    # Read headers from all input files
    input_file_path = input_specs["file"]
    with open(input_file_path, "r", encoding="utf-8") as f:
        main_header = f.readline().rstrip()

    # Open stream with main table header
    stream_handle = kni.open_stream(
        dictionary_file, dictionary_name, main_header, field_separator
    )

    if stream_handle < 0:
        raise KNIError(
            f"Open stream failed: {kni.get_error_message(stream_handle)}",
            stream_handle,
        )

    try:
        # Set secondary table headers
        secondary_files = {}
        for spec in secondary_specs:
            data_path = spec["path"]
            sec_file = spec["file"]

            with open(sec_file, "r", encoding="utf-8") as f:
                sec_header = f.readline().rstrip()

            ret_code = kni.set_secondary_header_line(
                stream_handle, data_path, sec_header
            )
            if ret_code != KNI.KNI_OK:
                raise KNIError(
                    f"Set secondary header failed for {data_path}: "
                    f"{kni.get_error_message(ret_code)}",
                    ret_code,
                )

            # Store opened file for reading records
            secondary_files[data_path] = {
                "file": open(sec_file, "r", encoding="utf-8"),
                "keys": spec["keys"],
                "records": {},
            }
            # Skip header
            secondary_files[data_path]["file"].readline()

        # Set external tables
        for spec in external_specs:
            ret_code = kni.set_external_table(
                stream_handle, spec["root"], spec.get("path", ""), spec["file"]
            )
            if ret_code != KNI.KNI_OK:
                raise KNIError(
                    f"Set external table failed: {kni.get_error_message(ret_code)}",
                    ret_code,
                )

        # Finish opening stream (required for multi-table)
        ret_code = kni.finish_opening_stream(stream_handle)
        if ret_code != KNI.KNI_OK:
            raise KNIError(
                f"Finish opening stream failed: {kni.get_error_message(ret_code)}",
                ret_code,
            )

        # Load all secondary records into memory indexed by key
        for data_path, sec_info in secondary_files.items():
            print(f"Loading secondary table: {data_path}")
            for line in sec_info["file"]:
                record = line.rstrip()
                if not record:
                    continue

                # Extract key from record
                fields = record.split(field_separator)
                key_values = [fields[idx - 1] for idx in sec_info["keys"]]
                key = tuple(key_values)

                # Store record by key (support multiple records per key)
                if key not in sec_info["records"]:
                    sec_info["records"][key] = []
                sec_info["records"][key].append(record)

            sec_info["file"].close()

        # Process main table records
        record_number = 0
        with open(input_file_path, "r", encoding="utf-8") as main_file, open(
            output_file, "w", encoding="utf-8"
        ) as out_file:

            for line_number, line in enumerate(main_file, start=1):
                # Skip header
                if line_number == 1:
                    continue

                # Get main record
                main_record = line.rstrip()
                if not main_record:
                    continue

                # Extract key from main record
                main_fields = main_record.split(field_separator)
                main_key = tuple([main_fields[idx - 1] for idx in input_specs["keys"]])

                # Set all secondary records matching the main record key
                for data_path, sec_info in secondary_files.items():
                    matching_records = sec_info["records"].get(main_key, [])
                    for sec_record in matching_records:
                        ret_code = kni.set_secondary_input_record(
                            stream_handle, data_path, sec_record
                        )
                        if ret_code != KNI.KNI_OK:
                            raise KNIError(
                                f"Set secondary record failed at line {line_number}: "
                                f"{kni.get_error_message(ret_code)}",
                                ret_code,
                            )

                # Recode the main record
                ret_code, output_record = kni.recode_stream_record(
                    stream_handle, main_record
                )
                if ret_code == KNI.KNI_OK:
                    out_file.write(f"{output_record}\n")
                    record_number += 1
                else:
                    raise KNIError(
                        f"Recode failed at line {line_number}: "
                        f"{kni.get_error_message(ret_code)}",
                        ret_code,
                    )

        print(f"{record_number} records recoded")
    finally:
        # Close any open secondary files
        for sec_info in secondary_files.values():
            if not sec_info["file"].closed:
                sec_info["file"].close()

        # Close stream
        ret_code = kni.close_stream(stream_handle)
        if ret_code != KNI.KNI_OK:
            raise KNIError(
                f"Close stream failed: {kni.get_error_message(ret_code)}",
                ret_code,
            )


def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(
        description="Recode multi-table input files using a Khiops dictionary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  KNIRecodeMTFiles -d data/ModelingSpliceJunction.kdic SNB_SpliceJunction \\
      -i data/SpliceJunction.txt 1 \\
      -s DNA data/SpliceJunctionDNA.txt 1 \\
      -o R_SpliceJunction.txt
        """,
    )

    parser.add_argument(
        "-d",
        "--dictionary",
        nargs=2,
        required=True,
        metavar=("FILE", "NAME"),
        help="Dictionary file and dictionary name",
    )
    parser.add_argument(
        "-f",
        "--field-separator",
        default="\t",
        help="Field separator character (default: tab)",
    )
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        required=True,
        metavar="ARG",
        help="Input file name followed by key column indices (1-based): FILE KEY...",
    )
    parser.add_argument(
        "-s",
        "--secondary",
        action="append",
        nargs="+",
        metavar="ARG",
        help="Secondary data path, file name, and key indices: PATH FILE KEY...",
    )
    parser.add_argument(
        "-x",
        "--external",
        action="append",
        nargs=3,
        metavar=("ROOT", "PATH", "FILE"),
        help="External data root, path, and file name: ROOT PATH FILE",
    )
    parser.add_argument("-o", "--output", required=True, help="Output file name")
    parser.add_argument(
        "-e", "--error-file", default="", help="Error log file name (optional)"
    )
    parser.add_argument("-m", "--max-memory", type=int, help="Maximum memory in MB")

    args = parser.parse_args()

    # Parse input specification
    input_file = args.input[0]
    key_indices = [int(k) for k in args.input[1:]]
    input_specs = {"file": input_file, "keys": key_indices}

    # Parse secondary specifications
    secondary_specs = []
    if args.secondary:
        for sec in args.secondary:
            data_path = sec[0]
            sec_file = sec[1]
            sec_keys = [int(k) for k in sec[2:]]
            secondary_specs.append(
                {"path": data_path, "file": sec_file, "keys": sec_keys}
            )

    # Parse external specifications
    external_specs = []
    if args.external:
        for ext in args.external:
            external_specs.append({"root": ext[0], "path": ext[1], "file": ext[2]})

    # Execute recoding
    try:
        recode_mt_files(
            args.dictionary[0],
            args.dictionary[1],
            input_specs,
            secondary_specs,
            external_specs,
            args.output,
            args.field_separator,
            args.error_file,
            args.max_memory,
        )
        return 0
    except KNIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: File not found: {e.filename}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
