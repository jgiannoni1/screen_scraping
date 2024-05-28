from selenium import webdriver 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import TimeoutException, NoSuchElementException 
import undetected_chromedriver as uc 
from bs4 import BeautifulSoup 
from time import sleep
import pandas as pd

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
options.add_argument("start-maximized")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
driver = uc.Chrome(options=options)

# To test individual websites
'''
websites = [

]
'''
websites = [
    {"url": "https://orange.realforeclose.com/", "county": "Orange"},
]


# Gets turned into dataframe and CSV at the end 
all_auction_details_global = []

for site in websites:
    print(site["url"])
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
                            'Parcel ID': parcel_id,
                            'Parcel ID Link': parcel_id_link,
                            'Case #': case_number,
                            'Case # Link': case_link,
                            'Auction Status': item.find('div', class_='ASTAT_MSGB').text if item.find('div', class_='ASTAT_MSGB') else 'N/A',
                            'Auction Type': item.find('th', string='Auction Type:').find_next_sibling('td').text if item.find('th', string='Auction Type:') else 'N/A',
                            'Assessed Value': assessed_value,
                            'Opening Bid': item.find('th', string='Opening Bid:').find_next_sibling('td').text if item.find('th', string='Opening Bid:') else 'N/A',
                            'Certificate #': item.find('th', string='Certificate #:').find_next_sibling('td').text if item.find('th', string='Certificate #:') else 'N/A',
                            'Final Judgment Amount': final_judgment_amount,
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

df = pd.DataFrame(all_auction_details_global)

# If you want to save this DataFrame to a CSV file
df.to_csv('auction_details.csv', index=False)