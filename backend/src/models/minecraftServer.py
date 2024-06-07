import os
import csv
import time
import gzip
import shutil
import logging
import datetime
from typing import Any
from datetime import datetime
from logging.handlers import RotatingFileHandler



import pytz
import docker
import logging
from mcrcon import MCRcon
from docker.models.containers import Container
from docker.client import DockerClient

from schema.minecraftServerInfromation import McServerInformation

class McServer(McServerInformation):

    __container: Container = None
    __timezone: Any
    __server_running: bool
    __client: DockerClient

    def __init__(self, 
                volumes: str,
                name: str | None,
                seed: str | None,
                max_ram: str | None = '2G',
                port: int | None = 25565,
                rcon: str | None = 'super',
                hardcore: bool | None = False,
                difficulty: int | None = 3,
                version: str | None = 'latest',
                raw_timezone: str | None = 'America/New_York',
                reset_time: int | None = 3,
                take_new: bool | None = False,
                logging_level: str | None = "INFO"
        ):
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
        
        super().__init__(volumes=volumes, name=name, seed=seed, max_ram=max_ram, port=port, 
                         rcon=rcon, hardcore=hardcore, difficulty=difficulty, version=version, 
                         raw_timezone=raw_timezone, reset_time=reset_time)
        
        self.__timezone = pytz.timezone(raw_timezone)

        self.__server_running = False
        self.__client = docker.from_env()
        self.__last_logged_line = ""
        self.__logging_level = logging_level

        self.__configure_logger()

        self.start_docker_container(take_new=take_new)

        

    def __configure_logger(self):

        # Add a rotating file handler to limit the log file size
        file_handler = RotatingFileHandler(
            f'{self.name}.log',
            maxBytes=1024*1024*7,
            backupCount=5)
        file_handler.setLevel(self.__logging_level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logging.getLogger(f'{self.name}').addHandler(file_handler)
        return

    async def check(self):
        """
        Runs the server monitor.

        This method continuously monitors the server and restarts it if necessary.
        It reloads the server container every 10 seconds and checks if the time since
        the last restart is greater than or equal to 24 hours. If so, it restarts the server.

        Note: This method assumes that the `self.container` and `self.__server_running`
        attributes have been properly initialized.

        Returns:
            None
        """
        logging.getLogger(f'{self.name}').info('Starting server monitor')
        logging.getLogger(f'{self.name}').info(f'Pid 2: {os.getpid()}')

        # container_stream = self.container.logs(stream=True)
        self.__last_logged_line = ""
        
        logging.getLogger(f'{self.name}').debug('Reloading container')
        self.__container.reload()
        current_time = datetime.now(self.__timezone)

        raw_results = self.__container.stats(stream=False)

        # logs_results = self.container.logs(stream=False)
        
        csv_results = self.__generate_data_row(raw_results)

        with open('data.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_results)

        self.monitor_logs()  
        
        
        hour = current_time.strftime('%H')
        logging.getLogger(f'{self.name}').debug(f'Checking Time: {hour}, \n restart time: {hour}')
        if (int(hour) == int(self.reset_time)):
            self.restart_server()
            
            # time.sleep(5)

    def monitor_logs(self):
        """
        Monitors the server logs for new entries.

        This method continuously monitors the server logs for new entries.
        It reads the logs line by line and prints the new entries to the console.

        Returns:
            None
        """
        logging.getLogger(f'{self.name}').debug('Checking Docker Logs')
        # while self.__server_running:
        logs_results = self.__container.logs(stream=False)
        new_logs = logs_results.splitlines()[len(self.__last_logged_line.splitlines()):]

        for line in new_logs:
            logging.getLogger(f'{self.name}').info(line)

        self.__last_logged_line = logs_results

    def get_player_count(self) -> str:
        """
        Retrieves the current player count from the server.

        Returns:
            str: The player count in the format 'current_players/maximum_players'.

        Raises:
            Exception: If the server is offline.
        """
        response = self.__send_command('list')
        if response == 'failed':
            raise Exception('Server is offline')
        return f'{response.split(":")[0].strip().split(" ")[2]}/{response.split(":")[0].strip().split(" ")[7]}'
    
    def get_players_online(self) -> list[str]:
        raw_response = self.__send_command('list')
        if raw_response == 'failed':
            raise Exception('Server is offline')
        if 'There are 0' in raw_response:
            return []
        return raw_response.split(':')[1].strip().split(',')
    
    def __generate_data_row(self, container_stats) -> tuple:

        time_stamp = datetime.now(self.__timezone).strftime('%Y-%m-%d %H:%M:%S')

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

    def start_docker_container(self, take_new=False):
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
        logging.getLogger(f'{self.name}').info('Starting server')

        if self.__client.containers.list(all=True, filters={'name': self.name}):

            logging.getLogger(f'{self.name}').info(f'Container {self.name} exists')
            self.__container = self.__client.containers.get(self.name)


            self.__check_environment(take_new)


            if self.__container.status == 'exited':
                logging.getLogger(f'{self.name}').debug(f'Container {self.name} is stopped. starting...')
                self.__container.start()
                self.__check_server_online()
                self.__server_running = True

            elif self.__container.status == 'running':
                logging.getLogger(f'{self.name}').debug(f'Container {self.name} is already running')
                self.__server_running = True 

            else:
                logging.getLogger(f'{self.name}').error(f'!! Unknown Status !! Container status: {self.__container.status}')
                raise Exception(f'!! Unknown Status !! Container status: {self.__container.status}')
        else:
            logging.getLogger(f'{self.name}').info(f'Container does not exist creating {self.name}')
            self.create_docker_container()
        
    def __check_environment(self, take_new):
        logging.getLogger(f'{self.name}').debug('Checking environment variables')
        environment = self.__container.attrs['Config']['Env']
        volumes = self.__container.attrs['HostConfig']['Binds']

        if not take_new:
            if volumes != [f'{self.volumes}:/data:rw']:
                logging.getLogger(f'{self.name}').info(f'Volumes {volumes} are different than already set.')
                logging.getLogger(f'{self.name}').warning('Restart Program server with --take-new \
                                (-t) to apply new changes to the container')

            for env in environment:
                if env.startswith('EULA=') and env != 'EULA=TRUE' or \
                env.startswith('JVM_OPTS=') and env != f'JVM_OPTS=-Xms1G -Xmx{self.max_ram}' or\
                env.startswith('HARDCORE=') and env != f'HARDCORE={self.hardcore}' or \
                env.startswith('DIFFICULTY=') and env != f'DIFFICULTY={self.difficulty}' or \
                env.startswith('RCON_ENABLED=') and env != 'RCON_ENABLED=true' or \
                env.startswith('RCON_PASSWORD=') and env != f'RCON_PASSWORD={self.rcon}':
                    logging.getLogger(f'{self.name}').info(f'Environment variable {env} are different than already set.')
                    logging.getLogger(f'{self.name}').warning('Restart Program server with --take-new \
                                    (-t) to apply new changes to the container')
        else:
            logging.getLogger(f'{self.name}').info('Applying new changes to the container')

            logging.getLogger(f'{self.name}').debug(f'Current Environment: m{environment}')
            logging.getLogger(f'{self.name}').debug(f'Current Volumes: {volumes}')

            logging.getLogger(f'{self.name}').debug('New Environment:')
            for attr, value in self.__dict__.items():
                logging.getLogger(f'{self.name}').debug(f'{attr}: {value}')
            logging.getLogger(f'{self.name}').debug(f'Volumes: {self.volumes}')

            if self.__container.status == 'running':
                self.__container.stop()
                self.__await_status('exited')

            self.__container.remove()

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
        logging.getLogger(f'{self.name}').info('Starting Minecraft server with the following parameters:')
        logging.getLogger(f'{self.name}').info(f'Max RAM: {self.max_ram}')
        logging.getLogger(f'{self.name}').info(f'Port: {self.port}')
        logging.getLogger(f'{self.name}').info(f'RCON: {self.rcon}')
        logging.getLogger(f'{self.name}').info(f'Volumes: {self.volumes}')
        logging.getLogger(f'{self.name}').info(f'Hardcore: {self.hardcore}')
        logging.getLogger(f'{self.name}').info(f'Difficulty: {self.difficulty}')
        logging.getLogger(f'{self.name}').info(f'Version: {self.version}')
        logging.getLogger(f'{self.name}').info(f'Reset Time: {self.reset_time}')
        

        f_port: dict = {'25565/tcp': self.port}

        f_environment: list = [
            'EULA=TRUE',
            f'JVM_OPTS=-Xms1G -Xmx{self.max_ram}',
            f'HARDCORE={self.hardcore}',
            f'DIFFICULTY={self.difficulty}',
            f'VERSION={self.version}',
            f'TZ={self.raw_timezone}',
            f'SNOOPER_ENABLED=false',
            f'ENABLE_WHITELIST=true',
        ]

        if self.seed:
            logging.getLogger(f'{self.name}').info(f'Seed: {self.seed}')
            f_environment.append(f'SEED={self.seed}')

        f_port.update({'25575/tcp': 25575})
        f_environment.append('RCON_ENABLED=true')
        f_environment.append(f'RCON_PASSWORD={self.rcon}')

        self.__container = self.__client.containers.run(
            'itzg/minecraft-server',
            detach=True,
            name=self.name,
            ports=f_port,
            environment=f_environment,
            volumes={self.volumes:  {'bind': '/data', 'mode': 'rw'}},
        )


        self.__check_server_online()
        self.__await_status('running')

        logging.getLogger(f'{self.name}').info(f'Minecraft server started with container ID: {self.__container.id}')

        self.__server_running = True

    def restart_server(self):
        """
        Restarts the Minecraft server.

        This method shuts down the server if it is running, backs up the server folder,
        and then starts the Docker container.

        If the server is not running, an error message is logged.

        """
        logging.getLogger(f'{self.name}').info("Restarting server!")
        if self.__server_running:
            self.shutdown_server()
            time.sleep(3)
            self.backup_server_folder()
            self.__last_logged_line = ''
            time.sleep(3)
            self.start_docker_container()
        else:
            logging.getLogger(f'{self.name}').error("Server is not running")

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
        logging.getLogger(f'{self.name}').debug("Stopping server")
        if self.__server_running:

            self.__send_command("say !! The server will reset in 30 minute !!")

            time.sleep(20 * 60)

            self.__send_command("say !! The server will reset in 10 minutes !!")

            time.sleep(9 * 60)

            self.__send_command("say !! The world will reset in 45 seconds !!")

            time.sleep(40)

            self.__send_command("say !! The server will reset 5 seconds !!")

            time.sleep(5)

            self.__send_command("say !! The server is being shut down !!")
            self.__send_command("say !! It will restart in a few moments !!")

            time.sleep(3)

            logging.getLogger(f'{self.name}').info("Server shutdown beginning")

            self.__container.stop()

            self.__await_status('exited')

            self.__server_running = False
            time.sleep(4)
            logging.getLogger(f'{self.name}').info("Server shutdown complete")
        else:
            logging.getLogger(f'{self.name}').debug("Server is already shutdown")

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
            logging.getLogger(f'{self.name}').info("Backing up Server Data.")
            current_time = datetime.now(self.__timezone)
            format_date = current_time.strftime("%Y-%m-%d")

            logging.getLogger(f'{self.name}').debug("Backing up server info")
            
            shutil.make_archive( f'server_backup', 'zip', self.volumes)
            logging.getLogger(f'{self.name}').debug("Backup complete")

            logging.getLogger(f'{self.name}').debug("Compressing server statistics!")
            with open("server.log", 'rb') as file_in:
                with gzip.open(f'{format_date}_server_data') as file_out:
                    shutil.copyfileobj(file_in, file_out)

            logging.getLogger(f'{self.name}').debug("Log compression complete")

        except Exception as e:
            logging.getLogger(f'{self.name}').error(f"Backup failed: {e}")

    def whitelist_player(self, username):
        response =  self.__send_command(f"whitelist add {username}")

        if response:
            return f"Successfully Whitelisted {username}"
        else:
            return response
        
    def __send_command(self, command):
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
        logging.getLogger(f'{self.name}').debug(f'Sending command: {command}')
        try:
            # Replace 'your_rcon_password' and 'your_minecraft_server_ip'
            # with your actual RCON password and server IP
            with MCRcon('0.0.0.0', 'super', 25575, timeout=10) as client:
                response = client.command(command)
                logging.getLogger(f'{self.name}').debug(f'Message Response: {response}')
        except Exception as e:
            # logging.getLogger(f'{self.name}').error(f'Command Failed {command}, {e}')
            return 'failed'

        return response

    def __check_server_online(self):
        response = self.__send_command("say hi")

        while response == 'failed':
            time.sleep(6)
            response = self.__send_command("say hi")
        logging.getLogger(f'{self.name}').info('Server is online')

    def __await_status(self, status):
        logging.getLogger(f'{self.name}').info(f'Awaiting status: {status}')
        while self.__container.status != status:
            logging.getLogger(f'{self.name}').debug(f'Container status: {self.__container.status}, Expected: {status}')
            time.sleep(6)
            self.__container.reload()
               