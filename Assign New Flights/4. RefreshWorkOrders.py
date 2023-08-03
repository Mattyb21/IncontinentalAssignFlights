import pandas as pd
import requests
import json

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
    data = json.loads(response.text)

    work_order_list = data.get('Content', [])

    # Prepare the table headers
    headersData = [["Aircraft", "HoursBefore100", "WorkOrderName"]]

    results = headersData + [[wo['Aircraft']['HoursBefore100HInspection'], wo['Aircraft']['Identifier'], wo['Name']] for wo in work_order_list]

    print(f"Extracted Results: {results}")

    # Create a DataFrame from the results
    results_df = pd.DataFrame(results[1:], columns=results[0])

    # Write the DataFrame to a CSV file
    results_df.to_csv('Workorders.csv', index=False)


except Exception as error:
    print(f"API Request Error: {error}")
