from fastapi import FastAPI
import requests

app = FastAPI()


@app.get('/home')
def get_home():
    return {"detail": "EC2 seems to Work FINE NOw"}

def get_session_token():
    url = "http://169.254.169.254/latest/api/token"
    headers = {"X-aws-ec2-metadata-token-ttl-seconds": "60"}
    response = requests.put(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print("Error getting session token:", response.status_code)
        return None

def get_metadata(token, metadata_path):
    url = f"http://169.254.169.254/latest/meta-data/{metadata_path}"
    headers = {"X-aws-ec2-metadata-token": token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error getting metadata for {metadata_path}: {response.status_code}")
        return None

@app.get('/info')
def main():
    token = get_session_token()
    if token:
        region = get_metadata(token, "placement/region")

        availability_zone = get_metadata(token, "placement/availability-zone")
        return {"Availability Zone:", availability_zone, "Region:", region}
    