
import csv
import datetime
import time
import shutil
import logging
import argparse
from logging.handlers import RotatingFileHandler

import docker
from mcrcon import MCRcon
from docker.models.containers import Container

class McServerController:
    """
    A class representing a Minecraft Server Controller.

    Attributes:
    - name (str): The name of the Minecraft server container.
    - max_ram (str): The maximum amount of RAM allocated to the server.
    - port (int): The port number for the server.
    - rcon (str): The RCON password for the server.
    - volumes (str): The path to the server data volume.
    - hardcore (bool): Whether hardcore mode is enabled.
    - difficulty (str): The difficultypy level of the server.
    - version (str): The version of Minecraft server to run.
    - container (Container): The Docker container object representing the Minecraft server.
    - server_running (bool): Indicates whether the server is currently running.
    - client (DockerClient): The Docker client object for interacting with Docker.
    - last_restart_time (float): The timestamp of the last server restart.

    Methods:
    - __init__(self, name, max_ram, port, rcon, volumes, hardcore, difficulty, version): 
        Initializes the Minecraft Server Controller.
    - run(self): Starts the server monitor loop.
    - start_docker_container(self): Starts the Docker container for the Minecraft server.
    - create_docker_container(self): Creates a new Docker container for the Minecraft server.
    - restart_server(self): Restarts the Minecraft server.
    - shutdown_server(self): Shuts down the Minecraft server.
    - backup_server_folder(self): Performs a backup of the server folder.
    - send_command(self, command): Sends a command to the Minecraft server via RCON.
    - __check_server_online(self): Checks if the server is online and ready to accept commands.
    - __await_status(self, status): Waits for the container status to reach the specified status.
    """

    container: Container = None

    def __init__(self, name, max_ram, port, rcon, volumes, hardcore, difficulty, version):
        """
        Initializes the Minecraft Server Controller.

        Args:
        - name (str): The name of the Minecraft server container.
        - max_ram (str): The maximum amount of RAM allocated to the server.
        - port (int): The port number for the server.
        - rcon (str): The RCON password for the server.
        - volumes (str): The path to the server data volume.
        - hardcore (bool): Whether hardcore mode is enabled.
        - difficulty (str): The difficulty level of the server.
        - version (str): The version of Minecraft server to run.
        """
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
        self.start_docker_container()

    def run(self):
        """
        Runs the server monitor.

        This method continuously monitors the server and restarts it if necessary.
        It reloads the server container every 10 seconds and checks if the time since
        the last restart is greater than or equal to 24 hours. If so, it restarts the server.

        Note: This method assumes that the `self.container` and `self.server_running`
        attributes have been properly initialized.

        Returns:
            None
        """
        logging.info('Starting server monitor')

        while self.server_running:
            self.container.reload()
            

            raw_results = self.container.stats(stream=False)
            
            csv_results = self.__generate_data_row(raw_results)

            with open('data.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_results)

            current_time = time.time()


            logging.debug(f'current time: {current_time} \
                          last restart time: {self.last_restart_time}')
            if current_time - self.last_restart_time >= 24 * 60 * 60:
                self.restart_server()
                self.last_restart_time = current_time
            
            time.sleep(10)
    
    def __generate_data_row(self, container_stats) -> tuple:

        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        total_cpu_usage = container_stats['cpu_stats']['cpu_usage']['total_usage'] - container_stats['precpu_stats']['cpu_usage']['total_usage']
        # Get the total system CPU time used
        total_system_cpu_usage = container_stats['cpu_stats']['system_cpu_usage'] - container_stats['precpu_stats']['system_cpu_usage']
        # Get the number of online CPUs
        online_cpus = container_stats['cpu_stats']['online_cpus']
        # Calculate the CPU usage percentage
        cpu_percent = (total_cpu_usage / total_system_cpu_usage) * online_cpus * 100
        # Round the result to two decimal places
        cpu_percent = round(cpu_percent, 2)

        ram_usage = container_stats['memory_stats']['usage']
        ram_limit = container_stats['memory_stats']['limit']
        ram_percent = (ram_usage / ram_limit) * 100

        ram_percent = round(ram_percent, 2)

        net_rx_bytes = container_stats['networks']['eth0']['rx_bytes']
        net_tx_bytes = container_stats['networks']['eth0']['tx_bytes']
        blk_read_bytes = sum(entry['value'] for entry in container_stats['blkio_stats']['io_service_bytes_recursive'] if entry['op'] == 'read')
        blk_write_bytes = sum(entry['value'] for entry in container_stats['blkio_stats']['io_service_bytes_recursive'] if entry['op'] == 'write')

        data_row = [time_stamp, cpu_percent, ram_percent, net_rx_bytes, net_tx_bytes, blk_read_bytes, blk_write_bytes]

        return data_row


    def start_docker_container(self):
        """
        Starts the Docker container for the Minecraft server.

        This method checks if the container already exists. If it does, 
        it checks the status of the container.
        If the container is already running, it sets the `server_running` 
        flag to True and calls the `run` method.
        If the container is stopped, it starts the container, waits for the 
        server to come online, and sets the `server_running` flag to True.
        If the container has an unknown status, it raises an exception.

        If the container does not exist, it creates a new Docker 
        container using the `create_docker_container` method.

        Returns:
            None
        """
        logging.info('Starting server')

        if self.client.containers.list(all=True, filters={'name': self.name}):
            logging.info(f'Container {self.name} exists')
            self.container = self.client.containers.get(self.name)
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


    def create_docker_container(self):
        """
        Creates a Docker container for running a Minecraft server with the specified parameters.

        This method starts a Minecraft server using the itzg/minecraft-server Docker image.
        It sets up the necessary environment variables, port mappings, and volumes for the server.
        After starting the container, it checks if the server is online and logs the container ID.

        Returns:
            None
        """
        logging.info('Starting Minecraft server with the following parameters:')
        logging.info(f'Max RAM: {self.max_ram}')
        logging.info(f'Port: {self.port}')
        logging.info(f'RCON: {self.rcon}')
        logging.info(f'Volumes: {self.volumes}')
        logging.info(f'Hardcore: {self.hardcore}')
        logging.info(f'Difficulty: {self.difficulty}')
        logging.info(f'Version: {self.version}')

        f_port: dict = {'25565/tcp': self.port}

        f_environment: list = [
            'EULA=TRUE',
            f'JVM_OPTS=-Xms1G -Xmx{self.max_ram}',
            f'HARDCORE={self.hardcore}',
            f'DIFFICULTY={self.difficulty}',
            f'TZ=America/New_York',
        ]

        f_port.update({'25575/tcp': 25575})
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

        logging.info(f'Minecraft server started with container ID: {self.container.id}')

        self.server_running = True

    def restart_server(self):
        """
        Restarts the Minecraft server.

        This method shuts down the server if it is running, backs up the server folder,
        and then starts the Docker container.

        If the server is not running, an error message is logged.

        """
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
        """
        Shuts down the Minecraft server gracefully.

        This method sends a series of commands to the server to notify
        players about the impending shutdown, waits for specific durations, and then 
        stops the server container.

        Note: The server_running attribute is set to False after the server 
        is successfully shut down.

        Returns:
            None
        """
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

            self.__await_status('exited')

            self.server_running = False
            time.sleep(4)
            logging.info("Server shutdown complete")
        else:
            logging.debug("Server is already shutdown")


    def backup_server_folder(self):
        """
        Backs up the server folder by creating a zip archive of the specified volumes.

        This method uses the `shutil.make_archive` function to create a zip 
        archive of the server folder.
        The archive is named 'server_backup.zip' and is created in the 
        same directory as the specified volumes.

        Returns:
            None
        """
        try:
            logging.info("Backing up server folder")
            shutil.make_archive('server_backup', 'zip', self.volumes)
            logging.info("Backup complete")
        except Exception as e:
            logging.error(f"Backup failed: {e}")


    def send_command(self, command):
        """
        Sends a command to the Minecraft server using RCON.

        Args:
            command (str): The command to send to the server.

        Returns:
            str: The response from the server.

        Raises:
            Exception: If the command fails to execute.

        """
        response = ''

        logging.debug(f'Sending command: {command}')
        try:
            # Replace 'your_rcon_password' and 'your_minecraft_server_ip'
            # with your actual RCON password and server IP
            with MCRcon('0.0.0.0', 'super', 25575, timeout=10) as client:
                response = client.command(command)
                logging.debug(f'Message Response: {response}')
        except Exception as e:
            logging.error(f'Command Failed {command}, {e}')
            return 'failed'

        return response

    def __check_server_online(self):
        response = self.send_command("say hi")

        while response == 'failed':
            time.sleep(6)
            response = self.send_command("say hi")

    def __await_status(self, status):
        logging.info(f'Awaiting status: {status}')
        while self.container.status != status:
            logging.debug(f'Container status: {self.container.status}, Expected: {status}')
            time.sleep(6)
            self.container.reload()

def set_up_logging(level_str, log_file_size=1):
    """
    Set up logging configuration.

    Args:
        level_str (str): The logging level as a string. Valid values are
                        'DEBUG', 'CRITICAL', 'ERROR', 'WARNING', and 'INFO'.
        log_file_size (int, optional): The maximum size of the log file in megabytes. Defaults to 1.

    Returns:
        None
    """
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
    file_handler = RotatingFileHandler(
        'server.log',
        maxBytes=1024*1024*log_file_size,
        backupCount=5)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logging.getLogger().addHandler(file_handler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Minecraft server with Docker')
    parser.add_argument('--max-ram', default='2G', help='Maximum RAM for the server')
    parser.add_argument('--port', '-p', default=25565, type=int, help='Port to run the server on')
    parser.add_argument(
        '--rcon',
        default='super',
        type=str,
        help='Password for the RCON for the server. Default leave RCON off.'
    )
    parser.add_argument('--volumes', '-v', help='List of volumes to mount to the server')
    parser.add_argument(
        '--hardcore',
        default=False,
        type=bool,
        help='Enable hardcore mode for the server. Default is false.'
    )
    parser.add_argument(
        '--difficulty',
        default=2,
        type=int,
        help='Set the difficulty for the server using ints \
        (easy 1, medium 2, hard 3). Default is normal (2).'
    )
    parser.add_argument('--version', default='latest', help='Minecraft server version')
    parser.add_argument('--name', '-n', default='minecraft-server', help='Minecraft server name')
    parser.add_argument(
        '--log-level',
        '-l',
        default=None,
        help='Set the logging level for the server'
    )
    parser.add_argument(
        '--log-file-size',
        default=2,
        type=int,
        help='Set the max size of the log file in MB'
    )

    if parser.parse_args().volumes is None:
        parser.error('Please provide a volume to mount to the server')

    set_up_logging(parser.parse_args().log_level, parser.parse_args().log_file_size)

    controller = McServerController(
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
