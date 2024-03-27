import os
import time
import docker
import argparse
import logging
import shutil
import daemon
from logging.handlers import RotatingFileHandler
from docker.models.containers import Container
from mcrcon import MCRcon

class MC_Server_Controller:

    container: Container = None
    def __init__(self, name, max_ram, port, rcon, volumes, hardcore, difficulty, version, take_new):


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
        
        self.start_docker_container(take_new=take_new)
    
    def run(self):
        logging.info('Starting server monitor')
        logging.info(f'Pid 2: {os.getpid()}')
        

        while self.server_running:
            self.container.reload()
            time.sleep(10)

            current_time = time.time()

            logging.debug(f'current time: {current_time} last restart time: {self.last_restart_time}')
            if current_time - self.last_restart_time >= 24 * 60 * 60:
                self.restart_server()
                self.last_restart_time = current_time

    def start_docker_container(self, take_new=False):
        logging.info('Starting server')

        if self.client.containers.list(all=True, filters={'name': self.name}):

            logging.info(f'Container {self.name} exists')
            self.container = self.client.containers.get(self.name)


            self.__check_environment(take_new)


            if self.container.status == 'exited':
                logging.debug(f'Container {self.name} is stopped. starting...')
                self.container.start()
                self.__check_server_online()
                self.server_running = True

            elif self.container.status == 'running':
                logging.debug(f'Container {self.name} is already running')
                self.server_running = True 
                self.run()

            else:
                logging.error(f'!! Unknown Status !! Container status: {self.container.status}')
                raise Exception(f'!! Unknown Status !! Container status: {self.container.status}')
        else:
            logging.info(f'Container does not exist creating {self.name}')
            self.create_docker_container()

    def __check_environment(self, take_new):
        logging.debug('Checking environment variables')
        environment = self.container.attrs['Config']['Env']
        volumes = self.container.attrs['HostConfig']['Binds']

        if not take_new:
            if volumes != [f'{self.volumes}:/data:rw']:
                logging.info(f'Volumes {volumes} are different than already set.')
                logging.warning('Restart Program server with --take-new (-t) to apply new changes to the container')

            for env in environment:
                if env.startswith('EULA=') and env != 'EULA=TRUE' or \
                env.startswith('JVM_OPTS=') and env != f'JVM_OPTS=-Xms1G -Xmx{self.max_ram}' or\
                env.startswith('HARDCORE=') and env != f'HARDCORE={self.hardcore}' or \
                env.startswith('DIFFICULTY=') and env != f'DIFFICULTY={self.difficulty}' or \
                env.startswith('RCON_ENABLED=') and env != 'RCON_ENABLED=true' or \
                env.startswith('RCON_PASSWORD=') and env != f'RCON_PASSWORD={self.rcon}':
                    logging.info(f'Environment variable {env} are different than already set.')
                    logging.warning('Restart Program server with --take-new (-t) to apply new changes to the container')
        else:
            logging.info('Applying new changes to the container')

            logging.debug(f'Current Environment: m{environment}')
            logging.debug(f'Current Volumes: {volumes}')

            logging.debug('New Environment:')
            for attr, value in self.__dict__.items():
                logging.debug(f'{attr}: {value}')
            logging.debug(f'Volumes: {self.volumes}')

            if self.container.status == 'running':
                self.container.stop()
                self.__await_status('exited')

            self.container.remove()

            self.create_docker_container()

    def create_docker_container(self):
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
            f'JVM_OPTS=-Xms1G -Xmx{self.max_ram}',
            f'HARDCORE={self.hardcore}',
            f'DIFFICULTY={self.difficulty}',
        ]

        f_port.update({f'25575/tcp': 25575})
        f_environment.append('RCON_ENABLED=true')
        f_environment.append(f'RCON_PASSWORD={self.rcon}')

        self.container = self.client.containers.run(
            'itzg/minecraft-server',
            detach=True,
            name=self.name,
            ports=f_port,
            environment=f_environment,
            volumes={self.volumes:  {'bind': '/data', 'mode': 'rw'}},
        )

        
        self.__check_server_online()
        self.__await_status('running')

        logging.info(f'Minecraft server started with container ID: {self.container.id}')

        self.server_running = True
        
    def restart_server(self):
        logging.info("Restarting server Soon")
        if self.server_running:
            self.shutdown_server()
            time.sleep(3)
            self.backup_server_folder()
            time.sleep(3)
            self.start_docker_container()
        else:
            logging.error("Server is not running")


    def shutdown_server(self):
        logging.debug("Stopping server")
        if self.server_running:

            self.send_command("say !! The server will reset in 30 minute !!")

            time.sleep(20 * 60)

            self.send_command("say !! The server will reset in 10 minutes !!")

            time.sleep(9 * 60)

            self.send_command("say !! The world will reset in 45 seconds !!")

            time.sleep(40)

            self.send_command("say !! The server will reset 5 seconds !!")

            time.sleep(5)
            
            self.send_command("say !! The server is being shut down !!") 
            self.send_command("say !! It will restart in a few moments !!")

            time.sleep(3)
            
            logging.info("Server shutdown beginning")

            self.container.stop()

            # TODO: Check to see if this works.
            self.__await_status('exited')

            self.server_running = False
            time.sleep(4)
            logging.info("Server shutdown complete")
        else:
            logging.debug("Server is already shutdown")


    def backup_server_folder(self):
        logging.info("Backing up server folder")
        shutil.make_archive('server_backup', 'zip', self.volumes)
        logging.info("Backup complete")


    def send_command(self, command):
        response = ''

        logging.debug(f'Sending command: {command}')
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
    
    def __await_status(self, status):
        logging.info(f'Awaiting status: {status}')
        while self.container.status != status:
            logging.debug(f'Container status: {self.container.status}, Expected: {status}')
            time.sleep(6)
            self.container.reload()

def set_up_logging(level_str, log_file_size=1):
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

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # Add a rotating file handler to limit the log file size
    file_handler = RotatingFileHandler('server.log', maxBytes=1024*1024*log_file_size, backupCount=5)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logging.getLogger().addHandler(file_handler)

    return file_handler


def main(parser):
    # logging.info(f'Pif: {os.getpid()}')
    controller = MC_Server_Controller(
        parser.parse_args().name,
        parser.parse_args().max_ram,
        parser.parse_args().port,
        parser.parse_args().rcon,
        parser.parse_args().volumes,
        parser.parse_args().hardcore,
        parser.parse_args().difficulty,
        parser.parse_args().version,
        parser.parse_args().take_new
    )

    controller.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Minecraft server with Docker')
    parser.add_argument('-d', '--daemon',action='store_true', help='Run the server in daemon mode')
    parser.add_argument('--max-ram', default='2G', help='Maximum RAM for the server')
    parser.add_argument('--port', '-p', default=25565, type=int, help='Port to run the server on')
    parser.add_argument('--rcon', default='super', type=str, help='Password for the RCON for the server. Default leave RCON off.')
    parser.add_argument('--volumes', '-v', help='List of volumes to mount to the server')
    parser.add_argument('--hardcore', default=False, type=bool, help='Enable hardcore mode for the server. Default is false.')
    parser.add_argument('--difficulty', default=2, type=int, help='Set the difficulty for the server using ints (easy 1, medium 2, hard 3). Default is normal (2).')
    parser.add_argument('--version', default='latest', help='Minecraft server version')
    parser.add_argument('--name', '-n', default='minecraft-server', help='Minecraft server name')
    parser.add_argument('--log-level', '-l', default=None, help='Set the logging level for the server')
    parser.add_argument('--log-file-size', default=2, type=int, help='Set the max size of the log file in MB')
    parser.add_argument('--take-new', '-t', default=False, type=bool, help='Apply new changes to the container')

    fh = set_up_logging(parser.parse_args().log_level, parser.parse_args().log_file_size)

    if parser.parse_args().take_new:
        logging.warning('!! Applying new changes to the container !!')
        logging.warning('THIS WILL COMPLETELY REMOVE THE OLD CONTAINER AND CREATE A NEW ONE.')

        print ('Do you wish to proceed? (y/n)')
        if input().lower() != 'y':
            exit()
    
    if parser.parse_args().volumes == None:
        parser.error('Please provide a volume to mount to the server')

    if parser.parse_args().daemon:
        with daemon.DaemonContext(
            files_preserve=[fh.stream.fileno()]
        ):
            main(parser)
    else:
        main(parser)
