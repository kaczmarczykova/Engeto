import pytest
import playwright.sync_api
import re
import datetime
import vitapur
import definitions

@pytest.mark.playwright
def test_1_doplnovaci_okna(page):
    
    vitapur.prihlaseni(page, definitions.TESTING_CREDS)

    page.goto(definitions.BASE_URL + '/addressbookdetail/8')
    page.wait_for_load_state("networkidle")
    page.get_by_text("testovací entita").click()

    vitapur.povolit_zmenu(page)

    ac = datetime.datetime.now()
    cas_znacka = f"{ac.year}{ac.month}{ac.day}{ac.hour}{ac.minute}{ac.second}"
    zdd = ac + datetime.timedelta(days = 365)
    termin = f"{zdd.day}.{zdd.month}.{zdd.year}"
    
    # změna osobních údajů
    page.locator("input[id='subject']").fill('testovací entita ' + cas_znacka)
    page.locator("input[id='email']").fill(cas_znacka + '@email.cz')
    page.locator("input[id='phone']").fill('+420' + cas_znacka)

    #změna nastavení rolí osoby
    page.locator("input[id='role_button']").first.click()
    page.locator("input[id='role_button']").locator("nth=1").click()
    page.locator("input[id='role_button']").locator("nth=2").click()

    #změna přihlašování    
    page.locator("input[id='AccessLimitation']").fill(termin)

    #změna IČO, DIČ atd.
    page.locator("input[id='Ico']").fill('ico_' + cas_znacka)
    page.locator("input[id='Dic']").fill('dic_' + cas_znacka)
    page.locator("div[id='Web'] input[class='form-control form-control']").fill('web_' + cas_znacka)
    page.locator("textarea[id='Note']").fill('note_' + cas_znacka)

    #uloží změny v adresáři
    page.locator("input[id='btnSaveModify']").click()
    page.locator("input[id='SaveDialogConfirmed']").click()

    #proměnné
    jmeno = page.locator("input[id='subject']").input_value()
    adresa = page.locator("input[id='email']").input_value()
    mobil = page.locator("input[id='phone']").input_value()

    ico = page.locator("input[id='Ico']").input_value()
    dic = page.locator("input[id='Dic']").input_value()
    web = page.locator("div[id='Web'] input[class='form-control form-control']").input_value()
    poznamka = page.locator("textarea[id='Note']").input_value()

    platnost = page.locator("input[id='AccessLimitation']").input_value()

    assert jmeno == ('testovací entita ' + cas_znacka)
    assert adresa == (cas_znacka + '@email.cz')
    assert mobil == ('+420' + cas_znacka)

    assert platnost == termin

    assert ico == ('ico_' + cas_znacka)
    assert dic == ('dic_' + cas_znacka)
    assert web == ('web_' + cas_znacka)
    assert poznamka == ('note_' + cas_znacka)


@pytest.mark.playwright
def test_2_zmena_parametru(page):
    vitapur.prihlaseni(page, definitions.TESTING_CREDS)

    page.goto(definitions.BASE_URL + '/addressbookdetail/8')
    page.wait_for_load_state("networkidle")
    vitapur.povolit_zmenu(page)

    #změna přihlašování
    status_element = page.get_by_text("Povolit přihlášení")
    if status_element.is_checked():
        org_status = True
        page.get_by_text("Povolit přihlášení").click()
        active_status = False
    else:
        org_status = False
        page.get_by_text("Povolit přihlášení").click()
        active_status = True
   
    tz_locator = page.locator("select[id='TimeZone']").first
    active_tz = tz_locator.input_value()
    if active_tz == "1":
        tz_locator.select_option("Central Europe Standard Time")
    else:
        tz_locator.select_option("UTC")
   
    #uloží změny v adresáři
    vitapur.ulozeni(page)

    assert org_status != active_status

    assert tz_locator.input_value() != active_tz

@pytest.mark.playwright
def test_3_povoleni_pristupu(page):
    vitapur.prihlaseni(page, definitions.TESTING_CREDS)

    page.goto(definitions.BASE_URL + '/addressbookdetail/8')
    page.wait_for_load_state("networkidle")
    vitapur.povolit_zmenu(page)

    #změna přihlašování  
    status_element = page.get_by_text("Povolit přihlášení")  
    status = status_element.is_checked()
    if status:
        status_element.uncheck()

        #uloží změny v adresáři
        vitapur.ulozeni(page)
       
    #pokusné přihlášení
    new_context = page.context.browser.new_context()
    new_page = new_context.new_page()

    vitapur.prihlaseni(new_page, definitions.ENTITY_CREDS)

    wrong_password_element = new_page.locator("div[data-bind='visible: WrongPassword()==true']")
    assert wrong_password_element.inner_text() == "Wrong password"

    #kontrola = playwright.sync_api.expect(wrong_password_element).to_have_text("Wrong password")
    #assert kontrola == False

    new_page.close()
    new_context.close()

    vitapur.odhlaseni(page)


@pytest.mark.playwright
def test_4_povoleni_pristupu(page):
    vitapur.prihlaseni(page, definitions.TESTING_CREDS)

    #povolí změnu
    page.goto(definitions.BASE_URL + '/addressbookdetail/8')
    page.wait_for_load_state("networkidle")
    vitapur.povolit_zmenu(page)

    #časová značka
    ac = datetime.datetime.now()
    cas_znacka = f"{ac.year}{ac.month}{ac.day}{ac.hour}{ac.minute}{ac.second}"
    pdd = ac + datetime.timedelta(days = -2)
    termin = f"{pdd.day}.{pdd.month}.{pdd.year}"

    #změna přihlašování    
    page.locator("input[id='AccessLimitation']").fill(termin)

    #změna přihlašování  
    status_element = page.get_by_text("Povolit přihlášení")  
    status = status_element.is_checked()
    if status == False:
        status_element.check()
    else:
        pass

    #uloží změny v adresáři
    vitapur.ulozeni(page)

    #pokusné přihlášení
    new_context = page.context.browser.new_context()
    new_page = new_context.new_page()

    vitapur.prihlaseni(new_page, definitions.ENTITY_CREDS)

    kontrola = new_page.locator("div[class='modal-header']")
    assert kontrola.is_visible() == True