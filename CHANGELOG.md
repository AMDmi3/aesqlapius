# Changelog

## 0.0.4

* Add sqlite3 support
* Remove stray print in the module

## 0.0.3

* Queries may now return *dict* of rows by specified (by either
  name or index) column, with possibility to omit key column from
  the output.
* Queries may now return single value (scalar) as row type.

## 0.0.2

* Added global `generate_api()` entry point for all supported
  drivers. Driver is now selected by a string argument.
* Replace `file_as_namespace` flag with clearer `namespace_mode`
  argument which allows `dirs`, `files` and a new `flat` modes.
* Allow loading queries from a plain file
* Added documentation

## 0.0.1

* Initial release
