#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
import os
import sys
import traceback
import datetime
import gurux_dlms
from gurux_serial import GXSerial
from gurux_net import GXNet
from gurux_dlms.enums import ObjectType, DataType
from gurux_dlms.objects.GXDLMSObjectCollection import GXDLMSObjectCollection
from gurux_dlms.objects import GXDLMSProfileGeneric
from gurux_dlms import GXDateTime, GXByteBuffer
from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader
import locale
from gurux_dlms import (
    GXDLMSException,
    GXDLMSExceptionResponse,
    GXDLMSConfirmedServiceError,
    GXDLMSClient,
)

try:
    if sys.version_info >= (3, 7):
        from importlib.metadata import version
    else:
        import pkg_resources
    # pylint: disable=broad-except
except Exception:
    # It's OK if this fails.
    print("pkg_resources not found")


# pylint: disable=too-few-public-methods,broad-except
class LoadProfileReader:
    @classmethod
    def main(cls, args):
        try:
            if sys.version_info >= (3, 7):
                print("gurux_dlms version: " + version("gurux_dlms"))
                print("gurux_net version: " + version("gurux_net"))
                print("gurux_serial version: " + version("gurux_serial"))
            else:
                print(
                    "gurux_dlms version: "
                    + pkg_resources.get_distribution("gurux_dlms").version
                )
                print(
                    "gurux_net version: "
                    + pkg_resources.get_distribution("gurux_net").version
                )
                print(
                    "gurux_serial version: "
                    + pkg_resources.get_distribution("gurux_serial").version
                )
        except Exception:
            # It's OK if this fails.
            print("pkg_resources not found")
        
        reader = None
        settings = GXSettings()
        output_filename = "load_profile_data.txt"
        
        try:
            # //////////////////////////////////////
            #  Handle command line parameters.
            ret = settings.getParameters(args)
            if ret != 0:
                return
            
            # Check if user wants to override output filename via -o parameter
            if settings.outputFile:
                # Use the output file parameter if specified, but change extension to .txt
                base_name = os.path.splitext(settings.outputFile)[0]
                output_filename = base_name + "_load_profile.txt"
            
            # //////////////////////////////////////
            #  Initialize connection settings.
            if not isinstance(settings.media, (GXSerial, GXNet)):
                raise Exception("Unknown media type.")
            
            # //////////////////////////////////////
            reader = GXDLMSReader(
                settings.client,
                settings.media,
                settings.trace,
                settings.invocationCounter,
            )
            settings.media.open()
            
            # Initialize connection
            print("Initializing connection to Landis and Gyr meter...")
            reader.initializeConnection()
            
            # Get the load profile object (1.0.99.1.0.255 is the standard LN for load profile)
            print("Reading load profile object...")
            profile = GXDLMSProfileGeneric("1.0.99.1.0.255")
            
            # Read capture objects (column definitions)
            print("Reading capture objects...")
            reader.read(profile, 3)
            
            print("Capture objects:")
            for i, (obj, attr) in enumerate(profile.captureObjects):
                print(f"  Column {i}: {obj.logicalName} - {obj.name} (Attribute {attr})")
            
            # Calculate date range for last 31 days
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=31)
            
            print(f"Reading load profile data from {start_date} to {end_date}...")
            
            # Read load profile data by date range
            # The C# code uses ReadRowsByRange which adds 1 day to the end date
            rows = reader.readRowsByRange(profile, start_date, end_date + datetime.timedelta(days=1))
            
            # Write results to file
            print(f"Writing results to {output_filename}...")
            with open(output_filename, 'w') as f:
                # Write header
                f.write("Landis and Gyr Load Profile Data\n")
                f.write("=" * 80 + "\n")
                f.write(f"Generated: {datetime.datetime.now()}\n")
                f.write(f"Date Range: {start_date} to {end_date}\n")
                f.write(f"Total Rows: {len(rows) if rows else 0}\n")
                f.write(f"Client Address: {settings.client.clientAddress}\n")
                f.write(f"Server Address: {settings.client.serverAddress}\n")
                f.write(f"Authentication: {settings.client.authentication}\n")
                if isinstance(settings.media, GXNet):
                    f.write(f"Connection: TCP/IP {settings.media.hostName}:{settings.media.port}\n")
                elif isinstance(settings.media, GXSerial):
                    f.write(f"Connection: Serial {settings.media.port}\n")
                f.write("=" * 80 + "\n\n")
                
                # Write column headers
                if profile.captureObjects:
                    header = " | ".join([f"{obj.name} ({obj.logicalName})" 
                                        for obj, attr in profile.captureObjects])
                    f.write(header + "\n")
                    f.write("-" * len(header) + "\n")
                
                # Write data rows
                if rows:
                    last_datetime = datetime.datetime(1970, 1, 1)
                    interval_minutes = 30  # Default load profile interval
                    
                    for row in rows:
                        row_str = ""
                        for i, cell in enumerate(row):
                            if row_str:
                                row_str += " | "
                            
                            # Handle different data types
                            # First column is typically the datetime
                            if i == 0:
                                if cell is None:
                                    # If datetime is NULL, increment from last datetime
                                    # This matches the C# code behavior
                                    last_datetime = last_datetime + datetime.timedelta(minutes=interval_minutes)
                                    row_str += str(last_datetime)
                                elif isinstance(cell, (bytearray, bytes)):
                                    try:
                                        dt = GXDLMSClient.changeType(cell, DataType.DATETIME)
                                        if isinstance(dt, GXDateTime):
                                            last_datetime = dt.value
                                            row_str += str(dt.value)
                                        else:
                                            row_str += GXByteBuffer.hex(cell)
                                    except Exception:
                                        row_str += GXByteBuffer.hex(cell)
                                elif isinstance(cell, (datetime.datetime, GXDateTime)):
                                    if isinstance(cell, GXDateTime):
                                        last_datetime = cell.value
                                        row_str += str(cell.value)
                                    else:
                                        last_datetime = cell
                                        row_str += str(cell)
                                else:
                                    row_str += str(cell)
                            else:
                                # For other columns, just convert to string
                                if isinstance(cell, (bytearray, bytes)):
                                    row_str += GXByteBuffer.hex(cell)
                                else:
                                    row_str += str(cell)
                        
                        f.write(row_str + "\n")
                    
                    f.write("\n" + "=" * 80 + "\n")
                    f.write(f"Successfully retrieved {len(rows)} load profile entries.\n")
                else:
                    f.write("No data retrieved.\n")
            
            print(f"Load profile data successfully written to {output_filename}")
            print(f"Total entries: {len(rows) if rows else 0}")
            
        except (
            ValueError,
            GXDLMSException,
            GXDLMSExceptionResponse,
            GXDLMSConfirmedServiceError,
        ) as ex:
            print(f"Error: {ex}")
            traceback.print_exc()
        except (KeyboardInterrupt, SystemExit, Exception) as ex:
            print(f"Error: {ex}")
            traceback.print_exc()
            if settings.media:
                settings.media.close()
            reader = None
        finally:
            if reader:
                try:
                    reader.close()
                except Exception:
                    traceback.print_exc()
            print("Ended. Press any key to continue.")


if __name__ == "__main__":
    LoadProfileReader.main(sys.argv)
