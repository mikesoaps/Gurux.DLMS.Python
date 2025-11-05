# Load Profile Reader for Landis and Gyr Meters

This utility is specifically designed to read load profile data from Landis and Gyr DLMS meters for the last 31 days and save it to a text file.

## Overview

The `read_load_profile.py` script is based on the standard `main.py` example but tailored specifically for reading load profile data. It:

- Connects to a Landis and Gyr meter using the DLMS protocol
- Reads load profile data from the standard load profile object (1.0.99.1.0.255)
- Retrieves data for the last 31 days
- Outputs the data to a text file (`load_profile_data.txt`)

## Usage

The script accepts all the same command-line arguments as the main.py example.

### Basic Examples

**TCP/IP Connection:**
```bash
python read_load_profile.py -h [Meter IP Address] -p [Meter Port] -c 16 -s 1 -r SN
```

**Serial Port Connection:**
```bash
python read_load_profile.py -S COM1 -c 16 -s 1 -r SN
```

**With Authentication:**
```bash
python read_load_profile.py -h [IP] -p [Port] -c 16 -s 1 -r SN -a Low -P [password]
```

### Command-Line Arguments

- `-h` : Host name or IP address
- `-p` : Port number (Example: 4059)
- `-S` : Serial port (Example: COM1 or COM1:9600:8None1)
- `-c` : Client address (Default: 16)
- `-s` : Server address (Default: 1)
- `-r` : Referencing type - `sn` (Short Name) or `ln` (Logical Name, default)
- `-a` : Authentication (None, Low, High, HighMd5, HighSha1, HighGMac, HighSha256)
- `-P` : Password for authentication (ASCII or 0x-prefixed hex)
- `-i` : Communication interface (HDLC, WRAPPER, HdlcWithModeE, Plc, PlcHdlc)
- `-t` : Trace level (Error, Warning, Info, Verbose)
- `-C` : Security Level (None, Authentication, Encrypted, AuthenticationEncryption)
- `-T` : System title for ciphering (hex string)
- `-M` : Meter system title for ciphering (hex string)
- `-A` : Authentication key for ciphering (hex string)
- `-B` : Block cipher key for ciphering (hex string)
- `-D` : Dedicated key for ciphering (hex string)
- `-v` : Invocation counter data object Logical Name
- `-I` : Auto increase invoke ID
- `-w` : HDLC Window size (Default: 1)
- `-f` : HDLC Frame size (Default: 128)
- `-W` : General Block Transfer window size
- `-d` : DLMS standard (DLMS, India, Italy, Saudi_Arabia, IDIS)
- `-L` : Manufacturer ID (Example: -L LGZ)

### Output

The script creates a file named `load_profile_data.txt` containing:
- Header with date range and total row count
- Column headers showing the captured objects
- Data rows with timestamps and values
- Summary with total entries retrieved

## Technical Details

### Load Profile Object

The script reads from the standard DLMS load profile object:
- **Logical Name:** 1.0.99.1.0.255
- **Object Type:** Profile Generic

### Date Range

The script automatically calculates the date range:
- **Start Date:** Current date minus 31 days
- **End Date:** Current date and time

### Data Format

The output file contains pipe-separated values with:
- DateTime stamps (converted from DLMS DateTime format)
- Energy values (import/export kWh, kvar, kVA)
- Other captured parameters as defined by the meter

## Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- gurux-common==1.0.13
- gurux-dlms==1.0.191
- gurux-net==1.0.22
- gurux-serial==1.0.21

## Notes

- The script defaults to Logical Name (LN) referencing. Use `-r sn` for Short Name referencing, which is typical for Landis and Gyr meters
- For HDLC connections, the default client address is 16 and server address is 1
- Authentication may be required depending on your meter configuration
- The load profile columns/captured objects are read from the meter and may vary by meter model
- The script automatically retrieves data for the last 31 days
- Load profile interval (15/30/60 minutes) is read dynamically from the meter
