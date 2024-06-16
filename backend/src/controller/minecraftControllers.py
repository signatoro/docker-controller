

from models.minecraftServer import McServer
from schema.minecraftServerInfromation import McServerInformation

class McContainerController():

    servers: dict[str: McServer]

    def __init__(self):
        self.servers: dict[str: McServer] = {}
        return
    
    def get_servers(self):
        return self.servers

    async def check_servers(self):
        if self.servers:
            for id, server in self.servers.items():
                await server.check()
    
    def __check_server_exists(self, id: str) -> bool:

        return False

    def create_minecraft_server(self, server_info: McServerInformation):
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
        return self.servers[id].whitelist_player(username)

    
    def check_status(self, id:str):
        return
    
    def get_server_players_online(self, id:str):
        return self.servers[id].get_players_online()
    
    def op_player(self, id: str, username: str):

        return self.servers[id].op_player(username)
         
    
    



