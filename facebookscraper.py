# coding=utf-8
from time import sleep

from bs4 import BeautifulSoup

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

# web driver path
driver = webdriver.Chrome('./chromedriver')
driver.maximize_window()
wait = WebDriverWait(driver, 10)
driver.get(link)
print("Opened facebook...")

# locate username field and enter username
email = driver.find_element_by_xpath("//input[@id='email' or @name='email']")
email.send_keys('d9921298@urhen.com')
print("Username entered...")

# locate password field and enter password
password = driver.find_element_by_xpath("//input[@id='pass']")
password.send_keys('test1234')
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
    # scroll to bottom
    driver.execute_script(
        "window.scrollTo(0,document.documentElement.scrollHeight);")

    # loading page waiting time
    sleep(10)

    # compare new and initial scroll height
    new_height = driver.execute_script(
        "return document.documentElement.scrollHeight")
    if new_height == initial_height:
        print("Reached the bottom of view page: ", new_height)
        break
    initial_height = new_height

# locate comment link and click to show comments
wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[@data-testid='UFI2CommentsCount/root']")))
comments_link = driver.find_element_by_xpath(
    "//a[@data-testid='UFI2CommentsCount/root']")
comments_link.click()
print(comments_link.text)

# show_comments = driver.find_elements_by_xpath(
#     "//a [@data-testid='UFI2CommentsCount/root']")
# print("comments available: ", show_comments)
# show_comments.click()


# locate comment filter dropdown then select all comments to be displayed
show_dropdown = driver.find_elements_by_xpath(
    "//a[@data-testid='UFI2ViewOptionsSelector/link']")
print("dropdown option", show_dropdown)
# showDropdown.click()


while True:
    element = driver.find_element_by_xpath(
        "//div[@class='col-sm-12']/div[@class='load-more-btn text-center']/a")
    element.click()
    time.sleep(1)

comments = driver.find_elements_by_xpath("//span [@class='_3l3x']")
print('number of comments found', str(len(comments)))

for com in comments:
    print(com.text)
