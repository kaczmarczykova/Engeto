from enum import auto
import os
from typing import Generator
import pytest
from playwright.sync_api import Playwright, Page, APIRequestContext, expect
import random
import definitions
import datetime
import json
import time

@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright,
) -> Generator[APIRequestContext, None, None]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    request_context = playwright.request.new_context(
        base_url= definitions.BASE_API_URL, extra_http_headers=headers
    )
    yield request_context
    request_context.dispose()


def test_should_send_data(api_request_context: APIRequestContext) -> None:
    
    #casova znacka je v tomto formatu: "2024-07-12T18:40:50.3333813+02:00"
    test_timestamp = f'{datetime.datetime.now().isoformat()}'

    #Zameni vyskyty {uid}, {tempamb}, {humamb} za prislusne hodnoty
    test_humamb = str(random.randrange(10, 91))
    test_tempamb = str(random.randrange(15,41))

    #Otevre soubor pro cteni a vycte obsah do promenne data
    with open('data_v2.json', encoding='utf-8') as soubor:
        obsah = soubor.read()
        obsah = obsah.replace('**uid**', str(definitions.API_MATTRESS_ID))
        obsah = obsah.replace('**tempamb**', test_tempamb)
        obsah = obsah.replace('**humamb**', test_humamb)
        obsah = obsah.replace('**timestamp**', test_timestamp)

    new_issue = api_request_context.post(f"/api/v2/mattress", data=obsah)
    
    assert new_issue.status == 200

    time.sleep(5)

    new_issue = api_request_context.get(f"/api/v2/mattress/5")
    assert new_issue.ok

    #Test, zda odpoved obsahuje spravne EquipmentUId
    new_content = (new_issue.json()) #Vycteni textu odpovedi
    new_content_object = json.loads(new_content) #Prevod na JSON
    new_equipment_uid = new_content_object['EquipmentUId'] #Vycteni hodnoty z klice EquipmentUId

    assert new_equipment_uid == definitions.API_MATTRESS_ID

    #Test, zda odpoved obsahuje spravne Timestamp
    new_content = (new_issue.json()) #Vycteni textu odpovedi
    new_content_object = json.loads(new_content) #Prevod na JSON
    new_equipment_timestamp = new_content_object['Timestamp'] #Vycteni hodnoty z klice Timestamp

    assert new_equipment_timestamp == str(test_timestamp)

    #Test, zda odpoved obsahuje spravne TemperatureAmbientestamp
    new_content = (new_issue.json()) #Vycteni textu odpovedi
    new_content_object = json.loads(new_content) #Prevod na JSON
    new_equipment_tempamb = new_content_object['TemperatureAmbient'] #Vycteni hodnoty z klice TemperatureAmbient

    assert int(new_equipment_tempamb) == int(test_tempamb)

    #Test, zda odpoved obsahuje spravne HumidityAmbient
    new_content = (new_issue.json()) #Vycteni textu odpovedi
    new_content_object = json.loads(new_content) #Prevod na JSON
    new_equipment_humamb = new_content_object['HumidityAmbient'] #Vycteni hodnoty z klice HumidityAmbient

    assert int(new_equipment_humamb) == int(test_humamb)