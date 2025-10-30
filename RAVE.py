'''
    ******DOCUMENTATION******
    --> This is RAVE spectroscopy code which download CSV file of particular star based on Ra and Dec value.
    --> Code flow :
                  --> The chrome driver will open the link
                  --> after, it will click on cone search button
                  --> Then, it will enter value of Ra and Dec and radius of first star(LNCV001) from star_list.txt directory
                  --> after inputing the values, it click on search button.
                  --> Then one table will appear. To see full table, the code will scroll down to 300px.In table there are
                      2 field by which we can predict whether that star have downloadable file or not
                      first--> the table row is 0
                      second--> table size is 0 bytes
                      if we found these two rows in table then we will be skip that and move to next iteration
                  --> If we do not found table row 0 and table size 0 bytes then we scrolled up and then click on download
                      button
                  --> After clicking on download button 4 options appears like in which file formate we want to download.
                  --> among that 4 option, the code will choose third option ( in CSV file formate)
                  --> click on CSV file link and after that the file in csv formate will download in system
                  --> after downloading , the newly downloaded file will move and rename to desired directory.
'''

from selenium.common import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time
import urllib.request
import os
import shutil
import glob
import pyautogui as pag
from webdriver_manager.chrome import ChromeDriverManager

# File Paths
source_path = "C:/Users/CHINTAN BARODAWALA/downloads/"
destination_path = "C:/Users/CHINTAN BARODAWALA/PycharmProjects/PythonProject3/RAVE_CSV_FILE/"
LOG_FILE = 'download_CSV_RAVE_FILE.log'
star_data_file_path = 'C:/Users/CHINTAN BARODAWALA/PycharmProjects/PythonProject3/star_list.txt'
no_result = 'zero_result.png'

# XPaths
raXpath = '/html/body/div[1]/main/section/div[1]/div[2]/div[2]/div[1]/div[1]/div/input'
decXpath = '/html/body/div[1]/main/section/div[1]/div[2]/div[2]/div[1]/div[2]/div/input'
radiusXpath = '/html/body/div[1]/main/section/div[1]/div[2]/div[2]/div[1]/div[3]/div/input'
searchBtnXpath = '/html/body/div[1]/main/section/div[1]/div[2]/div[2]/button'
downloadXpath = '/html/body/div[1]/main/section/div[1]/div[2]/div[4]/ul/li[4]/a'
csvFileXpath = '/html/body/div[1]/main/section/div[1]/div[2]/div[4]/div[4]/div[1]/div[2]/div[1]/p/a'
noResulFoundXpath = '/html/body/div[1]/main/section/div[1]/div[2]/div[4]/div[1]/div[2]/div[2]/dl/div[5]/dd'
jobOverviewXpath = '/html/body/div[1]/main/section/div[1]/div[2]/div[4]/ul/li[1]/a'
coneSearchXpath = ' /html/body/div[1]/main/section/div[1]/div[1]/div/div[2]/ul/li[2]/a'
tableSizeXpath='/html/body/div[1]/main/section/div[1]/div[2]/div[4]/div[1]/div[2]/div[2]/dl/div[6]/dd'
# Create destination directory if it doesn't exist
if not os.path.exists(destination_path):
    os.mkdir(destination_path)

def move_csv_file(source_path, destination_path, star_name):
    all_csv_files = glob.glob(os.path.join(source_path, '*.csv'))
    if not all_csv_files:
        print("No CSV files found in the source directory.")
        return None

    most_recent_csv = max(all_csv_files, key=os.path.getmtime) # only store most recent  .csv file
    file_name = os.path.basename(most_recent_csv)
    file_extension = os.path.splitext(file_name)[1]
    target_file = os.path.join(destination_path, file_name)

    try:
        shutil.move(most_recent_csv, target_file)
        new_file_name = f"{star_name}_RAVE{file_extension}" #rename formate
        new_file_path = os.path.join(destination_path, new_file_name)
        os.rename(target_file, new_file_path)
        print(f"CSV file moved and renamed to: {new_file_name}")
        return new_file_path
    except Exception as e:
        print(f"An error occurred while moving the file: {e}")
        return None

def is_internet_available():
    try:
        urllib.request.urlopen('https://www.google.com', timeout=20)
        return True
    except:
        return False

if not is_internet_available():
    print("No internet connection/slow internet connection. Please try later.")
    exit()

def load_star_data(file_path):
    """Load star list file [star_name, Ra, Dec]"""
    coordArr = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    coordArr.append([parts[0], float(parts[1]), float(parts[2])])
    except FileNotFoundError:
        print("Error: File not found. Wrong file path.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return coordArr

def load_downloaded_stars():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as file:
        return set(file.read().splitlines())  # Set for unique IDs only

def save_downloaded_star(star_id):
    with open(LOG_FILE, "a") as file:
        file.write(f"{star_id}\n")  # Write name/ID of star which is just processed

def got_result_rave(star_id):
    print(f"Results found for {star_id}. Proceeding with download.")

    # Scroll Back to the Top to locate download button
    chrome_driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

    # Click on Download Button
    try:
        download_button = WebDriverWait(chrome_driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, downloadXpath))
        )
        download_button.click()
        print("Download button clicked successfully!")
        time.sleep(2)  # Wait for the download menu to appear
    except Exception as e:
        print(f"Error clicking download button: {e}")
        raise

    # Click on CSV Download Button
    try:
        csv_button = WebDriverWait(chrome_driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, csvFileXpath))
        )
        print("CSV button located. Attempting to click...")
        csv_button.click()
        print("CSV button clicked successfully!")
        time.sleep(5)  # Wait for the file to download
    except Exception as e:
        print(f"Error clicking CSV button: {e}")
        raise

    # Move downloaded file
    move_csv_file(source_path, destination_path, star_id)
    save_downloaded_star(star_id)

    # Refresh page for next iteration
    chrome_driver.get('https://www.rave-survey.org/query/')
    time.sleep(3)

def process_star(chrome_driver, star):
    star_id = star[0]  # Star name
    downloaded_stars = load_downloaded_stars()

    if star_id in downloaded_stars:
        print(f"Data for star {star_id} has already been downloaded. Skipping.")
        return

    try:
        # Click on cone search
        WebDriverWait(chrome_driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, coneSearchXpath))
        ).click()
        time.sleep(1)

        # Input values
        WebDriverWait(chrome_driver, 20).until(EC.presence_of_element_located((By.XPATH, raXpath))).clear()
        chrome_driver.find_element(By.XPATH, raXpath).send_keys(star[1])  # RA value
        WebDriverWait(chrome_driver, 20).until(EC.presence_of_element_located((By.XPATH, decXpath))).clear()
        chrome_driver.find_element(By.XPATH, decXpath).send_keys(star[2])  # Dec value

        radius_field = WebDriverWait(chrome_driver, 20).until(
            EC.presence_of_element_located((By.XPATH, radiusXpath))
        )
        radius_field.clear()
        radius_field.send_keys('2')

        # Click on search button
        WebDriverWait(chrome_driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, searchBtnXpath))
        ).click()
        time.sleep(3)

        # Scroll Down Slightly to Make the Table Visible
        chrome_driver.execute_script("window.scrollBy(0, 300);")
        print("Scrolled down to make the table visible.")
        time.sleep(2)  # Wait for scrolling to complete

        # Extract "Number of rows" and "Size of the table" from the table
        try:
            number_of_rows_text = WebDriverWait(chrome_driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/section/div[1]/div[2]/div[4]/div[1]/div[2]/div[2]/dl/div[5]"))
            ).text
            table_size_text = WebDriverWait(chrome_driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/section/div[1]/div[2]/div[4]/div[1]/div[2]/div[2]/dl/div[6]"))
            ).text

            # Extract numeric values from the text
            number_of_rows = int(''.join(filter(str.isdigit, number_of_rows_text)))  # Extract digits only
            table_size = table_size_text.split()[-1]  # Extract the last part (e.g., "8.2 kB")

            print(f"Number of rows: {number_of_rows}, Size of the table: {table_size}")

            # Check if results exist
            if number_of_rows > 0 and table_size != "0 bytes":
                print(f"Results found for {star_id}. Proceeding with download.")
                got_result_rave(star_id)
            else:
                print(f"No data available for {star_id}. Taking screenshot.")

                # Take Screenshot
                ssName = f"{star_id}_no_result_found.png"
                screenshot_path = os.path.join(destination_path, ssName)
                chrome_driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")

                save_downloaded_star(star_id)  # Save status
                chrome_driver.get('https://www.rave-survey.org/query/')
                time.sleep(3)
                return  # Skip this iteration

        except Exception as e:
            print(f"Error while extracting table data: {e}")

    except Exception as e:
        print(f"An error occurred while processing {star_id}: {e}")
        raise

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
chrome_driver = webdriver.Chrome(service=service)
chrome_driver.get("https://www.rave-survey.org/query/")

time.sleep(2)

star_data = load_star_data(star_data_file_path)
WebDriverWait(chrome_driver, 60).until(EC.presence_of_element_located((By.XPATH, coneSearchXpath)))
#iterate all stars available in star_data
for star in star_data:
    process_star(chrome_driver, star)

chrome_driver.quit()

