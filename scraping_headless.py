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

# To test individual websites
'''
websites = [

]
'''
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

for site in websites:
    driver.get(site["url"])
    initial_tab = driver.current_window_handle

    # Handle different types of calendar buttons 
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Auction') and contains(., 'Calendar')]")))
        button = driver.find_element(By.XPATH, "//a[contains(., 'Auction') and contains(., 'Calendar')]")
        button.click()
    except (TimeoutException, NoSuchElementException):
        # If the first XPath fails, try the second XPath for the new type of website
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='splashMenuBottom']")))
        button = driver.find_element(By.XPATH, "//*[@id='splashMenuBottom']")
        button.click()

    # Check if a new window/tab has been opened
    try:
        WebDriverWait(driver, 2).until(EC.number_of_windows_to_be(2))
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
                next_month_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//a[starts-with(@aria-label, 'Next Month')]")))
                next_month_button.click()
            except Exception as e:
                print(f"Could not navigate to the next month: {e}")
                break
        else:
            # After the first iteration, set the flag to False
            first_iteration = False

        # Check for absence of links and count them up or keep going if links found
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@role="link"]')))
            calendar_days = driver.find_elements(By.XPATH, '//*[@role="link"]')

            if not calendar_days:
                consecutive_pages_without_links += 1
                print(f"No links found on this page. Pages without links so far: {consecutive_pages_without_links}")
            else:
                consecutive_pages_without_links = 0  # Reset the counter because links were found

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

            html_page = driver.page_source

            # Extract the total number of pages
            try:
                # First, try to find the element with ID "maxWA"
                total_pages = int(WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.ID, "maxWA"))).text)
            except TimeoutException:
                '''
                try:
                    # If "maxWA" is not found, then try to find the element with ID "maxCA"
                    total_pages = int(WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.ID, "maxCA"))).text)
                '''
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
                        # First we handle multi-line property addresses 
                        property_address_th = item.find('th', string='Property Address:')
                        property_address = 'N/A'  # Default value
                        
                        if property_address_th:
                            # Extract the first part of the address
                            property_address = property_address_th.find_next_sibling('td').text.strip()
                            
                            # Check for and append the second part of the address if it exists
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

                    
                    # Add the current page's items to the global list
                    all_auction_details_global.extend(all_auction_details)
                    
                    # After scraping, check if it's not the last page and click the "next page" button
                    if current_page < total_pages:
                        try:
                            next_page_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#BID_WINDOW_CONTAINER > div.Head_W > div:nth-child(3) > span.PageRight > img')))
                            next_page_button.click()
                        except TimeoutException:
                            print("Head_W div next_page_button not found")

                        # Wait for the next page to load
                        sleep(2)  # Adjust sleep time as necessary
                        
                        # Increment the current page counter
                        current_page += 1
                    else:
                        # If it's the last page, exit the loop
                        break
        
                else:
                    print("Head_W div next_page_button not found")
            
            # go back to calendar page
            driver.back()

            sleep(2)
    
driver.quit()

# Create DataFrame
df = pd.DataFrame(all_auction_details_global)

# Create an in-memory file-like object
csv_buffer = io.BytesIO()

# Write DataFrame to CSV in memory
df.to_csv(csv_buffer, index=False)

# Initialize the S3 client
s3 = boto3.client('s3')

# Specify the bucket name and the file key for S3
bucket_name = 'blufetch'
s3_key = 'PropertiesOutput.csv'

# Upload the in-memory CSV to S3
s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue())