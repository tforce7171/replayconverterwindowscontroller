import requests
import time
import boto3
import pprint
import os

def WindowsController(base_url, g4dn_instance_id, t2micro_instance_id):
    while True:
        time.sleep(5)
        replay_data = GetReplayData(base_url)
        if ReplayInQueue(replay_data):
            StartInstance(g4dn_instance_id)
            while True:
                time.sleep(5)
                replay_data = GetReplayData(base_url)
                if not ReplayInQueue(replay_data) and not ReplayInProcess(replay_data):
                    StopInstance(g4dn_instance_id)
                    break

def GetReplayData(base_url):
    result = requests.get(base_url+"/replay_data")
    replay_data = result.json()
    return replay_data

def ReplayInQueue(replay_data):
    replay_in_queue = False
    for data in replay_data:
        if data["conversion_status"] == "in queue":
            replay_in_queue = True
            print(f'replay in queue {replay_in_queue}')
    return replay_in_queue

def ReplayInProcess(replay_data):
    replay_in_process = False
    for data in replay_data:
        if data["conversion_status"] == "in process":
            replay_in_process = True
            print(f'replay in queue {replay_in_process}')
    return replay_in_process

def StartInstance(instance_id):
    print(f'starting instance {instance_id}')
    client = boto3.client('ec2')
    response = client.start_instances(InstanceIds=[instance_id])
    while True:
        time.sleep(5)
        state = InstanceState(instance_id)
        print(f'instance state is {state}')
        if state == "running":
            break

def StopInstance(instance_id):
    print(f'stopping instance {instance_id}')
    client = boto3.client('ec2')
    response = client.stop_instances(InstanceIds=[instance_id])
    while True:
        time.sleep(5)
        state = InstanceState(instance_id)
        print(f'instance state is {state}')
        if state == "stopped":
            break

def InstanceState(instance_id):
    instance_status = GetInstanceStatus(instance_id)
    state = instance_status["Reservations"][0]["Instances"][0]["State"]["Name"]
    return state

def GetInstanceStatus(instance_id):
    client = boto3.client('ec2')
    instance_status = client.describe_instances(InstanceIds=[instance_id])
    return instance_status

if __name__ == '__main__':
    database_url = os.environ['BASE_URL']
    g4dn_instance_id = os.environ['G4DN_INSTANCE_ID']
    WindowsController(base_url, g4dn_instance_id)
