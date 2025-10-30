# Automatic-Star-data-collection-
By using selenium and pyautogui, the star data were being downloaded from various websites as required parameters.

Project flow: 
First if we click on run button, the selenium webdriver will open perticular URL as mentioned and then by using XPATHs of elements, it automatically input the data fetch from external file, and then get result and then download it in local system. 
The next part is to relocate and rename the downloaded file from download folder to particular directory. This is done by Shutil and OS library.

In this project, i have automate 4 websites 
1. LAMOST
2. RAVE spectroscopy
3. PGIR
4. ASSASN 
