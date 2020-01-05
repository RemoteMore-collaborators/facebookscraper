# coding=utf-8
import os
import re
import csv
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

# link
link = 'https://www.facebook.com/login.php?login_attempt=1&lwv=110'
candy_link = 'https://www.facebook.com/CandyCrushSodaSaga/'
with open("creds.txt", 'r') as f:
    creds = f.readline()
    details = creds.split(",")
    user = details[0]
    passw = details[1]

# web driver path
driver = webdriver.Chrome('./chromedriver')
# driver = webdriver.Chrome("./chromedriver.exe")
driver.maximize_window()
wait = WebDriverWait(driver, 10)
driver.get(link)
print("Opened facebook...")

# locate username field and enter username
email = driver.find_element_by_xpath("//input[@id='email' or @name='email']")
email.send_keys(user)
print("Username entered...")

# locate password field and enter password
password = driver.find_element_by_xpath("//input[@id='pass']")
password.send_keys(passw)
print("Password entered...")

# locate login button and click to login user with valid credentials
button = driver.find_element_by_xpath("//button[@id='loginbutton']")
button.click()
print("Facebook logged in...")


# redirect to CandyCrushSodaSaga page
driver.get(candy_link)
print('Redirected to CandyCrushSodaSaga page')

# Calculate page height
initial_height = driver.execute_script(
    "return document.documentElement.scrollHeight")
print("Initial page height: ", initial_height)

while True:
    try:
        # scroll to bottom
        driver.execute_script(
            "window.scrollTo(0,document.documentElement.scrollHeight);")

        # loading page waiting time
        sleep(5)

        # compare new and initial scroll height
        new_height = driver.execute_script(
            "return document.documentElement.scrollHeight")
        if new_height == initial_height:
            print("Reached the bottom of view page: ", new_height)
            break
        initial_height = new_height
    except:
        print("cannot scroll any more")

# locate all posts available with comments
all_posts = driver.find_elements_by_xpath(
    "//a[@data-testid='UFI2ViewOptionsSelector/link']")
total_number_of_posts = len(all_posts)
print("Total number of posts: ", total_number_of_posts)

# select all comments from dropdown menu
for post in range(total_number_of_posts):
    actions = ActionChains(driver)
    element = all_posts[post]
    driver.implicitly_wait(5)
    actions.move_to_element(element).click().perform()
    driver.execute_script("scrollBy(0,500);")
    try:
        driver.implicitly_wait(2)
        
    except StaleElementReferenceException:
        pass
    sleep(2)


# load more more comments/click view more comments
view_more_comments = driver.find_elements_by_xpath(
    "//a [@data-testid='UFI2CommentsPagerRenderer/pager_depth_0']")
for elements in view_more_comments:
    driver.execute_script("arguments[0].click();", elements)
    sleep(2)


current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
csv_path = f"./csv/facebook_{current_time}.csv"
fp = open(csv_path, "w")
wr = csv.writer(fp, dialect='excel')
wr.writerow(['from_user', 'Comments', 'Time', 'Reactions'])

while True:
    sleep(5)
    comments_ul = driver.find_element_by_xpath(
        '//*[@id="u_1k_51"]/div/div[3]/ul')
    try:

        for single_comment in comments_ul:
            data = []
            from_user = single_comment.find_element_by_xpath(
                '//*[@id="u_1j_7t"]/div/div[3]/ul/li[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/div[1]/div/div/div/a').text
            print('from_user', from_user)
            data.append(from_user)

            comment = single_comment.find_element_by_xpath(
                '//*[@id="u_1j_7t"]/div/div[3]/ul/li[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/div[1]/div/div/div/span/span/span').text
            data.append(comment)

            comment_time = single_comment.find_element_by_xpath(
                '//*[@id="js_2mk"]').get_attribute('datetime')
            data.append(comment_time)

            reactions = single_comment.find_element_by_xpath(
                '//*[@id="js_yj"]/a/span[2]').text
            data.append(reactions)

            print('data', data)

            wr = csv.writer(fp, dialect='excel')
            wr.writerow(data)

    except NoSuchElementException:
        print(csv_path, " writing complete!")
        fp.close()
        driver.quit()
        break
