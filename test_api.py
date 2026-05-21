import requests

url = "http://127.0.0.1:5000/predict"

data = {
    "MonsoonIntensity": 5,
    "TopographyDrainage": 4,
    "RiverManagement": 6,
    "Deforestation": 5,
    "Urbanization": 7,
    "ClimateChange": 6,
    "DamsQuality": 5,
    "Siltation": 4,
    "AgriculturalPractices": 5,
    "Encroachments": 6,
    "IneffectiveDisasterPreparedness": 7,
    "DrainageSystems": 5,
    "CoastalVulnerability": 4,
    "Landslides": 3,
    "Watersheds": 5,
    "DeterioratingInfrastructure": 6,
    "PopulationScore": 7,
    "WetlandLoss": 5,
    "InadequatePlanning": 6,
    "PoliticalFactors": 5
}

response = requests.post(url, json=data)
print(response.text)