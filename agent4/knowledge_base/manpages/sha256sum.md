Name
sha256sum - compute and check SHA256 message digest
Synopsis
sha256sum [OPTION]... [FILE]...
Description

Print or check SHA256 (256-bit) checksums. With no FILE, or when FILE is -, read standard input.

-b, --binary
    read in binary mode 
-c, --check
    read SHA256 sums from the FILEs and check them 
-t, --text
    read in text mode (default) 
Note: There is no difference between binary and text mode option on GNU system.

The following three options are useful only when verifying checksums:

--quiet
    don't print OK for each successfully verified file 
--status
    don't output anything, status code shows success 
-w, --warn
    warn about improperly formatted checksum lines 
--help
    display this help and exit 
--version
    output version information and exit