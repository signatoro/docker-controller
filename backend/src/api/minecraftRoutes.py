
from fastapi import APIRouter

from schema.minecraftServerInfromation import McServerInformation
from controller.minecraftControllers import McContainerController



class McRoutes():
    router: APIRouter = APIRouter(
        prefix='/mc',
        tags=['Minecraft']
    )

    def __init__(self, controller: McContainerController):
        self.controller = controller
        self.router.add_api_route("/server", self.add_minecraft_server, methods=["POST"])
        self.router.add_api_route("/server/{id}", self.whitelist_player, methods=["POST"])

    
    async def add_minecraft_server(self, server_info: McServerInformation):
        print(f'Inputed Server Info {server_info}')
        self.controller.add_minecraft_server(server_info)

    async def whitelist_player(self,id: str, username: str):
        print("In route")
        self.controller.whitelist_player(id, username)