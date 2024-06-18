import argparse
import bcrypt

def hash_token(token: str) -> bytes:
    """Hash a password for the first time, with a randomly-generated salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(token.encode('utf-8'), salt)
    return hashed.decode()
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start Minecraft server with Docker')
    parser.add_argument('--hash', '-t', type=str, help='List of volumes to mount to the server')
    print(hash_token(parser.parse_args().hash))
