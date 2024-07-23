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


def test_should_send_v1_data(api_request_context: APIRequestContext) -> None:
    
    test_timestamp = f'{datetime.datetime.now().isoformat()}'   #časová značka
    
    #Zameni vyskyty {uid}, {tempamb}, {humamb} za prislusne hodnoty
    test_tempamb = str(random.randrange(-4,58))
    test_humamb = str(random.randrange(-5, 42))

    #Otevre soubor pro cteni a vycte obsah do promenne data
    with open('data_v1.json', encoding='utf-8') as soubor:
        obsah = soubor.read()
        obsah = obsah.replace('**uid**', str(definitions.API_MATTRESS_V1_ID))
        obsah = obsah.replace('**tempamb**', test_tempamb)
        obsah = obsah.replace('**humamb**', test_humamb)
        obsah = obsah.replace('**timestamp**', test_timestamp)


    #Test, že odesílá a ukládá data
    new_data = api_request_context.post(f"/api/v1/mattress", data=obsah)

    assert new_data.ok
    
    time.sleep(5)

    #Test, že komunikuje - přijímá data
    new_data = api_request_context.get(f"/api/v1/mattress/6")
    assert new_data.ok


    #Test, zda odpoved obsahuje spravne hodnoty
    novy_obsah = new_data.json()
    novy_obsah_objekt = json.loads(novy_obsah)
    novy_obsah_objekt_uid = novy_obsah_objekt['EquipmentUId']
    novy_obsah_objekt_timestamp = novy_obsah_objekt['Timestamp']
    novy_obsah_objekt_tempamb = novy_obsah_objekt['TemperatureAmbient']
    novy_obsah_objekt__humamb = novy_obsah_objekt['HumidityAmbient']
    
    assert novy_obsah_objekt_uid == definitions.API_MATTRESS_V1_ID
    assert novy_obsah_objekt_timestamp == test_timestamp
    assert float(novy_obsah_objekt_tempamb) == float(test_tempamb)
    assert float(novy_obsah_objekt__humamb) == float(test_humamb)
