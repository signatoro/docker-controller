from fastapi import APIRouter, FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

from deps.dependenceis import DiscordRoute


router = DiscordRoute()

@router.get("/cpu-data")
async def get_cpu_data():
    # Simulated CPU data
    data = pd.read_csv('/Users/couchcomfy/Code/personal/minecraft-server-controller/data.csv', header=None, names=['Timestamp', 'CPU Usage', 'RAM Usage', 'Net RX Bytes', 'Net TX Bytes', 'Block Read Bytes', 'Block Write Bytes'])
    data['timestamp'] = pd.to_datetime(data['Timestamp'])
    data['percentage'] = data['CPU Usage']

    cpu_data = data[['timestamp', 'percentage']].to_dict(orient='records')
    print(cpu_data)
    return cpu_data

@router.get("/ram-data")
async def get_cpu_data():
    # Simulated CPU data
    data = pd.read_csv('/Users/couchcomfy/Code/personal/minecraft-server-controller/data.csv', header=None, names=['Timestamp', 'CPU Usage', 'RAM Usage', 'Net RX Bytes', 'Net TX Bytes', 'Block Read Bytes', 'Block Write Bytes'])
    data['timestamp'] = pd.to_datetime(data['Timestamp'])
    data['percentage'] = data['RAM Usage']

    ram_data = data[['timestamp', 'percentage']].to_dict(orient='records')
    return ram_data

@router.get("/net-data")
async def get_cpu_data():
    # Simulated CPU data
    data = pd.read_csv('/Users/couchcomfy/Code/personal/minecraft-server-controller/data.csv', header=None, names=['Timestamp', 'CPU Usage', 'RAM Usage', 'Net RX Bytes', 'Net TX Bytes', 'Block Read Bytes', 'Block Write Bytes'])
    data['timestamp'] = pd.to_datetime(data['Timestamp'])
    data['read'] = data['Net RX Bytes']
    data['write'] = data['Net TX Bytes']

    net_data = data[['timestamp', 'read', 'write']].to_dict(orient='records')
    return net_data

@router.get("/block-data")
async def get_cpu_data():
    # Simulated CPU data
    data = pd.read_csv('/Users/couchcomfy/Code/personal/minecraft-server-controller/data.csv', header=None, names=['Timestamp', 'CPU Usage', 'RAM Usage', 'Net RX Bytes', 'Net TX Bytes', 'Block Read Bytes', 'Block Write Bytes'])
    data['timestamp'] = pd.to_datetime(data['Timestamp'])
    data['read'] = data['Block Read Bytes']
    data['write'] = data['Block Write Bytes']

    net_data = data[['timestamp', 'read', 'write']].to_dict(orient='records')
    return net_data
