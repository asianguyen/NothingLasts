import asyncio
from bleak import BleakScanner

async def scan():
    print("Scanning for 10 seconds...")
    devices = await BleakScanner.discover(timeout=10)
    for d in devices:
        print(f"  {d.name or '(no name)':30s}  {d.address}")

asyncio.run(scan())
