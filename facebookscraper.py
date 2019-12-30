# coding=utf-8
from time import sleep

import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
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

        # loading page waiting time _4sxd
        sleep(15)

        # compare new and initial scroll height
        new_height = driver.execute_script(
            "return document.documentElement.scrollHeight")
        if new_height == initial_height:
            print("Reached the bottom of view page: ", new_height)
            break
        initial_height = new_height
    except:
        print("cannot scroll any more")

# locate comment link and click to show comments
# wait.until(EC.element_to_be_clickable(
#     (By.XPATH, "//a[@data-testid='UFI2CommentsCount/root']")))


# click comment buttons
show_comments = driver.find_elements_by_xpath(
    "//a [@data-testid='UFI2CommentsCount/root']")
for elem in show_comments:
    driver.execute_script("arguments[0].click();", elem)
    sleep(2)

# click and select all comments as default is most relevant
all_comments = driver.find_elements_by_xpath(
    "//a [@data-testid='UFI2ViewOptionsSelector/link']")
for elem in all_comments:
    driver.execute_script("arguments[0].click();", elem)
    sleep(2)

# load more more comments/click view more comments
view_more_comments = driver.find_elements_by_xpath(
    "//a [@data-testid='UFI2CommentsPagerRenderer/pager_depth_0']")
for elem in view_more_comments:
    driver.execute_script("arguments[0].click();", elem)
    sleep(2)

comments_ul = driver.find_elements_by_class_name("_7791")

for span in comments_ul:
    parent_span = span.find_elements_by_class_name("_3l3x")
    for inner_span in parent_span:
        text_span = inner_span.find_element_by_tag_name("span").text
        print("comments", text_span)

# for com in comments:
#     print(com.text)
