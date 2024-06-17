
from deps.dependenceis import DiscordRoute
from schema.minecraftServerInfromation import McServerInformation
from controller.minecraftControllers import McContainerController



class McRoutes():
    router: DiscordRoute = DiscordRoute(
        prefix='/mc',
        tags=['Minecraft']
    )

    def __init__(self, controller: McContainerController):
        self.controller = controller
        self.router.add_api_route('/server', self.get_servers, methods=["GET"])
        self.router.add_api_route("/server", self.create_minecraft_server, methods=["POST"])
        self.router.add_api_route("/server/{id}", self.whitelist_player, methods=["POST"])
        self.router.add_api_route("/server/{id}", self.check_players_online, methods=['GET'])
        self.router.add_api_route("/server/{id}/op", self.op_player, methods=["POST"])

    async def get_servers(self):
        return self.controller.get_servers()
    
    async def create_minecraft_server(self, server_info: McServerInformation):
        # Check if server name is already in use
        # How to do update server info
        self.controller.create_minecraft_server(server_info)

    async def whitelist_player(self, id: str, username: str):
        self.controller.whitelist_player(id, username)

    async def check_players_online(self, id: str) -> list[str]:
        return self.controller.get_server_players_online(id)
    
    async def op_player(self, id: str, username: str):
        return self.controller.op_player(id, username)