import docker
import argparse
import signal
import sys

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


    def stop_container(signal, frame):
        print("Stopping Minecraft server container...")
        try:
            container = client.containers.get(name)
            container.stop()
            print("Minecraft server container stopped.")
        except docker.errors.NotFound:
            print(f"Container {name} not found.")
        sys.exit(0)

    # Register the signal handler
    signal.signal(signal.SIGINT, stop_container)

    container = client.containers.run(
        'itzg/minecraft-server',
        detach=True,
        name=name,
        ports={f'{port}/tcp': 25565},
        environment=[
            f'EULA=TRUE',
            f'SERVER_MAX_RAM={max_ram}',
            f'SERVER_MIN_RAM={min_ram}',
            f'RCON_ENABLED={rcon}',
            f'RCON_PASSWORD=super',
            f'HARDCORE={hardcore}',
            f'DIFFICULTY={difficulty}',
        ],
        volumes={volumes: {'bind': '/data/world', 'mode': 'rw'}},

    )

    print(f'Minecraft server started with container ID: {container.id}')


    return 0



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Minecraft server with Docker')
    parser.add_argument('--max-ram', default='2G', help='Maximum RAM for the server')
    parser.add_argument('--min-ram', default='1G', help='Initial RAM for the server')
    parser.add_argument('--port', '-p', default=25565, type=int, help='Port to run the server on')
    parser.add_argument('--rcon', default=False, type=bool, help='Enable RCON for the server. Default is false.')
    parser.add_argument('--volumes', '-v', help='List of volumes to mount to the server')
    parser.add_argument('--hardcore', default='false', type=bool, help='Enable hardcore mode for the server. Default is false.')
    parser.add_argument('--difficulty', default=2, type=int, help='Set the difficulty for the server using ints (easy 1, medium 2, hard 3). Default is normal (2).')
    parser.add_argument('--version', default='latest', help='Minecraft server version')
    parser.add_argument('--name', '-n', default='minecraft-server', help='Minecraft server name')

    main(parser.parse_args().name ,parser.parse_args().max_ram, parser.parse_args().min_ram, parser.parse_args().port, parser.parse_args().rcon, parser.parse_args().volumes, parser.parse_args().hardcore, parser.parse_args().difficulty, parser.parse_args().version)