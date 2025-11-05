# Example Usage for Load Profile Reader

This document provides practical examples for using the `read_load_profile.py` script with Landis and Gyr meters.

## Quick Start Examples

### Example 1: Basic TCP/IP Connection (LG Meter with Short Name Referencing)

```bash
python read_load_profile.py -h 192.168.1.100 -p 4059 -c 16 -s 1 -r sn
```

This is the most common configuration for Landis and Gyr meters:
- `-h 192.168.1.100`: Meter IP address
- `-p 4059`: TCP port (4059 is common for DLMS)
- `-c 16`: Client address (16 is standard public client)
- `-s 1`: Server address (1 is default)
- `-r sn`: Use Short Name referencing (typical for LG meters)

### Example 2: Serial Connection

```bash
python read_load_profile.py -S COM1:9600:8None1 -c 16 -s 1 -r sn
```

For serial connections:
- `-S COM1:9600:8None1`: Serial port configuration
  - COM1: Port name (use `/dev/ttyUSB0` on Linux)
  - 9600: Baud rate
  - 8: Data bits
  - None: No parity
  - 1: Stop bits

### Example 3: With Authentication

```bash
python read_load_profile.py -h 192.168.1.100 -p 4059 -c 16 -s 1 -r sn -a Low -P mypassword
```

If your meter requires authentication:
- `-a Low`: Authentication level (None, Low, High)
- `-P mypassword`: Password (use `0x` prefix for hex values)

### Example 4: With Encryption (Ciphering)

```bash
python read_load_profile.py -h 192.168.1.100 -p 4059 -c 16 -s 1 -r sn \
  -C AuthenticationEncryption \
  -T 4C47453031323334 \
  -A D0D1D2D3D4D5D6D7D8D9DADBDCDDDEDF \
  -B 000102030405060708090A0B0C0D0E0F
```

For encrypted communication:
- `-C AuthenticationEncryption`: Security level
- `-T`: Client system title (8 bytes hex)
- `-A`: Authentication key (16 bytes hex)
- `-B`: Block cipher key (16 bytes hex)

### Example 5: Custom Output File

```bash
python read_load_profile.py -h 192.168.1.100 -p 4059 -c 16 -s 1 -r sn -o meter_12345
```

The `-o` parameter will create a file named `meter_12345_load_profile.txt`

### Example 6: Verbose Logging

```bash
python read_load_profile.py -h 192.168.1.100 -p 4059 -c 16 -s 1 -r sn -t Verbose
```

Use `-t Verbose` for detailed logging during the read process. Options:
- `Error`: Only errors
- `Warning`: Warnings and errors
- `Info`: General information (default)
- `Verbose`: Detailed debugging information

## Common Landis and Gyr Configurations

### E650 Series (TCP/IP)
```bash
python read_load_profile.py -h 192.168.1.100 -p 4059 -c 16 -s 1 -r sn -a None
```

### E350 Series (Serial)
```bash
python read_load_profile.py -S COM1:9600:8None1 -c 16 -s 1 -r sn -i HDLC
```

### ZMD Series (with authentication)
```bash
python read_load_profile.py -h 192.168.1.100 -p 4059 -c 16 -s 1 -r sn -a Low -P 0x00000000
```

## Expected Output

After successful execution, you will get:
1. Console output showing:
   - Connection status
   - Capture objects (columns in the load profile)
   - Progress messages
   - Summary of entries retrieved

2. A text file (`load_profile_data.txt` or custom name) containing:
   - Header with connection details
   - Date range
   - Column headers
   - Data rows with timestamps and values
   - Summary footer

## Troubleshooting

### Connection Failed
- Check IP address and port
- Verify network connectivity: `ping [IP_ADDRESS]`
- Ensure meter is powered and accessible

### Authentication Failed
- Verify password is correct
- Try without authentication first (`-a None`)
- Check if hex password needs `0x` prefix

### No Data Retrieved
- Verify the meter has load profile data for the requested period
- Check if the meter supports the standard load profile OBIS code (1.0.99.1.0.255)
- Try a shorter date range

### Timeout Errors
- Increase the wait time in GXDLMSReader (edit the script if needed)
- Check network latency
- Verify meter is responding

## Additional Notes

- The script automatically retrieves data for the last 31 days
- Load profile interval (15/30/60 minutes) is read from the meter
- The output file can be imported into Excel or analyzed with text tools
- For best results, use Verbose logging the first time to verify connection parameters
