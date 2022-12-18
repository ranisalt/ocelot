import argparse
import asyncio
from os import getcwd, path

from tortoise import Tortoise

from ocelot.config import load_config
from ocelot.models import database_from_env
from ocelot.rsa import RSAKey
from ocelot.session import session_from_config
from ocelot.tfs import load_map

from .world import World

parser = argparse.ArgumentParser()
parser.add_argument("--config", "-c", type=str, default="./ocelot.toml")
parser.add_argument("--debug", "-d", action="store_true", default=False)
parser.add_argument("--world", "-w", type=str, required=True)
args = parser.parse_args()

with open(path.join(getcwd(), args.config)) as fp:
    config = load_config(fp)

config_dir = path.dirname(args.config)
with open(path.join(config_dir, config.universe.private_key), "rb") as fp:
    private_key = RSAKey.from_pem(fp.read())

db_url = database_from_env(config)
session_manager = session_from_config(config.universe.session)

world_config = config.worlds[args.world]
world = World(
    id=world_config.id,
    name=world_config.name,
    db_url=db_url,
    private_key=private_key,
    session_manager=session_manager,
    map=load_map(path.join(config_dir, world_config.map.file)),
)


async def main() -> None:
    await Tortoise.init(db_url=db_url, modules={"models": ["ocelot.models"]})

    server = await asyncio.start_server(
        world.on_connect,
        host=world_config.address_unprotected,
        port=world_config.port_unprotected,
        reuse_address=True,
    )

    addrs = ", ".join(":".join(str(i) for i in s.getsockname()) for s in server.sockets)
    print(f"World {world_config.name} listening on {addrs}")

    async with server:
        await server.serve_forever()


asyncio.run(main(), debug=args.debug)
