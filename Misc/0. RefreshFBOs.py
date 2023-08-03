import pandas as pd
import requests
import json

def queryFBOs():
    companyId = "c1069b00-adf0-4f00-b744-4287071e5484"
    endpoint = f"https://server1.onair.company/api/v1/company/{companyId}/fbos"

    apiKey = "8e62f5f0-b026-4301-a8d8-122a2d34bd4e"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "oa-apikey": apiKey
    }

    try:
        response = requests.get(endpoint, headers=headers)
        data = json.loads(response.text)

        print(f"API Response: {data}")

        fboList = data.get('Content', [])

        # Prepare the table headers
        headersData = [["ID", "Airport Name", "ICAO", "FBONAME"]]

        results = headersData + [[fbo['Id'], fbo['Airport']['Name'], fbo['Airport']['ICAO'], fbo['Name']] for fbo in fboList]

        print(f"Extracted Results: {results}")

        # Create a DataFrame from the results
        results_df = pd.DataFrame(results[1:], columns=results[0])

        # Write the DataFrame to a CSV file
        results_df.to_csv('FBOs.csv', index=False)
        print("Data written to the CSV")
    except Exception as error:
        print(f"API Request Error: {error}")

queryFBOs()
input("FBO's imported, press Enter to close..")
