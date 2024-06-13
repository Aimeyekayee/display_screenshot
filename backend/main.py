from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import os
import time
import datetime as dt

# Set default download folder for ChromeDriver
image_folder = r"\\172.23.3.18\shared\Andon"
if not os.path.exists(image_folder):
    os.makedirs(image_folder)
prefs = {"download.default_directory": image_folder}


def open_url(addresses):
    # SELENIUM SETUP
    logging.getLogger("WDM").setLevel(
        logging.WARNING
    )  # just to hide not so rilevant webdriver-manager messages
    edge_options = Options()
    # edge_options.headless = True
    # edge_options.use_chromium = True
    edge_options.add_argument("--headless")
    # edge_options.add_argument("--no-sandbox")
    # edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Edge(options=edge_options)
    driver.implicitly_wait(1)
    driver.maximize_window()
    for address in addresses:
        [url,name,by,locate_text] = address
        driver.get(url)
        WebDriverWait(driver,10).until(EC.invisibility_of_element_located((by,locate_text)))
        driver.set_window_size(1920, 1080)  # to set the screenshot width
        file_name = name
        save_screenshot(driver, "{}\{}.png".format(image_folder,file_name))
    driver.quit()


def save_screenshot(driver, file_name):
    height, width = scroll_down(driver)
    driver.set_window_size(width, height)
    img_binary = driver.get_screenshot_as_png()
    img = Image.open(BytesIO(img_binary))
    img.save(file_name)
    # print(file_name)
    print("{}: Screenshot saved as {}".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),file_name))


def scroll_down(driver):
    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")

    rectangles = []

    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width

            rectangles.append((ii, i, top_width, top_height))

            ii = ii + viewport_width

        i = i + viewport_height

    previous = None
    part = 0

    for rectangle in rectangles:
        if not previous is None:
            driver.execute_script(
                "window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1])
            )
            time.sleep(0.5)
        # time.sleep(0.2)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])

        previous = rectangle

    return total_height, total_width

def scheduled_tasks():
    url_list = [["http://192.168.101.70/View/browse/Rotor_Assy_Line2","OA_Rotor_Assy_Line2",By.CSS_SELECTOR,".loading-overlay-modal"],
                ["http://192.168.101.71/apl/monitor?boardno=7&pageno=2","Setup_time_Rotor_Assy_Line2",By.ID,"startLoadingAnime"],
                ["http://192.168.101.71/apl/monitor?boardno=9&pageno=2","Alarm_Pareto_Rotor_Assy_Line2",By.ID,"startLoadingAnime"]
                ]
    open_url(url_list)

scheduler = BlockingScheduler()
scheduler.add_job(scheduled_tasks,'interval', seconds=25)
scheduler.start()