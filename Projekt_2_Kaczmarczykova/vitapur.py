import pytest
import playwright.sync_api
import re
import datetime
import definitions

def prihlaseni(page, creds):
    page.goto(definitions.BASE_URL)
    page.locator("input[id='username']").fill(creds[0])
    page.locator("input[id='password']").fill(creds[1])
    page.locator("form[id='login-form'] > input[class*='btn']").click()
    page.wait_for_load_state("networkidle")


def ulozeni(page):
    #uloží změny v adresáři
    page.locator("input[id='btnSaveModify']").click()
    page.locator("input[id='SaveDialogConfirmed']").click()


def povolit_zmenu(page):
    page.get_by_text("Povolit změnu").first.click()


def odhlaseni(page):
    page.locator("a[id='languages']").click()
    page.get_by_text("Odhlášení").first.click()
    page.wait_for_load_state("networkidle")


def zmena_hesla(page, old_password, new_password):
    page.locator("input[id='ChangePassword']").click()
    page.locator("input[id='OldPassword']").fill(old_password)
    page.locator("input[id='NewPassword']").fill(new_password)
    page.locator("input[data-bind='dotvvm-textbox-text: NewPasswordRepeat']").fill(new_password)
    page.locator("input[id='PasswordDialogConfirmed']").click()
    page.locator("div[class='modal fade show'] input[class='btn btn-sm btn-secondary']").click()