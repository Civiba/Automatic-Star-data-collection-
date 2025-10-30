'''
    ******DOCUMENTATION******
    --> This is ASAS-SN sky patrol code. here we input Right ascention(Ra) and Declination and radius. and it will search
         for that star, light curve and download data in csv formate.
    --> Code flow:
                 --> Chrome driver will open the link.
                 --> the values of Ra,Dec will fetch from star_list.txt directory.
                 --> and then click on search button.
                 --> After clicking on search, there will be two possibilities 1) light curve retrieves : 0
                                                                               2) light curve retrieves : 1
                     1) if light curves retrieves : 0 then  the code will take screenshot for proof and move it to
                        desired directory with rename to "star_name_no_result_found.png"
                     2) if light curves retrieves : 1 that means we found result.
                 --> if we found result than the code will click on download button
                 --> after clicking, the website will redirect to new tab to download csv file
                 --> then code will click on CSV button to download the file
                 --> The downloaded files then move to desired directory and renamed according to star name
                 --> after each iteration the star  name will store in one log file so if we again rerun the code then it will skip
                        already downloaded star and move to unvisited star.
'''
from webdriver_manager.chrome import ChromeDriverManager

source_path = "C:/Users/CHINTAN BARODAWALA/downloads/"
destination_path = "C:/Users/CHINTAN BARODAWALA/PycharmProjects/PythonProject3/CSV_FILE/"
LOG_FILE = 'download_CSV_FILE.log'
star_data_file_path = 'C:/Users/CHINTAN BARODAWALA/PycharmProjects/PythonProject3/star_list.txt'

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

# Create destination directory if it doesn't exist
if not os.path.exists(destination_path):
    os.mkdir(destination_path)

def move_csv_file(source_path, destination_path, star_name):
    all_csv_files = glob.glob(os.path.join(source_path, '*.csv'))
    if not all_csv_files:
        print("No CSV files found in the source directory.")
        return None

    most_recent_csv = max(all_csv_files, key=os.path.getmtime)
    file_name = os.path.basename(most_recent_csv)
    file_extension = os.path.splitext(file_name)[1]
    target_file = os.path.join(destination_path, file_name)

    try:
        shutil.move(most_recent_csv, target_file)
        new_file_name = f"{star_name}{file_extension}"
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
    print("No internet connection/slow internet connection . Please try later .")
    exit()

def load_star_data(file_path): #load star_list file [star_name,Ra,Dec]
    coordArr = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    coordArr.append([parts[0], float(parts[1]), float(parts[2])])
    except FileNotFoundError:
        print("Error: File not found. wrong file path")
    except Exception as e:
        print(f"An error occurred: {e}")

    return coordArr

def load_downloaded_stars():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as file:
        return set(file.read().splitlines()) # set for unique ids only

def save_downloaded_star(star_id):
    with open(LOG_FILE, "a") as file:
        file.write(f"{star_id}\n")  # write name/id of  star which is just processed

def process_star(chrome_driver, star):
    star_id = star[0] #star name
    downloaded_stars = load_downloaded_stars()

    if star_id in downloaded_stars:
        print(f"Data for star {star_id} has already been downloaded. Skipping.")
        return

    raXpath = '/html/body/div/main/section[4]/form/div[3]/div/div/div[1]/div[1]/input'
    decXpath = '/html/body/div/main/section[4]/form/div[3]/div/div/div[1]/div[2]/input'
    radiusXpath = '/html/body/div/main/section[4]/form/div[3]/div/div/div[1]/div[3]/input'
    searchBtnXpath = '/html/body/div/main/section[4]/form/div[4]/div[2]/button[2]'
    dataXpath = '/html/body/div/main/section[5]/table/tbody/tr/td[1]/a'
    csvFileXpath = "//button[contains(text(), 'CSV')]"
    noResulFoundXpath = '/html/body/div/main/section[4]/form/div[5]/p'

    try:
        chrome_driver.find_element(By.XPATH, raXpath).clear()
        chrome_driver.find_element(By.XPATH, raXpath).send_keys(star[1]) #Ra value
        chrome_driver.find_element(By.XPATH, decXpath).clear()
        chrome_driver.find_element(By.XPATH, decXpath).send_keys(star[2]) #Dec value

        radius_field = chrome_driver.find_element(By.XPATH, radiusXpath)
        radius_field.clear()
        radius_field.send_keys('2')

        chrome_driver.find_element(By.XPATH, searchBtnXpath).click()

        try:
            # result not found
            WebDriverWait(chrome_driver, 10).until(EC.presence_of_element_located((By.XPATH, noResulFoundXpath)))
            print(f"No result found for {star_id}. Taking screenshot")
            time.sleep(2)
            ssName = f'{star_id}_no_result_found.png'
            screenshot_path = os.path.join(destination_path, ssName)  # screenshot if it contain zero result
            chrome_driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}") # move to csv file directory
            save_downloaded_star(star_id)
            return
        except:
            #result found
            print(f"Results found for {star_id}.")

            data_element = WebDriverWait(chrome_driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, dataXpath))
            )
            data_element.click()
            time.sleep(2)

            main_window = chrome_driver.current_window_handle #
            for window_handle in chrome_driver.window_handles:
                if window_handle != main_window:
                    chrome_driver.switch_to.window(window_handle)
                    break

            csv_element = WebDriverWait(chrome_driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, csvFileXpath))
            )
            chrome_driver.execute_script("arguments[0].scrollIntoView();", csv_element)
            csv_element.click()

            print("CSV button clicked successfully!")
            time.sleep(15)

            move_csv_file(source_path, destination_path, star[0])
            save_downloaded_star(star_id)

            chrome_driver.close()
            chrome_driver.switch_to.window(main_window)
            chrome_driver.get('http://asas-sn.ifa.hawaii.edu/skypatrol/')
            time.sleep(3)

    except Exception as e:
        print(f"An error occurred while processing {star_id}: {e}")
        chrome_driver.get('http://asas-sn.ifa.hawaii.edu/skypatrol/')
        time.sleep(3)

service = Service(ChromeDriverManager().install())
chrome_driver = webdriver.Chrome(service=service)
chrome_driver.get("http://asas-sn.ifa.hawaii.edu/skypatrol/")


star_data = load_star_data(star_data_file_path)
searchBtnXpath = '/html/body/div/main/section[4]/form/div[4]/div[2]/button[2]'
WebDriverWait(chrome_driver, 60).until(EC.presence_of_element_located((By.XPATH, searchBtnXpath)))

for star in star_data:
    process_star(chrome_driver, star)

chrome_driver.quit()

