import time
import docker
import argparse
import logging
from mcrcon import MCRcon

def main(name, max_ram, port, rcon, volumes, hardcore, difficulty, version):
    # Configure logging
    logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info('Starting Minecraft server with the following parameters:')
    logging.info(f'Max RAM: {max_ram}')
    logging.info(f'Port: {port}')
    logging.info(f'RCON: {rcon}') 
    logging.info(f'Volumes: {volumes}')
    logging.info(f'Hardcore: {hardcore}')
    logging.info(f'Difficulty: {difficulty}')
    logging.info(f'Version: {version}')

    client = docker.from_env()

    f_port: dict = {f'25565/tcp': port}
    
    f_environment: list = [
        f'EULA=TRUE',
        f'MEMORY={max_ram}',
        f'HARDCORE={hardcore}',
        f'DIFFICULTY={difficulty}',
    ]

    if rcon != None:
        f_port.update({f'25575/tcp': 25575})
        f_environment.append(f'RCON_ENABLED=true')
        f_environment.append(f'RCON_PASSWORD={rcon}')

    container = client.containers.run(
        'itzg/minecraft-server',
        detach=True,
        name=name,
        ports=f_port,
        environment=f_environment,
        volumes={volumes: {'bind': '/data/world', 'mode': 'rw'}},
    )

    logging.info(f'Minecraft server started with container ID: {container.id}')

    time.sleep(60)
    # Send command to the server
    logging.info("Sending command to the server")
    send_command('say Hello World')
    send_command('op CouchComfy')
    
    return 0

def send_command(command):
    response = ''
    try:
        # Replace 'your_rcon_password' and 'your_minecraft_server_ip' with your actual RCON password and server IP
        with MCRcon('0.0.0.0', 'super') as client:
            response = client.command(command)
            logging.info(response)
    except:
        logging.error(f'Command Failed {command}')
        return 'failed'
    
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Minecraft server with Docker')
    parser.add_argument('--max-ram', default='2G', help='Maximum RAM for the server')
    parser.add_argument('--port', '-p', default=25565, type=int, help='Port to run the server on')
    parser.add_argument('--rcon', default=None, type=str, help='Password for the RCON for the server. Default leave RCON off.')
    parser.add_argument('--volumes', '-v', help='List of volumes to mount to the server')
    parser.add_argument('--hardcore', default=False, type=bool, help='Enable hardcore mode for the server. Default is false.')
    parser.add_argument('--difficulty', default=2, type=int, help='Set the difficulty for the server using ints (easy 1, medium 2, hard 3). Default is normal (2).')
    parser.add_argument('--version', default='latest', help='Minecraft server version')
    parser.add_argument('--name', '-n', default='minecraft-server', help='Minecraft server name')

    if parser.parse_args().volumes == None:
        parser.error('Please provide a volume to mount to the server')

    main(parser.parse_args().name ,parser.parse_args().max_ram, parser.parse_args().port, parser.parse_args().rcon, parser.parse_args().volumes, parser.parse_args().hardcore, parser.parse_args().difficulty, parser.parse_args().version)