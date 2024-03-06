import time
import docker
import argparse
import logging
from docker.models.containers import Container
from mcrcon import MCRcon
import sys


class MC_Server_Controller:

    container: Container = None
    def __init__(self, level_str, name, max_ram, port, rcon, volumes, hardcore, difficulty, version):
        self.level_str = level_str
        self.name = name
        self.max_ram = max_ram
        self.port = port
        self.rcon = rcon
        self.volumes = volumes
        self.hardcore = hardcore
        self.difficulty = difficulty
        self.version = version

        self.server_running = False
        self.client = docker.from_env()
        self.last_restart_time = time.time()


        self.set_up_logging(self.level_str)
        self.start_docker_container()
        logging.info('Server started')

    
    def run(self):
        logging.info('Starting server monitor')
        

        while self.server_running:
            self.container.reload()
            logging.debug(f"Container status: {self.container.status}")
            time.sleep(3)

            current_time = time.time()

            logging.debug(f'current time: {current_time} last restart time: {self.last_restart_time}')
            if current_time - self.last_restart_time >=  24 * 60 * 60:
                self.restart_server()
                self.last_restart_time = current_time


    def set_up_logging(self, level_str):
        if level_str == 'DEBUG':
            logging_level = logging.DEBUG
        elif level_str == 'CRITICAL':
            logging_level = logging.CRITICAL
        elif level_str == 'ERROR':
            logging_level = logging.ERROR
        elif level_str == 'WARNING':
            logging_level = logging.WARNING
        else:
            logging_level = logging.INFO

        logging.basicConfig(filename='server.log', level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

        # Create a stream handler to print logs to the terminal
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging_level)
        stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Add the stream handler to the root logger
        logging.getLogger().addHandler(stream_handler)

    def start_docker_container(self):

        if self.client.containers.list(filters={'name': self.name}): 
            logging.error(f'Container with name {self.name} already exists')
            raise Exception(f'Container with name {self.name} already exists')

        logging.info('Starting Minecraft server with the following parameters:')
        logging.info(f'Max RAM: {self.max_ram}')
        logging.info(f'Port: {self.port}')
        logging.info(f'RCON: {self.rcon}') 
        logging.info(f'Volumes: {self.volumes}')
        logging.info(f'Hardcore: {self.hardcore}')
        logging.info(f'Difficulty: {self.difficulty}')
        logging.info(f'Version: {self.version}')

        f_port: dict = {f'25565/tcp': self.port}
        
        f_environment: list = [
            f'EULA=TRUE',
            f'MEMORY={self.max_ram}',
            f'HARDCORE={self.hardcore}',
            f'DIFFICULTY={self.difficulty}',
        ]

        f_port.update({f'25575/tcp': 25575})
        f_environment.append(f'RCON_ENABLED=true')
        f_environment.append(f'RCON_PASSWORD={self.rcon}')

        self.container = self.client.containers.run(
            'itzg/minecraft-server',
            detach=True,
            name=self.name,
            ports=f_port,
            environment=f_environment,
            volumes={self.volumes:  {'bind': '/data/world', 'mode': 'rw'}},
        )
        
        self.__check_server_online()

        logging.info(f'Minecraft server started with container ID: {self.container.id}')

        self.server_running = True
        
    def restart_server(self):
        logging.info("Restarting server")
        if self.server_running:
            self.shutdown_server()
            
            self.start_docker_container()
        else:
            logging.error("Server is not running")


    def shutdown_server(self):
        logging.debug("Stopping server")
        if self.server_running:

            self.send_command("say !! The server will reset in 30 minute !!")

            time.sleep(60 * 20)

            self.send_command("say !! The server will reset in 10 minutes !!")

            time.sleep(60 * 9)

            self.send_command("say !! The world will reset in 45 seconds !!")

            time.sleep(40)

            self.send_command("say !! The server will reset 5 seconds !!")

            time.sleep(5)
            
            self.send_command("say !! The server is being shut down !!") 
            self.send_command("say !! It will restart in a few minutes !!")

            time.sleep(3)
            
            logging.info("Server shutdown beginning")

            self.container.stop()

            time.sleep(10)
            
            self.container.remove()

            self.server_running = False
            print("Server Fully Stopped")
        else:
            logging.debug("Server is already shutdown")

    def send_command(self, command):
        response = ''

        logging.info(f'Sending command: {command}')
        try:
            # Replace 'your_rcon_password' and 'your_minecraft_server_ip' with your actual RCON password and server IP
            with MCRcon('0.0.0.0', 'super', 25575, timeout=10) as client:
                response = client.command(command)
                logging.debug(f'Message Response: {response}')
        except:
            logging.error(f'Command Failed {command}')
            return 'failed'
        
        return response
    
    def __check_server_online(self):
        response = self.send_command("say hi")

        while response == 'failed':
            time.sleep(6)
            response = self.send_command("say hi")
            
        
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Minecraft server with Docker')
    parser.add_argument('--max-ram', default='2G', help='Maximum RAM for the server')
    parser.add_argument('--port', '-p', default=25565, type=int, help='Port to run the server on')
    parser.add_argument('--rcon', default='super', type=str, help='Password for the RCON for the server. Default leave RCON off.')
    parser.add_argument('--volumes', '-v', help='List of volumes to mount to the server')
    parser.add_argument('--hardcore', default=False, type=bool, help='Enable hardcore mode for the server. Default is false.')
    parser.add_argument('--difficulty', default=2, type=int, help='Set the difficulty for the server using ints (easy 1, medium 2, hard 3). Default is normal (2).')
    parser.add_argument('--version', default='latest', help='Minecraft server version')
    parser.add_argument('--name', '-n', default='minecraft-server', help='Minecraft server name')
    parser.add_argument('--log-level', '-l', default=None, help='Set the logging level for the server')

    if parser.parse_args().volumes == None:
        parser.error('Please provide a volume to mount to the server')

    controller = MC_Server_Controller(
        parser.parse_args().log_level,
        parser.parse_args().name,
        parser.parse_args().max_ram,
        parser.parse_args().port,
        parser.parse_args().rcon,
        parser.parse_args().volumes,
        parser.parse_args().hardcore,
        parser.parse_args().difficulty,
        parser.parse_args().version
    )
    controller.run()