import requests


def get_ec2_ip():
    try:
        # Step 1: Get the token
        token_url = "http://169.254.169.254/latest/api/token"
        headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
        response = requests.put(token_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        token = response.text

        # Step 2: Use the token to get the instance metadata
        metadata_url = "http://169.254.169.254/latest/meta-data/local-ipv4"
        headers = {"X-aws-ec2-metadata-token": token}
        response = requests.get(metadata_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        metadata = response.text
        return metadata
    except requests.RequestException as e:
        print(f"Error retrieving EC2 metadata: {e}")
        return None


def get_ec2_hostname():
    try:
        # Step 1: Get the token
        token_url = "http://169.254.169.254/latest/api/token"
        headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
        response = requests.put(token_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        token = response.text

        # Step 2: Use the token to get the instance hostname
        hostname_url = "http://169.254.169.254/latest/meta-data/hostname"
        headers = {"X-aws-ec2-metadata-token": token}
        response = requests.get(hostname_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        hostname = response.text
        return hostname
    except requests.RequestException as e:
        print(f"Error retrieving EC2 hostname: {e}")
        return None
