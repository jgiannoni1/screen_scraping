from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import boto3
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Get rid of weird uc error
def suppress_exception_in_del(uc):
    old_del = uc.Chrome.__del__
    def new_del(self) -> None:
        try:
            old_del(self)
        except:
            pass
    setattr(uc.Chrome, '__del__', new_del)
suppress_exception_in_del(uc)

# Initialize driver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument('--disable-dev-shm-usage')
options.binary_location = "/usr/bin/google-chrome"
driver = uc.Chrome(options=options)

websites = [
    {"url": "https://alachua.realtaxdeed.com/", "county": "Alachua"},
    # List of similar entries to the one above
]

# Gets turned into dataframe and CSV at the end
all_auction_details_global = []

for site in websites:
    print(site["url"])
    try:
        driver.get(site["url"])
        initial_tab = driver.current_window_handle

        # Handle different types of calendar buttons
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Auction') and contains(., 'Calendar')]")))
            button = driver.find_element(By.XPATH, "//a[contains(., 'Auction') and contains(., 'Calendar')]")
            button.click()
        except (TimeoutException, NoSuchElementException):
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='splashMenuBottom']")))
                button = driver.find_element(By.XPATH, "//*[@id='splashMenuBottom']")
                button.click()
            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error finding calendar button: {e}")
                continue

        # Check if a new window/tab has been opened
        try:
            WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
            new_window_opened = True
        except TimeoutException:
            new_window_opened = False

        # Switch to the new tab if a new window/tab has been opened
        if new_window_opened:
            calANDprop_tab = next(window for window in driver.window_handles if window != initial_tab)
            driver.close()
            driver.switch_to.window(calANDprop_tab)
        else:
            print("No new tab opened, continuing in the current tab.")

        threshold = 5
        first_iteration = True
        consecutive_pages_without_links = 0

        while True:
            if not first_iteration:
                try:
                    next_month_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[starts-with(@aria-label, 'Next Month')]")))
                    next_month_button.click()
                except Exception as e:
                    print(f"Could not navigate to the next month: {e}")
                    break
            else:
                first_iteration = False

            try:
                WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@role="link"]')))
                calendar_days = driver.find_elements(By.XPATH, '//*[@role="link"]')

                if not calendar_days:
                    consecutive_pages_without_links += 1
                    print(f"No links found on this page. Pages without links so far: {consecutive_pages_without_links}")
                else:
                    consecutive_pages_without_links = 0

                if consecutive_pages_without_links >= threshold:
                    print(f"No links found on {threshold} consecutive pages. Stopping the script.")
                    break

            except TimeoutException:
                consecutive_pages_without_links += 1
                if consecutive_pages_without_links >= threshold:
                    print(f"No links found on {threshold} consecutive pages.")
                    break

            calendar_days = driver.find_elements(By.XPATH, '//*[@role="link"]')

            for index in range(len(calendar_days)):
                calendar_days = driver.find_elements(By.XPATH, '//*[@role="link"]')
                calendar_days[index].click()

                sleep(1)

                try:
                    html_page = driver.page_source

                    try:
                        total_pages = int(WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "maxWA"))).text)
                    except TimeoutException:
                        total_pages = 1

                    current_page = 1

                    while current_page <= total_pages:
                        html_page = driver.page_source
                        soup = BeautifulSoup(html_page, 'html.parser')
                        head_w_div = soup.find('div', class_='Head_W')

                        if head_w_div:
                            auction_items = head_w_div.find_all('div', class_='AUCTION_ITEM PREVIEW')
                            all_auction_details = []

                            for item in auction_items:
                                property_address_th = item.find('th', string='Property Address:')
                                property_address = 'N/A'

                                if property_address_th:
                                    property_address = property_address_th.find_next_sibling('td').text.strip()
                                    next_tr = property_address_th.find_parent('tr').find_next_sibling('tr')
                                    if next_tr and not next_tr.find('th').text.strip():
                                        second_part = next_tr.find('td').text.strip()
                                        property_address += ', ' + second_part

                                auction_details = {
                                    'County': site["county"],
                                    'Property Address': property_address,
                                    'Parcel ID': item.find('th', string='Parcel ID:').find_next_sibling('td').a.text if item.find('th', string='Parcel ID:') and item.find('th', string='Parcel ID:').find_next_sibling('td').a else 'N/A',
                                    'Auction Status': item.find('div', class_='ASTAT_MSGB').text if item.find('div', class_='ASTAT_MSGB') else 'N/A',
                                    'Auction Type': item.find('th', string='Auction Type:').find_next_sibling('td').text if item.find('th', string='Auction Type:') else 'N/A',
                                    'Case #': item.find('th', string=lambda text: 'Case #' in text).find_next_sibling('td').text if item.find('th', string=lambda text: 'Case #' in text) else 'N/A',
                                    'Parcel ID URL': item.find('th', string='Parcel ID:').find_next_sibling('td').find('a')['href'] if item.find('th', string='Parcel ID:') and item.find('th', string='Parcel ID:').find_next_sibling('td').find('a') else 'N/A',
                                    'Assessed Value': item.find('th', string='Assessed Value:').find_next_sibling('td').text if item.find('th', string='Assessed Value:') else 'N/A',
                                    'Opening Bid': item.find('th', string='Opening Bid:').find_next_sibling('td').text if item.find('th', string='Opening Bid:') else 'N/A',
                                    'Certificate #': item.find('th', string='Certificate #:').find_next_sibling('td').text if item.find('th', string='Certificate #:') else 'N/A',
                                }
                                all_auction_details.append(auction_details)

                            all_auction_details_global.extend(all_auction_details)

                            if current_page < total_pages:
                                try:
                                    next_page_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#BID_WINDOW_CONTAINER > div.Head_W > div:nth-child(3) > span.PageRight > img')))
                                    next_page_button.click()
                                except TimeoutException:
                                    print("Head_W div next_page_button not found")

                                sleep(2)
                                current_page += 1
                            else:
                                break

                        else:
                            print("Head_W div not found")

                except Exception as e:
                    print(f"Error while processing calendar day: {e}")
                finally:
                    driver.back()
                    sleep(2)

    except Exception as e:
        print(f"Error loading site {site['url']}: {e}")

driver.quit()

# Function to authenticate with Google Sheets
def authenticate_google_sheets(json_key_path):
    credentials = service_account.Credentials.from_service_account_file(json_key_path)
    service = build('sheets', 'v4', credentials=credentials)
    return service

# Function to clear all data from Google Sheets
def clear_entire_sheet(service, sheet_id):
    sheet_metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')

    requests = []
    for sheet in sheets:
        sheet_name = sheet['properties']['title']
        clear_range = f"{sheet_name}!A1:Z1000"
        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": sheet['properties']['sheetId'],
                    "startRowIndex": 0,
                    "startColumnIndex": 0
                },
                "fields": "userEnteredValue"
            }
        })

    if requests:
        body = {
            'requests': requests
        }
        response = service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
        print('All data cleared from all sheets successfully:', response)

# Function to write DataFrame to Google Sheet
def write_dataframe_to_sheet(service, sheet_id, dataframe):
    values = [dataframe.columns.values.tolist()] + dataframe.values.tolist()
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='A1',
        valueInputOption='RAW',
        body=body
    ).execute()
    print('Data uploaded to Google Sheet successfully:', result)

# Create DataFrame
df = pd.DataFrame(all_auction_details_global)

# Authenticate with Google Sheets API
json_key_path = '/home/ec2-user/screen_scraping/api_key.json'
service = authenticate_google_sheets(json_key_path)

# Google Sheet ID
sheet_id = '1ahT5hU60jAWBIeNGukj189ROdeP5EAtbCNKg_Y4mp_M'

# Clear all data from the sheet before updating
clear_entire_sheet(service, sheet_id)

# Write DataFrame to Google Sheet
write_dataframe_to_sheet(service, sheet_id, df)

# Create an in-memory file-like object for S3 upload
csv_buffer = io.BytesIO()
df.to_csv(csv_buffer, index=False)

# Initialize the S3 client
try:
    s3 = boto3.client('s3')
    bucket_name = 'blufetch'
    s3_key = 'PropertiesOutput.csv'
    csv_buffer.seek(0)
    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue())
    print('Data uploaded to S3 successfully.')
except Exception as e:
    print(f"Error uploading to S3: {e}")
