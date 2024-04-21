from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/cpu-data")
async def get_cpu_data():
    # Simulated CPU data
    data = pd.read_csv('/Users/couchcomfy/Code/personal/minecraft-server-controller/data.csv', header=None, names=['Timestamp', 'CPU Usage', 'RAM Usage', 'Net RX Bytes', 'Net TX Bytes', 'Block Read Bytes', 'Block Write Bytes'])
    data['timestamp'] = pd.to_datetime(data['Timestamp'])
    data['percentage'] = data['CPU Usage']

    cpu_data = data[['timestamp', 'percentage']].to_dict(orient='records')
    print(cpu_data)
    return cpu_data

@app.get("/ram-data")
async def get_cpu_data():
    # Simulated CPU data
    data = pd.read_csv('/Users/couchcomfy/Code/personal/minecraft-server-controller/data.csv', header=None, names=['Timestamp', 'CPU Usage', 'RAM Usage', 'Net RX Bytes', 'Net TX Bytes', 'Block Read Bytes', 'Block Write Bytes'])
    data['timestamp'] = pd.to_datetime(data['Timestamp'])
    data['percentage'] = data['RAM Usage']

    ram_data = data[['timestamp', 'percentage']].to_dict(orient='records')
    return ram_data

@app.get("/net-data")
async def get_cpu_data():
    # Simulated CPU data
    data = pd.read_csv('/Users/couchcomfy/Code/personal/minecraft-server-controller/data.csv', header=None, names=['Timestamp', 'CPU Usage', 'RAM Usage', 'Net RX Bytes', 'Net TX Bytes', 'Block Read Bytes', 'Block Write Bytes'])
    data['timestamp'] = pd.to_datetime(data['Timestamp'])
    data['read'] = data['Net RX Bytes']
    data['write'] = data['Net TX Bytes']

    net_data = data[['timestamp', 'read', 'write']].to_dict(orient='records')
    return net_data

@app.get("/block-data")
async def get_cpu_data():
    # Simulated CPU data
    data = pd.read_csv('/Users/couchcomfy/Code/personal/minecraft-server-controller/data.csv', header=None, names=['Timestamp', 'CPU Usage', 'RAM Usage', 'Net RX Bytes', 'Net TX Bytes', 'Block Read Bytes', 'Block Write Bytes'])
    data['timestamp'] = pd.to_datetime(data['Timestamp'])
    data['read'] = data['Block Read Bytes']
    data['write'] = data['Block Write Bytes']

    net_data = data[['timestamp', 'read', 'write']].to_dict(orient='records')
    return net_data
