import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
import mplcursors

def main(path):

    # Read data from CSV file
    data = pd.read_csv(path, header=None, names=['Timestamp', 'CPU Usage', 'RAM Usage', 'Net RX Bytes', 'Net TX Bytes', 'Block Read Bytes', 'Block Write Bytes'])

    
    # Convert timestamp column to datetime
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])

    # Calculate CPU and RAM usage percentages
    data['CPU Usage (%)'] = data['CPU Usage']
    data['RAM Usage (%)'] = data['RAM Usage']

    # Convert network I/O from bytes to KB
    data['Net RX KB'] = data['Net RX Bytes'] / 1024
    data['Net TX KB'] = data['Net TX Bytes'] / 1024

    # Convert block I/O from bytes to MB
    data['Block Read MB'] = data['Block Read Bytes'] / (1024 * 1024)
    data['Block Write MB'] = data['Block Write Bytes'] / (1024 * 1024)

    # Plot CPU Usage over time
    plt.plot(data['Timestamp'], data['CPU Usage (%)'], label='CPU Usage (%)')
    plt.xlabel('Timestamp')
    plt.ylabel('CPU Usage (%)')
    plt.title('CPU Usage over Time')
    plt.legend()
    plt.ylim(0, 100)
    plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
    mplcursors.cursor(hover=True).connect('add', lambda sel: sel.annotation.set_text(f'{sel.artist.get_label()}: {sel.target[1]}%'))
    plt.savefig('cpu_usage.png')
    plt.show()

    # Plot RAM Usage over time
    plt.plot(data['Timestamp'], data['RAM Usage (%)'], label='RAM Usage (%)', color='orange')
    plt.xlabel('Timestamp')
    plt.ylabel('RAM Usage (%)')
    plt.title('RAM Usage over Time')
    plt.legend()
    plt.ylim(0, 100)
    plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
    mplcursors.cursor(hover=True).connect('add', lambda sel: sel.annotation.set_text(f'{sel.artist.get_label()}: {sel.target[1]}%'))
    plt.savefig('ram_usage.png')
    plt.show()

    # Plot Network I/O over time
    plt.plot(data['Timestamp'], data['Net RX KB'], label='Net RX (KB)', color='green')
    plt.plot(data['Timestamp'], data['Net TX KB'], label='Net TX (KB)', color='blue')
    plt.xlabel('Timestamp')
    plt.ylabel('Network I/O (KB)')
    plt.title('Network I/O over Time')
    plt.legend()
    plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
    mplcursors.cursor(hover=True).connect('add', lambda sel: sel.annotation.set_text(f'{sel.artist.get_label()}: {sel.target[1]}%'))
    plt.savefig('network_io.png')
    plt.show()

    # Plot Block I/O over time
    plt.plot(data['Timestamp'], data['Block Read MB'], label='Block Read (MB)', color='red')
    plt.plot(data['Timestamp'], data['Block Write MB'], label='Block Write (MB)', color='purple')
    plt.xlabel('Timestamp')
    plt.ylabel('Block I/O (MB)')
    plt.title('Block I/O over Time')
    plt.legend()
    plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
    mplcursors.cursor(hover=True).connect('add', lambda sel: sel.annotation.set_text(f'{sel.artist.get_label()}: {sel.target[1]}%'))
    plt.savefig('block_io.png')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start Minecraft server with Docker')
    parser.add_argument('--volumes', '-v', help='List of volumes to mount to the server')
    main(parser.parse_args().volumes)