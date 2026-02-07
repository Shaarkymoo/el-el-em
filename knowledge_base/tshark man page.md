## tshark man page

Name

tshark - Dump and analyze network traffic
Synopsis

tshark [ -a <capture autostop condition> ] ... [ -b <capture ring buffer option>] ... [ -B <capture buffer size (Win32 only)> ] [ -c <capture packet count> ] [ -C <configuration profile> ] [ -d <layer type>==<selector>,<decode-as protocol> ] [ -D ] [ -e <field> ] [ -E <field print option> ] [ -f <capture filter> ] [ -F <file format> ] [ -h ] [ -i <capture interface>|- ] [ -K <keytab> ] [ -l ] [ -L ] [ -n ] [ -N <name resolving flags> ] [ -o <preference setting> ] ... [ -p ] [ -q ] [ -r <infile> ] [ -R <read (display) filter> ] [ -s <capture snaplen> ] [ -S ] [ -t ad|a|r|d|dd|e ] [ -T pdml|psml|ps|text|fields ] [ -v ] [ -V ] [ -w <outfile>|- ] [ -x ] [ -X <eXtension option>] [ -y <capture link type> ] [ -z <statistics> ] [ <capture filter> ]
Description

TShark is a network protocol analyzer. It lets you capture packet data from a live network, or read packets from a previously saved capture file, either printing a decoded form of those packets to the standard output or writing the packets to a file. TShark's native capture file format is libpcap format, which is also the format used by tcpdump and various other tools.

Without any options set, TShark will work much like tcpdump. It will use the pcap library to capture traffic from the first available network interface and displays a summary line on stdout for each received packet.

TShark is able to detect, read and write the same capture files that are supported by Wireshark. The input file doesn't need a specific filename extension; the file format and an optional gzip compression will be automatically detected. Near the beginning of the DESCRIPTION section of wireshark(1) or <http://www.wireshark.org/docs/man-pages/wireshark.html> is a detailed description of the way Wireshark handles this, which is the same way Tshark handles this.

Compressed file support uses (and therefore requires) the zlib library. If the zlib library is not present, TShark will compile, but will be unable to read compressed files.

If the -w option is not specified, TShark writes to the standard output the text of a decoded form of the packets it captures or reads. If the -w option is specified, TShark writes to the file specified by that option the raw data of the packets, along with the packets' time stamps.

When writing a decoded form of packets, TShark writes, by default, a summary line containing the fields specified by the preferences file (which are also the fields displayed in the packet list pane in Wireshark), although if it's writing packets as it captures them, rather than writing packets from a saved capture file, it won't show the "frame number" field. If the -V option is specified, it writes instead a view of the details of the packet, showing all the fields of all protocols in the packet.

If you want to write the decoded form of packets to a file, run TShark without the -w option, and redirect its standard output to the file (do not use the -w option).

When writing packets to a file, TShark, by default, writes the file in libpcap format, and writes all of the packets it sees to the output file. The -F option can be used to specify the format in which to write the file. This list of available file formats is displayed by the -F flag without a value. However, you can't specify a file format for a live capture.

Read filters in TShark, which allow you to select which packets are to be decoded or written to a file, are very powerful; more fields are filterable in TShark than in other protocol analyzers, and the syntax you can use to create your filters is richer. As TShark progresses, expect more and more protocol fields to be allowed in read filters.

Packet capturing is performed with the pcap library. The capture filter syntax follows the rules of the pcap library. This syntax is different from the read filter syntax. A read filter can also be specified when capturing, and only packets that pass the read filter will be displayed or saved to the output file; note, however, that capture filters are much more efficient than read filters, and it may be more difficult for TShark to keep up with a busy network if a read filter is specified for a live capture.

A capture or read filter can either be specified with the -f or -R option, respectively, in which case the entire filter expression must be specified as a single argument (which means that if it contains spaces, it must be quoted), or can be specified with command-line arguments after the option arguments, in which case all the arguments after the filter arguments are treated as a filter expression. Capture filters are supported only when doing a live capture; read filters are supported when doing a live capture and when reading a capture file, but require TShark to do more work when filtering, so you might be more likely to lose packets under heavy load if you're using a read filter. If the filter is specified with command-line arguments after the option arguments, it's a capture filter if a capture is being done (i.e., if no -r option was specified) and a read filter if a capture file is being read (i.e., if a -r option was specified).
Options

-a <capture autostop condition>

    Specify a criterion that specifies when TShark is to stop writing to a capture file. The criterion is of the form test:value, where test is one of:

    duration:value Stop writing to a capture file after value seconds have elapsed.

    filesize:value Stop writing to a capture file after it reaches a size of value kilobytes (where a kilobyte is 1024 bytes). If this option is used together with the -b option, TShark will stop writing to the current capture file and switch to the next one if filesize is reached. When reading a capture file, TShark will stop reading the file after the number of bytes read exceeds this number (the complete packet will be read, so more bytes than this number may be read).

    files:value Stop writing to capture files after value number of files were written. 
-b <capture ring buffer option>
    Cause TShark to run in "multiple files" mode. In "multiple files" mode, TShark will write to several capture files. When the first capture file fills up, TShark will switch writing to the next file and so on.

    The created filenames are based on the filename given with the -w option, the number of the file and on the creation date and time, e.g. outfile_00001_20050604120117.pcap, outfile_00001_20050604120523.pcap, ...

    With the files option it's also possible to form a "ring buffer". This will fill up new files until the number of files specified, at which point TShark will discard the data in the first file and start writing to that file and so on. If the files option is not set, new files filled up until one of the capture stop conditions match (or until the disk if full).

    The criterion is of the form key:value, where key is one of:

    duration:value switch to the next file after value seconds have elapsed, even if the current file is not completely filled up.

    filesize:value switch to the next file after it reaches a size of value kilobytes (where a kilobyte is 1024 bytes).

    files:value begin again with the first file after value number of files were written (form a ring buffer). 
-B <capture buffer size (Win32 only)>
    Win32 only: set capture buffer size (in MB , default is 1MB). This is used by the the capture driver to buffer packet data until that data can be written to disk. If you encounter packet drops while capturing, try to increase this size. 
-c <capture packet count>
    Set the maximum number of packets to read when capturing live data. If reading a capture file, set the maximum number of packets to read. 
-C <configuration profile>
    Run with the given configuration profile. 
-d <layer type>==<selector>,<decode-as protocol>
    Like Wireshark's Decode As... feature, this lets you specify how a layer type should be dissected. If the layer type in question (for example, tcp.port or udp.port for a TCP or UDP port number) has the specified selector value, packets should be dissected as the specified protocol.

    Example: -d tcp.port==8888,http will decode any traffic running over TCP port 8888 as HTTP .

    Using an invalid selector or protocol will print out a list of valid selectors and protocol names, respectively.

    Example: -d . is a quick way to get a list of valid selectors.

    Example: -d ethertype==0x0800. is a quick way to get a list of protocols that can be selected with an ethertype. 
-D

Print a list of the interfaces on which TShark can capture, and exit. For each network interface, a number and an interface name, possibly followed by a text description of the interface, is printed. The interface name or the number can be supplied to the -i option to specify an interface on which to capture.
This can be useful on systems that don't have a command to list them (e.g., Windows systems, or UNIX systems lacking ifconfig -a); the number can be useful on Windows 2000 and later systems, where the interface name is a somewhat complex string.

Note that "can capture" means that TShark was able to open that device to do a live capture. Depending on your system you may need to run tshark from an account with special privileges (for example, as root) to be able to capture network traffic. If TShark -D is not run from such an account, it will not list any interfaces.
-e <field>
    Add a field to the list of fields to display if -T fields is selected. This option can be used multiple times on the command line. At least one field must be provided if the -T fields option is selected.

    Example: -e frame.number -e ip.addr -e udp

    Giving a protocol rather than a single field will print multiple items of data about the protocol as a single field. Fields are separated by tab characters by default. -E controls the format of the printed fields. 
-E <field print option>
    Set an option controlling the printing of fields when -T fields is selected.

    Options are:

    header=y|n If y, print a list of the field names given using -e as the first line of the output; the field name will be separated using the same character as the field values. Defaults to n.

    separator=/t|/s|<character> Set the separator character to use for fields. If /t tab will be used (this is the default), if /s, s single space will be used. Otherwise any character that can be accepted by the command line as part of the option may be used.

    quote=d|s|n Set the quote character to use to surround fields. d uses double-quotes, s single-quotes, n no quotes (the default). 
-f <capture filter>
    Set the capture filter expression. 
-F <file format>
    Set the file format of the output capture file written using the -w option. The output written with the -w option is raw packet data, not text, so there is no -F option to request text output. The option -F without a value will list the available formats. 
-h

Print the version and options and exits.
-i <capture interface>|-
    Set the name of the network interface or pipe to use for live packet capture.

    Network interface names should match one of the names listed in "tshark -D" (described above); a number, as reported by "tshark -D", can also be used. If you're using UNIX , "netstat -i" or "ifconfig -a" might also work to list interface names, although not all versions of UNIX support the -a option to ifconfig.

    If no interface is specified, TShark searches the list of interfaces, choosing the first non-loopback interface if there are any non-loopback interfaces, and choosing the first loopback interface if there are no non-loopback interfaces. If there are no interfaces at all, TShark reports an error and doesn't start the capture.

    Pipe names should be either the name of a FIFO (named pipe) or ''-'' to read data from the standard input. Data read from pipes must be in standard libpcap format.

    Note: the Win32 version of TShark doesn't support capturing from pipes! 
-K <keytab>
    Load kerberos crypto keys from the specified keytab file. This option can be used multiple times to load keys from several files.

    Example: -K krb5.keytab 
-l

Flush the standard output after the information for each packet is printed. (This is not, strictly speaking, line-buffered if -V was specified; however, it is the same as line-buffered if -V wasn't specified, as only one line is printed for each packet, and, as -l is normally used when piping a live capture to a program or script, so that output for a packet shows up as soon as the packet is seen and dissected, it should work just as well as true line-buffering. We do this as a workaround for a deficiency in the Microsoft Visual C ++ C library.)
This may be useful when piping the output of TShark to another program, as it means that the program to which the output is piped will see the dissected data for a packet as soon as TShark sees the packet and generates that output, rather than seeing it only when the standard output buffer containing that data fills up.
-L

List the data link types supported by the interface and exit. The reported link types can be used for the -y option.

-n

Disable network object name resolution (such as hostname, TCP and UDP port names), the -N flag might override this one.
-N <name resolving flags>
    Turn on name resolving only for particular types of addresses and port numbers, with name resolving for other types of addresses and port numbers turned off. This flag overrides -n if both -N and -n are present. If both -N and -n flags are not present, all name resolutions are turned on.

    The argument is a string that may contain the letters:

    m to enable MAC address resolution

    n to enable network address resolution

    t to enable transport-layer port number resolution

    C to enable concurrent (asynchronous) DNS lookups 
-o <preference>:<value>
    Set a preference value, overriding the default value and any value read from a preference file. The argument to the option is a string of the form prefname:value, where prefname is the name of the preference (which is the same name that would appear in the preference file), and value is the value to which it should be set. 
-p

Don't put the interface into promiscuous mode. Note that the interface might be in promiscuous mode for some other reason; hence, -p cannot be used to ensure that the only traffic that is captured is traffic sent to or from the machine on which TShark is running, broadcast traffic, and multicast traffic to addresses received by that machine.

-q

When capturing packets, don't display the continuous count of packets captured that is normally shown when saving a capture to a file; instead, just display, at the end of the capture, a count of packets captured. On systems that support the SIGINFO signal, such as various BSDs, you can cause the current count to be displayed by typing your "status" character (typically control-T, although it might be set to "disabled" by default on at least some BSDs, so you'd have to explicitly set it to use it).
When reading a capture file, or when capturing and not saving to a file, don't print packet information; this is useful if you're using a -z option to calculate statistics and don't want the packet information printed, just the statistics.
-r <infile>
    Read packet data from infile, can be any supported capture file format (including gzipped files). It's not possible to use named pipes or stdin here! 
-R <read (display) filter>
    Cause the specified filter (which uses the syntax of read/display filters, rather than that of capture filters) to be applied before printing a decoded form of packets or writing packets to a file; packets not matching the filter are discarded rather than being printed or written. 
-s <capture snaplen>
    Set the default snapshot length to use when capturing live data. No more than snaplen bytes of each network packet will be read into memory, or saved to disk. A value of 0 specifies a snapshot length of 65535, so that the full packet is captured; this is the default. 
-S

Decode and display packets even while writing raw packet data using the -w option.
-t ad|a|r|d|dd|e
    Set the format of the packet timestamp printed in summary lines. The format can be one of:

    ad absolute with date: The absolute date and time is the actual time and date the packet was captured

    a absolute: The absolute time is the actual time the packet was captured, with no date displayed

    r relative: The relative time is the time elapsed between the first packet and the current packet

    d delta: The delta time is the time since the previous packet was captured

    dd delta_displayed: The delta_displayed time is the time since the previous displayed packet was captured

    e epoch: The time in seconds since epoch (Jan 1, 1970 00:00:00)

    The default format is relative. 
-T pdml|psml|ps|text|fields
    Set the format of the output when viewing decoded packet data. The options are one of:

    pdml Packet Details Markup Language, an XML-based format for the details of a decoded packet. This information is equivalent to the packet details printed with the -V flag.

    psml Packet Summary Markup Language, an XML-based format for the summary information of a decoded packet. This information is equivalent to the information shown in the one-line summary printed by default.

    ps PostScript for a human-readable one-line summary of each of the packets, or a multi-line view of the details of each of the packets, depending on whether the -V flag was specified.

    text Text of a human-readable one-line summary of each of the packets, or a multi-line view of the details of each of the packets, depending on whether the -V flag was specified. This is the default.

    fields The values of fields specified with the -e option, in a form specified by the -E option. 
-v

Print the version and exit.

-V

Cause TShark to print a view of the packet details rather than a one-line summary of the packet.
-w <outfile>|-
    Write raw packet data to outfile or to the standard output if outfile is '-'.

    NOTE: -w provides raw packet data, not text. If you want text output you need to redirect stdout (e.g. using '>'), don't use the -w option for this. 
-x

Cause TShark to print a hex and ASCII dump of the packet data after printing the summary or details.
-X <eXtension options>
    Specify an option to be passed to a TShark module. The eXtension option is in the form extension_key:value, where extension_key can be:

    lua_script:lua_script_filename tells Wireshark to load the given script in addition to the default Lua scripts. 
-y <capture link type>
    Set the data link type to use while capturing packets. The values reported by -L are the values that can be used. 
-z <statistics>
    Get TShark to collect various types of statistics and display the result after finishing reading the capture file. Use the -q flag if you're reading a capture file and only want the statistics printed, not any per-packet information. 