import csv
import time

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

# from utils import custom_logger, paste_csv_to_wks
start_time = datetime.now()
CURRENT_DIR = '/home/ubuntu/facebookscraper'
WINDOW_SIZE = "1024,2080"
URL = 'https://www.facebook.com/CandyCrushSodaSaga/posts'
SCROLL_PAUSE_TIME = 5
NUMBER_OF_POSTS = 5

current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
filename = f'{CURRENT_DIR}/logs/scraped_{current_time}.log'

# logger = custom_logger(filename)

# logger.info(f'Logfile name {filename}')

# Chrome browser options - Version 79.0.3945.88 (Official Build) (64-bit)
chrome_options = Options()

# chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--mute-audio")
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)

print("Opening page..")
driver.get(URL)

try:
    print("Waiting for page to load...")
    el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "u_0_ek")))
except TimeoutException as err:
    print("something went wrong")
    el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "u_0_ek")))

print("Page loaded, beginning sleep.")
time.sleep(5)
print("End of sleep")

see_more = driver.find_elements_by_xpath('//*[@id="www_pages_reaction_see_more_unitwww_pages_posts"]/div/a')
actions = ActionChains(driver)
actions.move_to_element(see_more[0]).perform()
time.sleep(5)

not_now = driver.find_element_by_xpath('//*[@id="expanding_cta_close_button"]')
not_now.click()

time.sleep(1)

# footer_notification = driver.find_element_by_xpath('//*[@id="u_0_el"]')
driver.execute_script("document.getElementById('u_0_ek').style.display = 'none';")
driver.execute_script("document.getElementById('u_0_ej').style.height = '0';")
driver.execute_script("document.querySelector('#content>div>div>div._1qkq._1ql0>div._1pfm').style.height = '0';")
driver.execute_script("document.querySelector('#content>div>div>div._1qkq._1ql0>div._1pfm').style.display = 'none';")
# selenium.common.exceptions.ElementClickInterceptedException
page = 1

print(f"Currently at page {page}")

# TODO Finish scrolling for 2 pages
while True:
    try:
        see_more = driver.find_elements_by_xpath('//*[@id="www_pages_reaction_see_more_unitwww_pages_posts"]/div/a')
        ActionChains(driver).move_to_element(see_more[0]).perform()
        time.sleep(5)
    except JavascriptException:
        print("Caught the JavascriptException exception! Sleeping")
        time.sleep(2)
        print("Resuming...")
    except StaleElementReferenceException:
        print("Caught the StaleElementReferenceException exception! Sleeping")
        time.sleep(2)
        print("Resuming...")
    except NoSuchElementException:
        print("Reached the bottom of the page")
        break

    all_posts_count = len(driver.find_elements_by_xpath("//a[@data-testid='UFI2ViewOptionsSelector/link']"))
    if all_posts_count >= NUMBER_OF_POSTS:
        break

    page += 1
    print(f"Moving to page {page}")

# TODO Open the comments section by selecting all_comments option

all_posts = driver.find_elements_by_xpath("//a[@data-testid='UFI2ViewOptionsSelector/link']")

total_number_of_posts = len(all_posts)
print("Total number of posts: ", total_number_of_posts)
all_posts_to_be_parsed = None

if total_number_of_posts > NUMBER_OF_POSTS:
    all_posts_to_be_parsed = all_posts[:NUMBER_OF_POSTS]
else:
    all_posts_to_be_parsed = all_posts

print("Total number of posts to be parsed: ", len(all_posts_to_be_parsed))
for (index, post) in enumerate(all_posts_to_be_parsed):
    print(f"Clicking on post {index + 1}")
    ActionChains(driver).move_to_element(post).perform()
    driver.execute_script("scrollBy(0,500);")
    post.click()
    driver.find_element_by_xpath('//div[@data-testid="UFI2ViewOptionsSelector/menuRoot"]/div/ul/li[last()]').click()
    time.sleep(5)

all_comment_blocks = driver.find_elements_by_xpath("//div[@data-testid='UFI2CommentsList/root_depth_0']")
total_number_of_comment_blocks = len(all_comment_blocks)
print(f"Number of comment blocks {total_number_of_comment_blocks}")

comment_block = None
if total_number_of_posts > NUMBER_OF_POSTS:
    comment_block = all_comment_blocks[:NUMBER_OF_POSTS]

print(f"Total comment blocks to be parsed {len(comment_block)}")

all_more_comments = []

# # import pdb
# # pdb.set_trace()
facebook_c = driver.find_element_by_xpath('//div[@aria-label="Facebook"]/div/following-sibling::*')
# # facebook_c =
for (i, block) in enumerate(comment_block):
    print(f"Clicking on comment block {i + 1}")
    while True:
        try:
            ActionChains(driver).move_to_element(block).perform()
            more_comments = block.find_elements_by_css_selector('[class^="_4swz _7a93"]')

            if not more_comments:
                print(f" No more comments on comment block {i + 1}")
                break

            more_comments_link = more_comments[0]
            ActionChains(driver).move_to_element(more_comments_link).perform()
            driver.execute_script("scrollBy(0,500);")
            more_comments_link.click()
            time.sleep(3)
        except NoSuchElementException as err:
            print("Clicked all more comments")
            break

for (i, block) in enumerate(comment_block):
    print(f"Clicking on replies on comment block {i + 1}")
    while True:
        try:
            ActionChains(driver).move_to_element(block).perform()
            replies = block.find_elements_by_css_selector('[class^="_4sso _4ssp"]')
            loading_replies = block.find_elements_by_css_selector('[class^="_4sxg img _55ym _55yn _55yo"]')
            print(f"Number of replies to click {len(replies)}")

            if not replies:
                print(f" No more replies on comment block {i + 1}")
                break

            replies_link = None

            if not loading_replies:
                print("No loading replies")
                replies_link = replies[0]
            elif len(replies) > len(loading_replies):
                print(f"Replies replies: {len(replies)}")
                print(f"Loading replies: {len(loading_replies)}")
                click_index = (len(replies) - len(loading_replies))
                replies_link = replies[-click_index]
            else:
                print(f"Replies replies: {len(replies)}")
                print(f"Loading replies: {len(loading_replies)}")
                break

            try:
                ActionChains(driver).move_to_element(replies_link).perform()
                driver.execute_script("scrollBy(0,200);")
                replies_link.click()
                ActionChains(driver).move_to_element(facebook_c).perform()
                time.sleep(1)
            except ElementClickInterceptedException as err:
                print("Element covered and not clickable")
                time.sleep(2)
                driver.execute_script("scrollBy(0,-500);")
                ActionChains(driver).move_to_element(replies_link).perform()
                replies_link.click()
                ActionChains(driver).move_to_element(facebook_c).perform()
                time.sleep(1)
                success_click = True

        except NoSuchElementException as err:
            print("Clicked all replies")
            break

all_comments = driver.find_elements_by_class_name("_72vr")
print(len(all_comments))

# with open("./index.html", 'r', encoding='utf-8') as file:
#     source_code = file.read()

soup = BeautifulSoup(driver.page_source, 'html.parser')

# ==============================================================
# Post data
post_block = "._5pcr.userContentWrapper"  # class name
post_title_with_time = "._6a._5u5j._6b"  # class name get the abbr and use the data-utime attribute
post_text = "._5pbx.userContent._3576"  # class name
post_reactions = "UFI2ReactionsCount/sentenceWithSocialContext"  # data-testid span
post_share = "UFI2SharesCount/root"  # data-testid

# Comments data
comment_block = "UFI2CommentsList/root_depth_0"  # data-testid div
parent_comment = "UFI2Comment/root_depth_0"  # data-testid div
reply_comment = "UFI2Comment/root_depth_1"  # data-testid div

comment_body = "UFI2Comment/body"  # data-testid div
comment_user_name = "_6qw4"  # class name in a span
comment_text = "._3l3x"  # class name in a span inside a span
comment_reaction = "UFI2CommentTopReactions/tooltip"  # data-testid span

comment_creation_time = "livetimestamp"  # classname in abbr then get the data-utime attribute

post_block_html = soup.select(post_block)
driver.quit()

data = []
for (i, post_block_h) in enumerate(post_block_html):
    print(f"====================== Post {i + 1}======================", end="\n\n")

    post_title_with_time_h = post_block_h.select(post_title_with_time)

    post_author = post_title_with_time_h[0].select('h5 a')[0].text
    print(f"Post author: {post_author}")

    post_text_h = post_block_h.select(post_text)[0].text
    print(f"Post content: {post_text_h}")

    time_attr = post_title_with_time_h[0].select("abbr")[0].attrs
    time = datetime.fromtimestamp(int(time_attr['data-utime']))
    print(f"Time of post: {time}")

    post_reactions_h = post_block_h.findAll("span", {"data-testid": post_reactions})[0].text
    print(f"Total reactions: {post_reactions_h}")

    line = [post_author, post_text_h, time, post_reactions_h]
    data.append(line)

    print("\n==================== Comments ====================", end="\n\n")

    comment_block_h = post_block_h.findAll("div", {"data-testid": comment_block})
    all_parent_comments = comment_block_h[0].findAll("div", {"data-testid": parent_comment})
    all_child_comments = comment_block_h[0].findAll("div", {"data-testid": reply_comment})
    all_comments = all_parent_comments + all_child_comments

    for (j, comment) in enumerate(all_comments):
        print(f"Comment {j + 1}")
        username = comment.select("._6qw4")[0].text
        print(f"Username : {username}")

        comment_text_h = comment.select(comment_text)
        text = None
        if not comment_text_h:
            print(f"Comment text: IMAGE/GIF")
            text = "IMAGE/GIF"
        else:
            print(f"Comment text: {comment_text_h[0].text}")
            text = comment_text_h[0].text

        comment_creation_time_h = comment.findAll("abbr", {"class": ['livetimestamp']})[0].attrs
        print(f"Time of post: {datetime.fromtimestamp(int(comment_creation_time_h['data-utime']))}")
        time = datetime.fromtimestamp(int(comment_creation_time_h['data-utime']))

        comment_reaction_h = comment.find("span", attrs={'data-testid':comment_reaction})
        reaction = None

        if comment_reaction_h is not None:
            print(f"Total reactions: {comment_reaction_h.text}")
            reaction = comment_reaction_h.text
        else:
            print("Total reactions: 0")
            reaction = 0

        row = [username, text, time, reaction]
        data.append(row)

    data.append(["", "", "", ""])
    print(data)

with open("./data.csv", 'w', encoding='utf-8') as csv_file:
    fileWriter = csv.writer(csv_file, dialect='excel')
    for i in range(len(data)):
        fileWriter.writerow(data[i])

end_time = datetime.now()

print(f"Total time taken: {end_time - start_time}")
