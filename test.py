import argparse
import daemon
import time

def main():
    while True:
        print("Daemonized program running...")
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Daemonized Python Program')
    parser.add_argument('-d', action='store_true', help='Run the program as a daemon')

    args = parser.parse_args()

    if args.d:
        with daemon.DaemonContext():
            main()
    else:
        main()