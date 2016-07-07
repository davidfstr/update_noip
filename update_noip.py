#!/usr/bin/env python3

import notifymail
import os.path
from selenium import webdriver
from selenium.common.exceptions import \
    WebDriverException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
import sys
import traceback

try:
    from settings import USERNAME, PASSWORD
except ImportError:
    raise ImportError(
        'You must create a "settings.py" file based on "settings.example.py" ' +
        'and fill in your no-ip username and password.')

# Useful to temporarily set to True for debugging purposes.
KEEP_BROWSER_OPEN = False

def go():
    browser = webdriver.Chrome()

    def login():
        browser.get('https://www.noip.com/login')
        
        # $('#clogs') is the login <form>
        inputs = browser.find_elements_by_css_selector('#clogs input')
        visible_inputs = [e for e in inputs if e.is_displayed()]
        (username_field, password_field) = visible_inputs
        
        login_button = browser.find_element_by_css_selector('#clogs button')
        
        username_field.click()
        username_field.send_keys(USERNAME)
        
        password_field.click()
        password_field.send_keys(PASSWORD)
        
        old_url = browser.current_url
        login_button.click()
        WebDriverWait(browser, 4).until(
            lambda _: browser.current_url != old_url)
        assert 'https://my.noip.com/' in browser.current_url

    def update_hosts():
        browser.get('https://my.noip.com/#!/dynamic-dns')
        
        def find_modify_host_buttons():
            return browser.find_elements_by_css_selector('.modify-host-ddns-table')
        
        def has_modify_host_buttons():
            return len(find_modify_host_buttons()) > 0
        
        WebDriverWait(browser, 3).until(
            lambda _: has_modify_host_buttons(),
            'Could not find any "Modify Host" buttons.')
        
        for i in range(len(find_modify_host_buttons())):
            def click_modify_host_button():
                try:
                    modify_host_button = find_modify_host_buttons()[i]  # refresh
                    modify_host_button.click()
                    return True
                except StaleElementReferenceException:
                    return False
                except WebDriverException as e:
                    if 'Element is not clickable' in str(e):
                        return False
                    else:
                        raise
            
            # NOTE: 3 seconds didn't seem to be enough time
            update_hostname_button = WebDriverWait(browser, 6).until(
                lambda _: click_modify_host_button(),
                'Could not click "Modify Host" button.')
            
            def find_update_hostname_button():
                buttons = browser.find_elements_by_css_selector('.btn-primary')
                update_hostname_buttons = [b for b in buttons if b.text == 'Update Hostname']
                if len(update_hostname_buttons) != 1:
                    return None
                (update_hostname_button,) = update_hostname_buttons
                return update_hostname_button
            
            update_hostname_button = WebDriverWait(browser, 3).until(
                lambda _: find_update_hostname_button(),
                'Could not find unique "Update Hostname" button.')
            update_hostname_button.click()
            
            # HACK: Sometimes the "Update Hostname" button
            #       fails to register the click...
            try:
                WebDriverWait(browser, 6).until(
                    lambda _: not find_update_hostname_button())
            except TimeoutException:
                # ...so try again in that situation
                find_update_hostname_button().click()
                
                WebDriverWait(browser, 6).until(
                    lambda _: not find_update_hostname_button())
    
    try:
        login()
        update_hosts()
        if KEEP_BROWSER_OPEN:
            browser.quit()
    except Exception as e:
        # Try to save screenshot of the problem
        if os.path.exists('/tmp'):
            try:
                browser.get_screenshot_as_file('/tmp/update_noip.png')
            except:
                pass  # swallow, to avoid clobbering the original exception
        
        raise e
    finally:
        if not KEEP_BROWSER_OPEN:
            browser.quit()

test = '--test' in sys.argv
try:
    go()
except Exception as e:
    if test:
        raise
    else:
        notifymail.send('[update_noip] Execution error', traceback.format_exc())
