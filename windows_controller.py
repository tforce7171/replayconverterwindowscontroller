import requests
import time
import boto3
import pprint
import os

def WindowsController(database_url, g4dn_instance_id, t2micro_instance_id):
    while True:
        time.sleep(5)
        replay_data_in_queue = GetReplayData(database_url, "in queue")
        if replay_data["meta"]["count"] >= 1:
            StartInstance(g4dn_instance_id)
            while True:
                time.sleep(5)
                replay_data_in_queue = GetReplayData(database_url, "in queue")
                replay_data_in_process = GetReplayData(database_url, "in process")
                if replay_data_in_queue["meta"]["count"] == 0 and replay_data_in_process["meta"]["count"] == 0:
                    StopInstance(g4dn_instance_id)
                    break

def GetReplayData(database_url, conversion_status):
    body = {"conversion_status": conversion_status}
    result = requests.get(database_url+"api/replay_data", body)
    replay_data = result.json()
    return replay_data

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
    database_url = os.environ['DATABASE_URL']
    g4dn_instance_id = os.environ['G4DN_INSTANCE_ID']
    WindowsController(database_url, g4dn_instance_id)
