import pandas as pd
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut
import time

# Load the data
file_path = 'C:\\Users\\jgian\\web_scraping_project\\API_from_S3.csv'
df_addresses = pd.read_csv(file_path)

# Add an index column to maintain the original order
df_addresses['Index'] = df_addresses.index

# List of values to be removed
unwanted_values = ["N/A", "00 UNASSIGNED LOCATION RE", "NO STREET", 
                   "PROPERTY LOCATION IS NOT AVAIL", "0 UNKNOWN"]

# Filter out rows with unwanted values and remove duplicates
filtered_df = df_addresses[~df_addresses['Property Address'].isin(unwanted_values)].drop_duplicates(subset=['Property Address'])

# Initialize the geolocator with your API key
geolocator = GoogleV3(api_key='AIzaSyDv4Xm9fZqId8S1S7Crx7xljX33dK_1wK4')

# Function to get full address components
def get_address_components(address):
    try:
        if pd.isna(address):
            return {'Address': '', 'City': '', 'State': '', 'Zip Code': ''}
        location = geolocator.geocode(str(address) + ", Florida")
        if location:
            address_parts = location.address.split(', ')
            return {
                'Address': address_parts[0] if len(address_parts) > 0 else '',
                'City': address_parts[1] if len(address_parts) > 1 else '',
                'State': 'Florida',
                'Zip Code': address_parts[-2] if len(address_parts) > 2 else ''
            }
        else:
            return {'Address': '', 'City': '', 'State': '', 'Zip Code': ''}
    except GeocoderTimedOut:
        return {'Address': 'Timed out', 'City': 'Timed out', 'State': 'Timed out', 'Zip Code': 'Timed out'}

# Initialize new columns in filtered dataframe
filtered_df['Address'] = ''
filtered_df['City'] = ''
filtered_df['State'] = ''
filtered_df['Zip Code'] = ''

# Rate limiting settings
requests_per_second = 50
wait_time = 2 / requests_per_second

# Apply the function to the filtered dataframe
for idx, row in filtered_df.iterrows():
    address_components = get_address_components(row['Property Address'])
    filtered_df.at[idx, 'Address'] = address_components['Address']
    filtered_df.at[idx, 'City'] = address_components['City']
    filtered_df.at[idx, 'State'] = address_components['State']
    filtered_df.at[idx, 'Zip Code'] = address_components['Zip Code']
    time.sleep(wait_time)  # Wait to avoid exceeding rate limit

# Merge the results back to the original dataframe
df_addresses = df_addresses.merge(filtered_df[['Index', 'Address', 'City', 'State', 'Zip Code']], on='Index', how='left')

# Save the updated dataframe to a new CSV file
output_file_path = 'C:\\Users\\jgian\\web_scraping_project\\DF_Full_Addresses.csv'
df_addresses.to_csv(output_file_path, index=False)

print("Updated addresses saved to:", output_file_path)
