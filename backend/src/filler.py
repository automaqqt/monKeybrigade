
import asyncio
from listener.wrap import LeapListener

if __name__ == "__main__":

    from pluginloader import leap_listener_config

    async def exampleRunner():
        await LeapListener(config=leap_listener_config).process_blocks()


    asyncio.run(exampleRunner())