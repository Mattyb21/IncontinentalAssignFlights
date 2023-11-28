import requests
import json

def test_api_request():
    companyId = "c1069b00-adf0-4f00-b744-4287071e5484"
    endpoint = f"https://server1.onair.company/api/v1/company/{companyId}/workorders"
    apiKey = "8e62f5f0-b026-4301-a8d8-122a2d34bd4e"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "oa-apikey": apiKey
    }

    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = json.loads(response.text)
        print("API Request Successful.")
        print("Data:", data)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as error:
        print(f"Other error occurred: {error}")

test_api_request()