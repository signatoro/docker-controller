import time
import docker
import argparse
from mcrcon import MCRcon

def main(name, max_ram, min_ram, port, rcon, volumes, hardcore, difficulty, version):

    print(f'Starting Minecraft server with the following parameters: \n')
    print(f'Max RAM: {max_ram}')
    print(f'Min RAM: {min_ram}')
    print(f'Port: {port}')
    print(f'RCON: {rcon}') 
    print(f'Volumes: {volumes}')
    print(f'Hardcore: {hardcore}')
    print(f'Difficulty: {difficulty}')
    print(f'Version: {version}')

    client = docker.from_env()

    f_port: dict = {f'25565/tcp': port}
    f_environment: list = [
        f'EULA=TRUE',
        f'SERVER_MAX_RAM={max_ram}',
        f'SERVER_MIN_RAM={min_ram}',
        f'RCON_ENABLED={rcon}',
        f'RCON_PASSWORD=super',
        f'HARDCORE={hardcore}',
        f'DIFFICULTY={difficulty}',
    ]

    container = client.containers.run(
        'itzg/minecraft-server',
        detach=True,
        name=name,
        ports=f_port,
        environment=f_environment,
        volumes={volumes: {'bind': '/data/world', 'mode': 'rw'}},

    )

    print(f'Minecraft server started with container ID: {container.id}')

    time.sleep(60)
    # Send command to the server
    send_command('say Hello World')
    send_command('op CouchComfy')
    
    return 0

def send_command(self, command):
    response = ''
    try:
        # Replace 'your_rcon_password' and 'your_minecraft_server_ip' with your actual RCON password and server IP
        with MCRcon('0.0.0.0', 'super') as client:
            response = client.command(command)
            print(response)
    except:
        print(f'Command Failed {command}')
        return 'failed'
    
    return response






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Minecraft server with Docker')
    parser.add_argument('--max-ram', default='2G', help='Maximum RAM for the server')
    parser.add_argument('--min-ram', default='1G', help='Initial RAM for the server')
    parser.add_argument('--port', '-p', default=25565, type=int, help='Port to run the server on')
    parser.add_argument('--rcon', default=None, type=str, help='Password for the RCON for the server. Default leave RCON off.')
    parser.add_argument('--volumes', '-v', help='List of volumes to mount to the server')
    parser.add_argument('--hardcore', default=False, type=bool, help='Enable hardcore mode for the server. Default is false.')
    parser.add_argument('--difficulty', default=2, type=int, help='Set the difficulty for the server using ints (easy 1, medium 2, hard 3). Default is normal (2).')
    parser.add_argument('--version', default='latest', help='Minecraft server version')
    parser.add_argument('--name', '-n', default='minecraft-server', help='Minecraft server name')

    main(parser.parse_args().name ,parser.parse_args().max_ram, parser.parse_args().min_ram, parser.parse_args().port, parser.parse_args().rcon, parser.parse_args().volumes, parser.parse_args().hardcore, parser.parse_args().difficulty, parser.parse_args().version)