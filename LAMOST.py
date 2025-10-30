'''
    ******Documentation******
    --> This is LAMOST project where we do code search to download fits and png file of stars.
        code flow :
                  --> Chrome driver will open link
                  --> Then the code will select cone radio button.
                  --> Ra,Dec values are fetched from star_list.txt directory where star[1]-->Ra and star[2]-->Dec
                  --> Then we enter radius value ( concept of entering radius is , it creates circle of 2km radius in sky
                      and check inside that circle how many stars are there and provide data of it )
                  --> After entering the Ra,Dec and radius values, the code will press search button.
                  --> After there are two possibilities 1) alert window indicating 0 row found
                                                        2) fits and png buttons
                    1) alert window : if alert window will appear ( identified by pyautogui image matching ) then we take screenshot
                                      of window and move it to desired directory with renamed like ( star_name_no_result.png)
                    2) found result: if we found result then fits and png button will appear.
                    --> By clicking on buttons we are able to download fits and png files of stars.
                    --> So code will simultaneously download each row data.
                    --> downloaded fits and png files will moved to destination directory and renamed to (star_name_LoW_count.file_extension)
                        here low --> resolution and count --> if we found more then 1 row then it will renamed according to it like for example
                        if we found 2 rows then (LNCV001_LOW_1 and LNCV001_LOW_2...)
                    --> after each iteration the star  name will store in one log file so if we again rerun the code then it will skip
                        already downloaded star and move to unvisited star.
'''
from tornado.autoreload import start
source_path="C:/Users/CHINTAN BARODAWALA/downloads/"
destination_path="C:/Users/CHINTAN BARODAWALA/PycharmProjects/PythonProject3/fiiis_images/"
mode="LOW"
LOG_FILE = "downloaded_stars.log" # store successfully iterated star name 
def click_event(event):
    global img1
    if event.button == 3:
        print(event.xdata, event.ydata, img1[int(event.ydata), int(event.xdata), :])
        print('[' + str(int(np.round(event.xdata))) + ',' + str(int(np.round(event.ydata))) + ']',
              img1[int(event.ydata), int(event.xdata), :])

def take_snapShot():
    global img1
    time.sleep(2)
    im1 = pag.screenshot()

    # im1 = pag.screenshot(region=(1110,268,100,10))
    # plt.imshow(im1)
    # plt.show()
    # im1.save(r'F:/Codes/personal/kite_automate/add_fund_button_1.png')
    # stop

    img1 = np.array(im1)
    #     np.save()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(img1, interpolation='none')

    numrows, numcols, dim = img1.shape

    def format_coord(x, y):
        col = int(x + 0.5)
        row = int(y + 0.5)
        if col >= 0 and col < numcols and row >= 0 and row < numrows:
            z = img1[row, col, :]
            return 'x=%1.0f, y=%1.0f, z=%1.0f, %1.0f, %1.0f' % (x, y, z[0], z[1], z[2])
        else:
            return 'x=%1.0f, y=%1.0f' % (x, y)

    ax.format_coord = format_coord
    plt.connect('button_release_event', click_event)

    # if matplotlib.get_backend() == u'TkAgg':
    #     mng = plt.get_current_fig_manager()
    #     mng.window.state('zoomed')
    # elif matplotlib.get_backend() == u'GTK3Agg':
    #     manager = plt.get_current_fig_manager()
    #     manager.window.maximize()
    # else:
    #     figManager = plt.get_current_fig_manager()
    #     figManager.window.showMaximized()
    #
    # thismanager = plt.get_current_fig_manager()
    # thismanager.toolbar.zoom()

    plt.show()
    #stop


def actionElement(chrome_driver, elementLocatedBy='css', text='', action='', sendKeys='', wait=False, codeName="",
                  printLog=0, spaceStr1="", FN=""):
    try:
        if wait:
            timeout = 30
            if elementLocatedBy == 'css':
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, text))
            elif elementLocatedBy == 'xpath':
                element_present = EC.presence_of_element_located((By.XPATH, text))
            WebDriverWait(chrome_driver, timeout).until(element_present)

           #sleep(0.05)

        if elementLocatedBy == 'css':
            element = chrome_driver.find_element(By.CSS_SELECTOR, text)
        elif elementLocatedBy == 'xpath':
            element = chrome_driver.find_element(By.XPATH, text)
        elementFound = 1
    except:
        elementFound = 0
        getText = "noElementExists"

    if elementFound == 1:
        getText = ' -999999999'
        if action == 'click':
            try:
                element.click()
            except:
                chrome_driver.execute_script("arguments[0].click();", element)
        elif action == 'getText':
            getText = element.text
        elif action == 'getValue':
            getText = element.get_property('value')
        elif action == 'sendKeys':
            element.send_keys(Keys.CONTROL + "a")  # to select all existing text
            element.send_keys(Keys.DELETE)  # to delete all existing text
            element.send_keys(sendKeys)
        elif action == 'sendKeys_slow':
            element.send_keys(Keys.CONTROL + "a")  # to select all existing text
            element.send_keys(Keys.DELETE)  # to delete all existing text
            for char1 in sendKeys:
                element.send_keys(char1)
                time.sleep(0.2)
        elif action == 'click_sendKeys':
            element.click()
            element.send_keys(Keys.CONTROL + "a")  # to select all existing text
            element.send_keys(Keys.DELETE)  # to delete all existing text
            element.send_keys(sendKeys)
        elif action == 'selectIfNotSelected':
            if not (element.is_selected()):
                element.click()
        elif action == 'deselectIfSelected':
            if element.is_selected():
                element.click()
        elif action == "ifExist":
            getText = "elementExists"
        elif action == 'nothing':
            pass

    return getText
# result found
def got_result(driver):
    """Finds and downloads all FITS and PNG files, scrolling when necessary."""
    max_wait_time = 120
    start_time = time.time()
    try:
        while True:
            rows = driver.find_elements(By.XPATH, "//table/tbody/tr") # checks fits / png are appears
            time.sleep(2)
            # zero_rows_found = pag.locateOnScreen('zero_rows.png', confidence=0.7)  # checks pop up appear or not

            if not rows:

                print("No results found.")
                #noResult(chrome_driver,star[0])
                return
            for i, row in enumerate(rows, start=1):
                fits_xpath = f"//table/tbody/tr[{i}]/td[2]/div/a/img"
                png_xpath = f"//table/tbody/tr[{i}]/td[3]/div/a/img"

                # Click FITS file
                fits_file = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, fits_xpath)))
                fits_file.click()
                time.sleep(2)
                png_file = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, png_xpath)))
                png_file.click()
                time.sleep(2)

            # Scroll down to load more results (if applicable)
            last_row = rows[-1]
            driver.execute_script("arguments[0].scrollIntoView();", last_row)
            time.sleep(2)

            # Check if scrolling is finished
            new_rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
            if len(new_rows) == len(rows):  # No new rows loaded
                break

        # if time.time() - start_time > max_wait_time:
        #     print("Timeout: Results did not load within the expected time.")
        #     return

    except Exception as e:
        print(f"Error in downloading files: {e}")


# def gotResult(driver):
#     try:
#         fits_file = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[2]/div/a/img")
#         png_file = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[3]/div/a/img")
#         return fits_file, png_file
#     except:
#         return None, None
# no result found
import time
import pyautogui as pag

def noResult(chrome_driver, star_id):
    # Define screenshot name and path
    screenshot_name = f"{star_id}_no_result.png"
    screenshot_path = os.path.join(destination_path, screenshot_name)

    # Take the screenshot
    chrome_driver.save_screenshot(screenshot_path)
    print(f"Screenshot taken: {screenshot_name}")

    # Move the screenshot to fits_image dir
    fits_file_dir = destination_path
    if not os.path.exists(fits_file_dir):
        os.makedirs(fits_file_dir)

    destination_screenshot = os.path.join(fits_file_dir, screenshot_name)
    shutil.move(screenshot_path, destination_screenshot)



def sendKeysToChrome(chrome_driver, key, spaceStr1=""):
    actions = ActionChains(chrome_driver)
    actions.send_keys(key)
    actions.perform()

def sendKeysCombinationToChrome(chrome_driver, key1, key2, spaceStr1=""):
    actions = ActionChains(chrome_driver)
    actions.send_keys(key1, key2)
    actions.perform()

import re

# source_path = "C:/Users/CHINTAN BARODAWALA/downloads/"
# destination_path = "C:/Users/CHINTAN BARODAWALA/PycharmProjects/PythonProject3/fits_images/"

def downloaded_files():
    # Create destination folder if it doesn't exist
    if not os.path.exists(destination_path):
        os.mkdir(destination_path)

    # List new files to move, sorted by creation time (newest first)
    files_to_move = sorted(
        [f for f in os.listdir(source_path) if f.endswith((".gz", ".png"))],
        key=lambda f: os.path.getctime(os.path.join(source_path, f)),
        reverse=True
    )

    # Check if no new files are found
    if not files_to_move:
        print("No new files found.")
        return []

    # Move files from source to destination and keep track of moved files
    moved_files = []
    for file in files_to_move:
        src_path = os.path.join(source_path, file)
        des_path = os.path.join(destination_path, file)
        shutil.move(src_path, des_path)
        moved_files.append(file)  # Record the moved file name

    print("Files moved successfully.")
    return moved_files  # Return the list of newly moved files



# Function to rename downloaded files in the destination folder
def rename_downloaded_files(star_id, mode, moved_files):
    existing_files = os.listdir(destination_path)
    count = 101

    # Sort the files to ensure .fits and .png files are processed together
    moved_files.sort()

    # Iterate over the files in pairs (assuming each star has exactly one .fits and one .png file)
    for i in range(0, len(moved_files), 2):
        file1 = moved_files[i]
        file2 = moved_files[i + 1]

        ext1 = os.path.splitext(file1)[1]
        ext2 = os.path.splitext(file2)[1]

        new_name1 = f"{star_id}_{mode}_{count}{ext1}"
        new_name2 = f"{star_id}_{mode}_{count}{ext2}"

        des_path1 = os.path.join(destination_path, new_name1)
        des_path2 = os.path.join(destination_path, new_name2)

        while os.path.exists(des_path1) or os.path.exists(des_path2):
            print(f"Files {new_name1} or {new_name2} already exist. Skipping rename.")
            count += 1
            new_name1 = f"{star_id}_{mode}_{count}{ext1}"
            new_name2 = f"{star_id}_{mode}_{count}{ext2}"
            des_path1 = os.path.join(destination_path, new_name1)
            des_path2 = os.path.join(destination_path, new_name2)

        src_path1 = os.path.join(destination_path, file1)
        src_path2 = os.path.join(destination_path, file2)
        os.rename(src_path1, des_path1)
        os.rename(src_path2, des_path2)
        print(f"Renamed: {file1} -> {new_name1}")
        print(f"Renamed: {file2} -> {new_name2}")

        existing_files.extend([new_name1, new_name2])
        count += 1

def load_star_data(file_path):
    coordArr = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                # Strip and split each line by comma
                parts = line.strip().split(',')
                if len(parts) == 3:
                    # Append as a list [Star Name, RA, Dec]
                    coordArr.append([parts[0], float(parts[1]), float(parts[2])])
    except FileNotFoundError:
        print("Error: File not found. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return coordArr

def wait_for_download_complete(timeout=20):

    WebDriverWait(chrome_driver, timeout).until(lambda driver: len(glob.glob(f"{source_path}/*")) > 0)
    print("Download completed.")
def check_internet():
    try:
        requests.get("https://www.google.com",timeout=6)
        return True
    except requests.ConnectionError:
        return False
def load_downloaded_stars():
    if not os.path.exists(LOG_FILE):
        return set()  # Return an empty set if the log file doesn't exist
    with open(LOG_FILE, "r") as file:
        return set(file.read().splitlines())

# Function to save a new star_id to the log file
def save_downloaded_star(star_id):
    with open(LOG_FILE, "a") as file:
        file.write(f"{star_id}\n")
def process_star(chrome_driver, star, mode):
    star_id = star[0]  # Assuming star[0] is the star ID

    # Check if the star has already been processed
    downloaded_stars = load_downloaded_stars()
    if star_id in downloaded_stars:
        print(f"Data for star {star_id} has already been downloaded. Skipping.")
        return

    # Perform cone search
    coneSearchRadioButtonXpath = '/html/body/div[3]/form/div[2]/div[1]/div/table/tbody/tr[3]/td[1]/span/input'
    coneRATextboxXpath = '/html/body/div[3]/form/div[2]/div[1]/div/table/tbody/tr[3]/td[3]/input'
    coneDecTextboxXpath = '/html/body/div[3]/form/div[2]/div[1]/div/table/tbody/tr[3]/td[4]/input'
    coneRadiusTextboxXpath = '/html/body/div[3]/form/div[2]/div[1]/div/table/tbody/tr[3]/td[5]/input'

    actionElement(chrome_driver, elementLocatedBy='xpath', text=coneSearchRadioButtonXpath, action='click')
    time.sleep(1)
    actionElement(chrome_driver, elementLocatedBy='xpath', text=coneRATextboxXpath, action='sendKeys', sendKeys=str(star[1]))
    time.sleep(1)
    actionElement(chrome_driver, elementLocatedBy='xpath', text=coneDecTextboxXpath, action='sendKeys', sendKeys=str(star[2]))
    time.sleep(1)
    actionElement(chrome_driver, elementLocatedBy='xpath', text=coneRadiusTextboxXpath, action='sendKeys', sendKeys='2')
    time.sleep(1)
    sendKeysToChrome(chrome_driver, Keys.ENTER)

    # Wait for download to complete
    got_result(chrome_driver)
    wait_for_download_complete()

    # Move and rename downloaded files
    moved_files = downloaded_files()  # Get newly downloaded files
    if moved_files:
        rename_downloaded_files(star_id, mode, moved_files)
        print("Downloaded files moved and renamed successfully.")
        save_downloaded_star(star_id)  # Update the log file
    else:
        noResult(chrome_driver, star_id)
        print(f"No results found for star {star_id}.")
        save_downloaded_star(star_id)

    # Go back to the home page
    chrome_driver.get('https://www.lamost.org/dr10/v1.0/search')
    time.sleep(1)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import shutil
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import requests
import pyautogui as pag
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import glob
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException
from selenium.common.exceptions import NoSuchElementException


if not check_internet():
    print("No internet connection: Try again later.")

# Initialize Chrome driver
service = Service(ChromeDriverManager().install())
chrome_driver = webdriver.Chrome(service=service)
chrome_driver.get("https://www.lamost.org/dr10/v1.0/search")

# Load star data
coordArr = load_star_data('star_list.txt')
print(coordArr)

# Wait for the cone search radio button to be clickable
coneSearchRadioButtonXpath = '/html/body/div[3]/form/div[2]/div[1]/div/table/tbody/tr[3]/td[1]/span/input'
WebDriverWait(chrome_driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, coneSearchRadioButtonXpath)))

# Process each star

for star in coordArr:
    process_star(chrome_driver, star, mode)

# Close the browser
chrome_driver.quit()
print('a')
