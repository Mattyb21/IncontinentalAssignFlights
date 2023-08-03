import pandas as pd
import requests
import json


def queryFBOJobs():
    fboIds_df = pd.read_csv('FBOs.csv')
    fboIds = fboIds_df['ID'].tolist()

    apiKey = "8e62f5f0-b026-4301-a8d8-122a2d34bd4e"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "oa-apikey": apiKey
    }

    headers_list = ["Mission ID", "FBOId", "DepartureAirport", "DepartureICAO", "DestinationAirport", "DestinationICAO", "Distance", "HumanOnly", "Pay", "Expiration Date", "Is Last Minute", "Descript", "PaxClass0", "PaxClass1", "PaxClass2", "Cargo"]
    results = []
    groupedResults = {}
    missions_with_humanonly_true = {}

    for fboId in fboIds:
        endpoint = "https://server1.onair.company/api/v1/fbo/" + str(fboId) + "/jobs"

        response = requests.get(endpoint, headers=headers)
        statusCode = response.status_code

        print(f"Response Status Code for FBO ID {fboId}: {statusCode}")

        if statusCode == 200:
            responseData = response.text
            if responseData:
                responseJson = json.loads(responseData)
                missions = responseJson.get('Content', [])
                
                for mission in missions:
                    flights = mission.get('Charters', []) + mission.get('Cargos', [])
                    
                    for flight in flights:
                        humanOnly = flight.get('HumanOnly', False)
                        if humanOnly:
                            missions_with_humanonly_true[mission.get("Id")] = True
                            
                    for flight in flights:
                        departureAirport = flight.get('DepartureAirport', {}).get('Name', "")
                        departureICAO = flight.get('DepartureAirport', {}).get('ICAO', "")
                        destinationAirport = flight.get('DestinationAirport', {}).get('Name', "")
                        destinationICAO = flight.get('DestinationAirport', {}).get('ICAO', "")
                        distance = flight.get('Distance', "")
                        if mission.get("Id") in missions_with_humanonly_true:
                            humanOnly = True
                        else:
                            humanOnly = flight.get('HumanOnly', False)
                        pay = mission.get('RealPay', "")
                        expirationDate = mission.get('ExpirationDate', "")
                        isLastMinute = mission.get('IsLastMinute', False)
                        descript = flight.get("Description", "")
                        if descript[-1:] == "n":
                            descript = descript[:2] + descript[-1:] if descript else ""
                        else:
                            descript = descript[:2] if descript else ""
                        paxClass = int(flight.get("MinPAXSeatConf", 0))
                        
                        paxClasses = [None, None, None]
                        if 0 <= paxClass <= 2:
                            paxClasses[paxClass] = flight.get("PassengersNumber", "")

                        key = mission.get("Id") + "_" + descript

                        if key not in groupedResults:
                            groupedResults[key] = [mission.get("Id"), fboId, departureAirport, departureICAO, destinationAirport, destinationICAO, distance, humanOnly, pay, expirationDate, isLastMinute, descript, *paxClasses]
                        else:
                            for i in range(3):
                                if paxClasses[i]:
                                    groupedResults[key][12 + i] = (groupedResults[key][12 + i] or 0) + paxClasses[i]
                        
                        row = [mission.get('Id', ""), fboId, departureAirport, departureICAO, destinationAirport, destinationICAO, distance, humanOnly, pay, expirationDate, isLastMinute, descript, *paxClasses, flight.get("Weight", 0)]
                        results.append(row)
            else:
                print(f"No response data received from the API for FBO ID {fboId}")
        else:
            print(f"Unexpected API response for FBO ID {fboId}: {statusCode}")

    results_df = pd.DataFrame(results, columns=headers_list)
    
    results_df["PaxClass0"] = pd.to_numeric(results_df["PaxClass0"], errors="coerce").fillna(0)
    results_df["PaxClass1"] = pd.to_numeric(results_df["PaxClass1"], errors="coerce").fillna(0)
    results_df["PaxClass2"] = pd.to_numeric(results_df["PaxClass2"], errors="coerce").fillna(0)
    results_df["Cargo"] = pd.to_numeric(results_df["Cargo"], errors="coerce").fillna(0)
    
    results_df.loc[results_df["Cargo"] > 0, "Cargo"] = results_df.loc[results_df["Cargo"] > 0, "Cargo"] * 0.45359237
    
    grouped_df = results_df.groupby(["Mission ID", "FBOId", "DepartureAirport", "DepartureICAO", "DestinationAirport", "DestinationICAO", "Distance", "HumanOnly", "Pay", "Expiration Date", "Is Last Minute", "Descript"]).sum().reset_index()

    grouped_df.to_csv('flights.csv', index=False)
    print("Data written to the CSV")

queryFBOJobs()
