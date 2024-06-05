

from models.minecraftServer import McServer
from schema.minecraftServerInfromation import McServerInformation

class McContainerController():

    servers: dict[str: McServer]

    def __init__(self):
        self.servers: dict[str: McServer] = {}
        return
    

    async def check_servers(self):
        print("Checking Servers")
        if self.servers:
            for id, server in self.servers.items():
                await server.check()
        print("Done Checking ")

    def add_minecraft_server(self, server_info: McServerInformation):
        mc_server = McServer(
            name=server_info.name,
            max_ram=server_info.max_ram,
            port=server_info.port,
            rcon=server_info.rcon,
            volumes=server_info.volumes,
            hardcore=server_info.hardcore,
            difficulty=server_info.difficulty,
            version=server_info.version,
            raw_timezone=server_info.raw_timezone,
            reset_time=server_info.reset_time,
            seed=server_info.seed
        )

        self.servers[server_info.name] = mc_server
    
    def whitelist_player(self, id: str, username: str):
        print("in controller")
        self.servers[id].whitelist_player(username)



