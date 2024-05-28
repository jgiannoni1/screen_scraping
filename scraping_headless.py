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
import concurrent.futures
import random

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
def init_driver(proxy=None):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/usr/bin/google-chrome"
    driver = uc.Chrome(options=options, use_subprocess=True)

    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    return driver

proxies = [
    "http://154.201.36.232:3128",
    "http://154.202.107.13:3128",
    "http://154.202.125.203:3128",
    "http://156.239.55.197:3128",
    "http://154.202.107.173:3128",
    "http://154.202.127.131:3128",
    "http://156.239.55.124:3128",
    "http://154.202.99.206:3128",
    "http://154.202.99.85:3128",
    "http://156.239.53.81:3128",
    "http://154.202.119.245:3128",
    "http://156.239.49.72:3128",
    "http://154.202.112.165:3128",
    "http://154.202.118.170:3128",
    "http://156.239.53.74:3128",
    "http://154.202.119.148:3128",
    "http://154.202.111.60:3128",
    "http://156.239.53.128:3128",
    "http://156.239.52.33:3128",
    "http://154.201.36.117:3128",
]

websites = [
    {"url": "https://alachua.realtaxdeed.com/", "county": "Alachua"},
    {"url": "https://baker.realtaxdeed.com/", "county": "Baker"},
    {"url": "https://www.baycoclerk.com/public-records/tax-deed-auctions/", "county": "Bay"},
    {"url": "https://www.citrus.realtaxdeed.com/index.cfm", "county": "Citrus"},
    {"url": "https://clay.realtaxdeed.com/", "county": "Clay"},
    {"url": "https://duval.realtaxdeed.com/", "county": "Duval"},
    {"url": "https://www.escambia.realtaxdeed.com/index.cfm?resetcfcobjs=1", "county": "Escambia"},
    {"url": "https://flagler.realtaxdeed.com/", "county": "Flagler"},
    {"url": "https://gulf.realtaxdeed.com/", "county": "Gulf"},
    {"url": "https://www.gilchrist.realtaxdeed.com/", "county": "Gilchrist"},
    {"url": "https://hendry.realtaxdeed.com/index.cfm", "county": "Hendry"},
    {"url": "https://hernando.realtaxdeed.com/index.cfm", "county": "Hernando"},
    {"url": "https://hillsborough.realtaxdeed.com/", "county": "Hillsborough"},
    {"url": "https://www.indian-river.realtaxdeed.com/", "county": "Indian River"},
    {"url": "https://jackson.realtaxdeed.com/", "county": "Jackson"},
    {"url": "https://www.lake.realtaxdeed.com/", "county": "Lake"},
    {"url": "https://www.lee.realtaxdeed.com/index.cfm", "county": "Lee"},
    {"url": "https://leon.realtaxdeed.com/index.cfm", "county": "Leon"},
    {"url": "https://marion.realtaxdeed.com/index.cfm", "county": "Marion"},
    {"url": "https://martin.realtaxdeed.com/", "county": "Martin"},
    {"url": "https://www.miamidade.realtaxdeed.com/index.cfm", "county": "Miami-Dade"},
    {"url": "https://nassau.realtaxdeed.com/", "county": "Nassau"},
    {"url": "https://okaloosa.realtaxdeed.com/", "county": "Okaloosa"},
    {"url": "https://orange.realtaxdeed.com/", "county": "Orange"},
    {"url": "https://www.osceola.realtaxdeed.com/", "county": "Osceola"},
    {"url": "https://palmbeach.realtaxdeed.com/", "county": "Palm Beach"},
    {"url": "https://pasco.realtaxdeed.com/", "county": "Pasco"},
    {"url": "https://pinellas.realtaxdeed.com/index.cfm", "county": "Pinellas"},
    {"url": "https://polk.realtaxdeed.com/", "county": "Polk"},
    {"url": "https://putnam.realtaxdeed.com/", "county": "Putnam"},
    {"url": "https://santa-rosa.realtaxdeed.com/index.cfm", "county": "Santa Rosa"},
    {"url": "https://sarasota.realtaxdeed.com/index.cfm", "county": "Sarasota"},
    {"url": "https://seminole.realtaxdeed.com/index.cfm", "county": "Seminole"},
    {"url": "https://www.volusia.realtaxdeed.com/", "county": "Volusia"},
    {"url": "https://www.washington.realtaxdeed.com/index.cfm", "county": "Washington"},
    {"url": "https://alachua.realforeclose.com/", "county": "Alachua"},
    {"url": "https://www.bay.realforeclose.com/", "county": "Bay"},
    {"url": "https://www.brevard.realforeclose.com/", "county": "Brevard"},
    {"url": "https://calhoun.realforeclose.com/", "county": "Calhoun"},
    {"url": "https://www.charlotte.realforeclose.com/index.cfm", "county": "Charlotte"},
    {"url": "https://www.citrus.realforeclose.com/index.cfm", "county": "Citrus"},
    {"url": "https://clay.realforeclose.com/", "county": "Clay"},
    {"url": "https://duval.realforeclose.com/", "county": "Duval"},
    {"url": "https://www.escambia.realforeclose.com/index.cfm?resetcfcobjs=1", "county": "Escambia"},
    {"url": "https://flagler.realforeclose.com/", "county": "Flagler"},
    {"url": "https://gulf.realforeclose.com/", "county": "Gulf"},
    {"url": "https://www.gilchrist.realforeclose.com/", "county": "Gilchrist"},
    {"url": "https://hillsborough.realforeclose.com/", "county": "Hillsborough"},
    {"url": "https://www.indian-river.realforeclose.com/", "county": "Indian River"},
    {"url": "https://jackson.realforeclose.com/", "county": "Jackson"},
    {"url": "https://www.lake.realforeclose.com/", "county": "Lake"},
    {"url": "https://www.lee.realforeclose.com/index.cfm", "county": "Lee"},
    {"url": "https://leon.realforeclose.com/", "county": "Leon"},
    {"url": "https://www.manatee.realforeclose.com/", "county": "Manatee"},
    {"url": "https://marion.realforeclose.com/index.cfm", "county": "Marion"},
    {"url": "https://martin.realforeclose.com/", "county": "Martin"},
    {"url": "https://www.miamidade.realforeclose.com/index.cfm", "county": "Miami-Dade"},
    {"url": "https://nassau.realforeclose.com/", "county": "Nassau"},
    {"url": "https://okaloosa.realforeclose.com/", "county": "Okaloosa"},
    {"url": "https://okeechobee.realforeclose.com/index.cfm", "county": "Okeechobee"},
    {"url": "https://orange.realforeclose.com/", "county": "Orange"},
    {"url": "https://www.osceola.realforeclose.com/", "county": "Osceola"},
    {"url": "https://palmbeach.realforeclose.com/", "county": "Palm Beach"},
    {"url": "https://pasco.realforeclose.com/", "county": "Pasco"},
    {"url": "https://pinellas.realforeclose.com/index.cfm", "county": "Pinellas"},
    {"url": "https://polk.realforeclose.com/", "county": "Polk"},
    {"url": "https://putnam.realforeclose.com/", "county": "Putnam"},
    {"url": "https://santa-rosa.realforeclose.com/index.cfm", "county": "Santa Rosa"},
    {"url": "https://sarasota.realforeclose.com/index.cfm", "county": "Sarasota"},
    {"url": "https://seminole.realforeclose.com/index.cfm", "county": "Seminole"},
    {"url": "https://stlucie.realforeclose.com/", "county": "St. Lucie"},
    {"url": "https://www.volusia.realforeclose.com/", "county": "Volusia"},
    {"url": "https://www.walton.realforeclose.com/", "county": "Walton"},
    {"url": "https://www.washington.realforeclose.com/index.cfm", "county": "Washington"}
]

# Gets turned into dataframe and CSV at the end
all_auction_details_global = []

def process_site(site, proxy):
    driver = init_driver(proxy)
    auction_details_list = []
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
                return auction_details_list

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
            # Continue in the current window; you can add any additional actions here
            print("No new tab opened, continuing in the current tab.")

        # Initialize variables for scrolling through calendar pages and checking if there are any links present
        threshold = 5
        first_iteration = True
        consecutive_pages_without_links = 0

        while True:
            if not first_iteration:
                # This block will be skipped during the first iteration
                # Click the button to go to the next month
                try:
                    next_month_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[starts-with(@aria-label, 'Next Month')]")))
                    next_month_button.click()
                except Exception as e:
                    print(f"Could not navigate to the next month: {e}")
                    break
            else:
                # After the first iteration, set the flag to False
                first_iteration = False

            try:
                WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@role="link"]')))
                calendar_days = driver.find_elements(By.XPATH, '//*[@role="link"]')

                if not calendar_days:
                    consecutive_pages_without_links += 1
                    print(f"No links found on this page. Pages without links so far: {consecutive_pages_without_links}")
                else:
                    consecutive_pages_without_links = 0 # Reset the counter because links were found

                if consecutive_pages_without_links >= threshold:
                    print(f"No links found on {threshold} consecutive pages. Stopping the script.")
                    break

            except TimeoutException:
                consecutive_pages_without_links += 1
                if consecutive_pages_without_links >= threshold:
                    print(f"No links found on {threshold} consecutive pages.")
                    break
            
            # Re-query calendar_days to avoid stale reference
            calendar_days = driver.find_elements(By.XPATH, '//*[@role="link"]')

            # CLicking into the links from one calendar month one at a time
            for index in range(len(calendar_days)):
                # Re-query calendar_days to avoid stale reference
                calendar_days = driver.find_elements(By.XPATH, '//*[@role="link"]')
                calendar_days[index].click()

                sleep(1)

                # Extract the total number of pages
                try:
                    html_page = driver.page_source

                    try:
                        # First, try to find the element with ID "maxWA"
                        total_pages = int(WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "maxWA"))).text)
                    except TimeoutException:
                        # If neither "maxWA" nor "maxCA" is found, handle the case (e.g., assume 1 page)
                        total_pages = 1

                    # Initialize the current page
                    current_page = 1

                    while current_page <= total_pages:
                        # Get the current page's HTML content
                        html_page = driver.page_source
                        
                        # Parse the current page's HTML
                        soup = BeautifulSoup(html_page, 'html.parser')
                        
                        # Find the <div class="Head_W">
                        head_w_div = soup.find('div', class_='Head_W')
                        
                        if head_w_div:
                            # Find all auction item containers on the page
                            auction_items = head_w_div.find_all('div', class_='AUCTION_ITEM PREVIEW')
                            
                            # List to store details of all auction items on the current page
                            all_auction_details = []
                            
                            # Extract details from each auction item container
                            for item in auction_items:
                                # Handle property addresses for both structures
                                property_address = 'N/A'
                                property_address_th = item.find('th', string='Property Address:')
                                if property_address_th:
                                    # Okeechobee structure
                                    property_address = property_address_th.find_next_sibling('td').text.strip()
                                    next_tr = property_address_th.find_parent('tr').find_next_sibling('tr')
                                    if next_tr and not next_tr.find('th'):
                                        second_part = next_tr.find('td').text.strip()
                                        property_address += ', ' + second_part
                                else:
                                    # Orange structure
                                    property_address_div = item.find('div', class_='AD_LBL', string='Property Address:')
                                    if property_address_div:
                                        property_address = property_address_div.find_next_sibling('div', class_='AD_DTA').text.strip()
                                        second_part_div = property_address_div.find_next_sibling('div', class_='AD_LBL').find_next_sibling('div', class_='AD_DTA')
                                        if second_part_div:
                                            property_address += ', ' + second_part_div.text.strip()
                                
                                # Extract Parcel ID and Parcel ID Link
                                parcel_id_th = item.find('th', string='Parcel ID:')
                                parcel_id = 'N/A'
                                parcel_id_link = 'N/A'
                                if parcel_id_th:
                                    parcel_id_td = parcel_id_th.find_next_sibling('td')
                                    parcel_id_a = parcel_id_td.find('a') if parcel_id_td else None
                                    if parcel_id_a:
                                        parcel_id = parcel_id_a.text.strip()
                                        parcel_id_link = parcel_id_a['href']
                                    else:
                                        parcel_id = parcel_id_td.text.strip() if parcel_id_td else 'N/A'
                                else:
                                    parcel_id_div = item.find('div', class_='AD_LBL', string='Parcel ID:')
                                    if parcel_id_div:
                                        parcel_id_dta_div = parcel_id_div.find_next_sibling('div', class_='AD_DTA')
                                        parcel_id_a = parcel_id_dta_div.find('a') if parcel_id_dta_div else None
                                        if parcel_id_a:
                                            parcel_id = parcel_id_a.text.strip()
                                            parcel_id_link = parcel_id_a['href']
                                        else:
                                            parcel_id = parcel_id_dta_div.text.strip() if parcel_id_dta_div else 'N/A'

                                # Extract Case # and Case # Link
                                case_th = item.find('th', string=lambda text: 'Case #' in text)
                                case_number = 'N/A'
                                case_link = 'N/A'
                                if case_th:
                                    case_td = case_th.find_next_sibling('td')
                                    case_a = case_td.find('a') if case_td else None
                                    if case_a:
                                        case_number = case_a.text.strip()
                                        case_link = case_a['href']
                                    else:
                                        case_number = case_td.text.strip() if case_td else 'N/A'
                                else:
                                    case_div = item.find('div', class_='AD_LBL', string=lambda text: 'Case #' in text)
                                    if case_div:
                                        case_dta_div = case_div.find_next_sibling('div', class_='AD_DTA')
                                        case_a = case_dta_div.find('a') if case_dta_div else None
                                        if case_a:
                                            case_number = case_a.text.strip()
                                            case_link = case_a['href']
                                        else:
                                            case_number = case_dta_div.text.strip() if case_dta_div else 'N/A'

                                # Extract Assessed Value
                                assessed_value_th = item.find('th', string='Assessed Value:')
                                assessed_value = 'N/A'
                                if assessed_value_th:
                                    assessed_value_td = assessed_value_th.find_next_sibling('td')
                                    assessed_value = assessed_value_td.text.strip() if assessed_value_td else 'N/A'
                                else:
                                    assessed_value_div = item.find('div', class_='AD_LBL', string='Assessed Value:')
                                    if assessed_value_div:
                                        assessed_value_dta_div = assessed_value_div.find_next_sibling('div', class_='AD_DTA')
                                        assessed_value = assessed_value_dta_div.text.strip() if assessed_value_dta_div else 'N/A'
                                
                                # Extract Final Judgment Amount
                                final_judgment_amount_th = item.find('th', string='Final Judgment Amount:')
                                final_judgment_amount = 'N/A'
                                if final_judgment_amount_th:
                                    final_judgment_amount_td = final_judgment_amount_th.find_next_sibling('td')
                                    final_judgment_amount = final_judgment_amount_td.text.strip() if final_judgment_amount_td else 'N/A'
                                else:
                                    final_judgment_amount_div = item.find('div', class_='AD_LBL', string='Final Judgment Amount:')
                                    if final_judgment_amount_div:
                                        final_judgment_amount_dta_div = final_judgment_amount_div.find_next_sibling('div', class_='AD_DTA')
                                        final_judgment_amount = final_judgment_amount_dta_div.text.strip() if final_judgment_amount_dta_div else 'N/A'
                                

                                auction_details = {
                                    'County': site["county"],
                                    'Property Address': property_address,
                                    'Auction Status': item.find('div', class_='ASTAT_MSGB').text if item.find('div', class_='ASTAT_MSGB') else 'N/A',
                                    'Case #': case_number,
                                    'Auction Type': item.find('th', string='Auction Type:').find_next_sibling('td').text if item.find('th', string='Auction Type:') else 'N/A',
                                    'Case # Link': case_link,
                                    'Parcel ID': parcel_id,
                                    'Parcel ID Link': parcel_id_link,
                                    'Assessed Value': item.find('th', string='Assessed Value:').find_next_sibling('td').text if item.find('th', string='Assessed Value:') else 'N/A',
                                    'Opening Bid': item.find('th', string='Opening Bid:').find_next_sibling('td').text if item.find('th', string='Opening Bid:') else 'N/A',
                                    'Final Judgment Amount': final_judgment_amount,
                                    'Certificate #': item.find('th', string='Certificate #:').find_next_sibling('td').text if item.find('th', string='Certificate #:') else 'N/A',
                                    'Tags': f"{site['county']}, {item.find('th', string='Auction Type:').find_next_sibling('td').text if item.find('th', string='Auction Type:') else 'N/A'}",
                                }
                                all_auction_details.append(auction_details)

                            auction_details_list.extend(all_auction_details)
                            
                            # After scraping, check if it's not the last page and click the "next page" button
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
                # go back to calendar page
                finally:
                    driver.back()
                    sleep(2)

    except Exception as e:
        print(f"Error loading site {site['url']}: {e}")

    driver.quit()
    return auction_details_list

def authenticate_google_sheets(json_key_path):
    credentials = service_account.Credentials.from_service_account_file(json_key_path)
    service = build('sheets', 'v4', credentials=credentials)
    return service

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

# Use concurrent futures to process sites concurrently with different proxies
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for site in websites:
        proxy = random.choice(proxies)
        futures.append(executor.submit(process_site, site, proxy))
    
    for future in concurrent.futures.as_completed(futures):
        all_auction_details_global.extend(future.result())

# Create DataFrame
df = pd.DataFrame(all_auction_details_global).drop_duplicates()

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
