# Table of Contents

* [kni](#kni)
  * [KNIError](#kni.KNIError)
  * [KNI](#kni.KNI)
    * [KNI\_MaxRecordLength](#kni.KNI.KNI_MaxRecordLength)
    * [\_\_init\_\_](#kni.KNI.__init__)
    * [get\_version](#kni.KNI.get_version)
    * [get\_full\_version](#kni.KNI.get_full_version)
    * [set\_log\_file\_name](#kni.KNI.set_log_file_name)
    * [open\_stream](#kni.KNI.open_stream)
    * [close\_stream](#kni.KNI.close_stream)
    * [recode\_stream\_record](#kni.KNI.recode_stream_record)
    * [set\_secondary\_header\_line](#kni.KNI.set_secondary_header_line)
    * [set\_external\_table](#kni.KNI.set_external_table)
    * [finish\_opening\_stream](#kni.KNI.finish_opening_stream)
    * [set\_secondary\_input\_record](#kni.KNI.set_secondary_input_record)
    * [get\_stream\_max\_memory](#kni.KNI.get_stream_max_memory)
    * [set\_stream\_max\_memory](#kni.KNI.set_stream_max_memory)
    * [get\_error\_message](#kni.KNI.get_error_message)

<a id="kni"></a>

# kni

Khiops Native Interface (KNI) Python wrapper using ctypes.

This module provides a Python interface to the Khiops Native Interface (KNI) C library,
allowing direct deployment of Khiops models without temporary files.

<a id="kni.KNIError"></a>

## KNIError Objects

```python
class KNIError(Exception)
```

Exception raised for KNI errors.

<a id="kni.KNI"></a>

## KNI Objects

```python
class KNI()
```

Python wrapper for Khiops Native Interface using ctypes.

<a id="kni.KNI.KNI_MaxRecordLength"></a>

#### KNI\_MaxRecordLength

8 MB

<a id="kni.KNI.__init__"></a>

#### \_\_init\_\_

```python
def __init__(library_path: str | bytes | Path | None = None)
```

Initialize the KNI wrapper.

**Arguments**:

- `library_path` - Optional path to the KNI shared library (str, bytes, or
  pathlib.Path). If None, attempts to locate it automatically.

<a id="kni.KNI.get_version"></a>

#### get\_version

```python
def get_version() -> int
```

Get KNI version as integer (10*major + minor).

<a id="kni.KNI.get_full_version"></a>

#### get\_full\_version

```python
def get_full_version() -> str
```

Get KNI full version string.

<a id="kni.KNI.set_log_file_name"></a>

#### set\_log\_file\_name

```python
def set_log_file_name(log_file_name: str | bytes) -> None
```

Set the log file name for error messages.

**Arguments**:

- `log_file_name` - Path to log file (str or bytes, empty string for no logging)
  

**Raises**:

- `KNIError` - If setting log file fails
- `TypeError` - If log_file_name is not str or bytes

<a id="kni.KNI.open_stream"></a>

#### open\_stream

```python
def open_stream(dictionary_file_path: str | bytes | Path,
                dictionary_name: str | bytes,
                header_line: str | bytes,
                field_separator: str | bytes = "\t") -> int
```

Open a KNI stream for recoding.

**Arguments**:

- `dictionary_file_path` - Path to the dictionary file (str, bytes, or pathlib.Path)
- `dictionary_name` - Name of the dictionary to use (str or bytes)
- `header_line` - Header line with field names (str or bytes)
- `field_separator` - Character used to separate fields (str or bytes, default: tab)
  

**Returns**:

  Stream handle (positive integer)
  

**Raises**:

- `KNIError` - If opening stream fails
- `TypeError` - If arguments have invalid types

<a id="kni.KNI.close_stream"></a>

#### close\_stream

```python
def close_stream(stream_handle: int) -> None
```

Close a KNI stream.

**Arguments**:

- `stream_handle` - Handle returned by open_stream (int)
  

**Raises**:

- `KNIError` - If closing stream fails
- `TypeError` - If stream_handle is not int

<a id="kni.KNI.recode_stream_record"></a>

#### recode\_stream\_record

```python
def recode_stream_record(stream_handle: int,
                         input_record: str | bytes,
                         max_output_length: int | None = None) -> str
```

Recode an input record using the stream's dictionary.

**Arguments**:

- `stream_handle` - Handle returned by open_stream (int)
- `input_record` - Input record (str or bytes)
- `max_output_length` - Maximum output buffer size (int, default: KNI_MaxRecordLength)
  

**Returns**:

  Recoded output string
  

**Raises**:

- `KNIError` - If recoding fails
- `TypeError` - If arguments have invalid types

<a id="kni.KNI.set_secondary_header_line"></a>

#### set\_secondary\_header\_line

```python
def set_secondary_header_line(stream_handle: int, data_path: str | bytes,
                              header_line: str | bytes) -> None
```

Set the header line of a secondary table (multi-table only).

**Arguments**:

- `stream_handle` - Handle returned by open_stream (int)
- `data_path` - Data path identifying the secondary table (str or bytes)
- `header_line` - Header line with field names (str or bytes)
  

**Raises**:

- `KNIError` - If setting secondary header fails
- `TypeError` - If arguments have invalid types

<a id="kni.KNI.set_external_table"></a>

#### set\_external\_table

```python
def set_external_table(stream_handle: int, data_root: str | bytes,
                       data_path: str | bytes,
                       data_table_file_name: str | bytes) -> None
```

Set the name of a data file for an external table (multi-table only).

**Arguments**:

- `stream_handle` - Handle returned by open_stream (int)
- `data_root` - Root dictionary of the external table (str or bytes)
- `data_path` - Data path for secondary external tables (str or bytes, empty for root)
- `data_table_file_name` - Path to the external table data file (str or bytes)
  

**Raises**:

- `KNIError` - If setting external table fails
- `TypeError` - If arguments have invalid types

<a id="kni.KNI.finish_opening_stream"></a>

#### finish\_opening\_stream

```python
def finish_opening_stream(stream_handle: int) -> None
```

Finish opening a stream (multi-table only).

Must be called after all secondary headers and external tables are set.

**Arguments**:

- `stream_handle` - Handle returned by open_stream (int)
  

**Raises**:

- `KNIError` - If finishing opening stream fails
- `TypeError` - If stream_handle is not int

<a id="kni.KNI.set_secondary_input_record"></a>

#### set\_secondary\_input\_record

```python
def set_secondary_input_record(stream_handle: int, data_path: str | bytes,
                               input_record: str | bytes) -> None
```

Set a secondary input record for multi-table recoding.

All secondary records must be set before recoding the primary record.

**Arguments**:

- `stream_handle` - Handle returned by open_stream (int)
- `data_path` - Data path identifying the secondary table (str or bytes)
- `input_record` - Secondary input record (str or bytes)
  

**Raises**:

- `KNIError` - If setting secondary input record fails
- `TypeError` - If arguments have invalid types

<a id="kni.KNI.get_stream_max_memory"></a>

#### get\_stream\_max\_memory

```python
def get_stream_max_memory() -> int
```

Get the maximum amount of memory (in MB) for stream opening.

**Returns**:

  Maximum memory in MB

<a id="kni.KNI.set_stream_max_memory"></a>

#### set\_stream\_max\_memory

```python
def set_stream_max_memory(max_mb: int) -> int
```

Set the maximum amount of memory (in MB) for stream opening.

**Arguments**:

- `max_mb` - Maximum memory in MB (int)
  

**Returns**:

  Accepted value (bounded by system limits)

<a id="kni.KNI.get_error_message"></a>

#### get\_error\_message

```python
@staticmethod
def get_error_message(error_code: int) -> str
```

Get a human-readable error message for an error code.

**Arguments**:

- `error_code` - KNI error code
  

**Returns**:

  Error message string

