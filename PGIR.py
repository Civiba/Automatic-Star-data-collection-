'''
    ****** Documentation ******
    -> it's an ADQL query based searching of lightcurve for PGIR catalog. THis code will fetch Ra and Dec
       values from star_list.txt and iterate till last star.
    -> The files (.hazel) will download in download directory and then moved to destination path (PGIR directory) and then
       rename the file according to the star name ( which also fetch from star_list.txt )
       star[0] --> star name/ID
       star[1] --> Ra
       star[2] --> Dec
    -> Code flow : --> chrome driver first open the link if internet is available (if not then return )
                   --> click on query interface button to write query.
                   --> Below the textarea to write query, there is one clear button which clear the textarea
                       before writing the new query. So code will first click on clear button and then click
                       inside textarea so it can write the query.
                   --> after writing query there is one checkbox with a purpose of download the light curves
                       so check that box.
                   --> After clicking on checkbox code will click on process button. Process button will check the query
                   --> If query is true then it will download the file in local system.
                   --> The downloaded file will then move to PGIR directory ( destination path ) and then rename it
                       according to star name.
                   --> After successfull first iteration, the code will move to next iteration ( next star  LNCV002 )
'''
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time
import urllib.request
import os
import shutil
import glob
import pyautogui as pag
from webdriver_manager.chrome import ChromeDriverManager

source_path = "C:/Users/CHINTAN BARODAWALA/downloads/"
destination_path = "C:/Users/CHINTAN BARODAWALA/PycharmProjects/PythonProject3/PGIR/"
LOG_FILE = 'download_PGIR.log' #store already downloaded star name
star_data_file_path = 'C:/Users/CHINTAN BARODAWALA/PycharmProjects/PythonProject3/star_list.txt'

# Ensure destination directory exists and creates if that directory not exist
if not os.path.exists(destination_path):
    os.mkdir(destination_path)


def move_pgir_lightcurve(source_path, destination_path, star_name):
    #Moves the most recent hazel file to the destination folder and renames it.
    timeout = 30  # Wait time for download to complete
    elapsed_time = 0
    while elapsed_time < timeout:
        all_hazel_files = glob.glob(os.path.join(source_path, '*.hazel'))
        if all_hazel_files:
            break
        time.sleep(1)
        elapsed_time += 1

    if not all_hazel_files:
        print("No hazel files found after waiting. Download might have failed.")
        return None

    most_recent_hazel = max(all_hazel_files, key=os.path.getmtime)
    file_extension = os.path.splitext(most_recent_hazel)[1]
    new_file_name = f"{star_name}{file_extension}" #rename
    new_file_path = os.path.join(destination_path, new_file_name)

    try:
        shutil.move(most_recent_hazel, new_file_path)
        print(f"Lightcurve moved and renamed to: {new_file_name}")
        return new_file_path
    except Exception as e:
        print(f"Error while moving the file: {e}")
        return None


def is_internet_available():
    try:
        urllib.request.urlopen('https://www.google.com', timeout=20)
        return True
    except:
        return False


if not is_internet_available():
    print("No internet connection. Please try later.")
    exit()


def load_star_data(file_path):
    """Loads star data from a file."""
    coordArr = []
    try:
        with open(file_path, 'r') as file:
            for line in file.readlines():
                parts = line.strip().split(',')
                if len(parts) == 3:
                    coordArr.append([parts[0], float(parts[1]), float(parts[2])])
    except FileNotFoundError:
        print("Error: Star list file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return coordArr


def load_downloaded_stars():
    """Loads the list of already downloaded stars to prevent duplicate downloads."""
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as file:
        return set(file.read().splitlines())


def save_downloaded_star(star_id):
    """Logs a successfully processed star to avoid reprocessing and duplication"""
    with open(LOG_FILE, "a") as file:
        file.write(f"{star_id}\n")


def process_star(chrome_driver, star):
    """Processes a single star by querying and downloading data."""
    star_id = star[0]
    downloaded_stars = load_downloaded_stars()

    if star_id in downloaded_stars:
        print(f"Data for {star_id} already downloaded. Skipping.")
        return

    # XPath Elements
    query_button = '/html/body/div[1]/section/div/div/div[2]/div/nav/ul/li[2]/a'
    query_textarea = '/html/body/form/table/tbody/tr[2]/td[2]/textarea'
    process_btn = '/html/body/form/table/tbody/tr[12]/td[1]/input'
    download_checkbox = '/html/body/form/table/tbody/tr[12]/td[2]/input'
    clear_btn_xpath = '/html/body/form/table/tbody/tr[3]/td[2]/button'
    query = f"SELECT tmcra, tmcdec FROM pgir_dr1.sources WHERE 't' = Q3C_RADIAL_QUERY(tmcra, tmcdec, {star[1]}, {star[2]}, 2)"

    try:
        # Click "Query Interface" button
        print("Clicking Query Interface button...")
        query_interface_button = WebDriverWait(chrome_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, query_button))
        )
        query_interface_button.click()
        print("Query Interface button clicked.")
        time.sleep(2)

        # Scroll to textarea
        chrome_driver.execute_script("window.scrollBy(0, 300);")

        time.sleep(1)

        # Check if button exists
        clear_buttons = chrome_driver.find_elements(By.XPATH, '//*[@id="searchForm"]/table/tbody/tr[3]/td[2]/button')

        if len(clear_buttons) > 0:  #check the clear button is there
            print("Clear button found!")
            clear_buttons[0].click()
        else:
            print("Clear button NOT found, checking if inside an iframe...")

            # Check all iframes
            iframes = chrome_driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Total iframes found: {len(iframes)}")

            for i, iframe in enumerate(iframes):
                chrome_driver.switch_to.frame(iframe)
                clear_buttons = chrome_driver.find_elements(By.XPATH, '//*[@id="searchForm"]/table/tbody/tr[3]/td[2]/button')
                if len(clear_buttons) > 0:
                    print(f"Clear button found inside iframe {i}!")
                    clear_buttons[0].click()
                    break  # Stop searching once found
                chrome_driver.switch_to.default_content()  # Switch back to main page

            if len(clear_buttons) == 0:
                print("Clear button still NOT found! Check if XPATH is correct.")

        # Locate textarea
        print("Locating textarea...")
        text_area = WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, query_textarea))
        )
        print("Textarea located.")

        # Force Click on Textarea
        print("Clicking inside textarea using JavaScript...")
        chrome_driver.execute_script("arguments[0].click();", text_area)
        time.sleep(1)

        # Ensure Textarea is Active
        print("Focusing on textarea ")
        chrome_driver.execute_script("arguments[0].focus();", text_area)
        time.sleep(1)

        # Entering query inside textarea
        print("Entering query ")
        chrome_driver.execute_script("arguments[0].value = arguments[1];", text_area, query)
        time.sleep(1)

        # **Trigger Change Event (Ensures Text is Recognized)**
        print("Triggering change event on s...")
        chrome_driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", text_area)

        print("Query entered successfully.")
        time.sleep(3)
        download_checkbox = WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.XPATH, download_checkbox)))
        download_checkbox.click()
        time.sleep(3)
        # Click the Process button
        process_button = WebDriverWait(chrome_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, process_btn)))
        process_button.click()
        time.sleep(3)

        # Wait for the download to complete
        print("Waiting for the download to complete...")
        move_pgir_lightcurve(source_path, destination_path, star_id)
        print(f"Download for {star_id} completed.")

        # Log the downloaded star
        save_downloaded_star(star_id)

    except Exception as e:
        print(f"Error: {e}")
        # Wait for the page to load
        print("Waiting for the page to load")
        time.sleep(5)

    # Reset for next query
    chrome_driver.get('https://datalab.noirlab.edu/query.php?name=pgir_dr1.sources')
    time.sleep(3)


# Set up WebDriver
service = Service(ChromeDriverManager().install())
chrome_driver = webdriver.Chrome(service=service)
chrome_driver.get("https://datalab.noirlab.edu/query.php?name=pgir_dr1.sources")

# Load star data
star_data = load_star_data(star_data_file_path)

# Process each star
for star in star_data:
    process_star(chrome_driver, star)

# Close browser
chrome_driver.quit()

