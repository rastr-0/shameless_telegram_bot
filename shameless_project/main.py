import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# this file stands for execution of extract_shifts and update_database

import extract_shifts
import update_database
import asyncio

async def main(loop):
    await update_database.update_database(extract_shifts.extract_shifts(), loop)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
