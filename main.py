import time
import requests
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


# Set the download directory
DOWNLOAD_DIR = r"C:\Users\adjum\Documents\Python\Numilog\FICHIERS"
DRIVER_PATH = r"C:\Users\PIGIERCI\Documents\Web Scraping\Drivers\edgedriver_win64\msedgedriver.exe"


# Set up Edge options
edge_options = Options()
edge_options.use_chromium = True
# edge_options.add_argument("--headless")
edge_options.add_argument("--disable-gpu")

prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
}
edge_options.add_experimental_option("prefs", prefs)

# Set up Edge WebDriver service
service = Service(DRIVER_PATH)
s_service = Service(DRIVER_PATH)
driver = webdriver.Edge(service=service, options=edge_options)
s_driver = webdriver.Edge(service=s_service, options=edge_options)
session = requests.Session()


def connect():
    payload = {
        'txtLogin': 'yvay03@gmail.com',
        'password': 'vvvv0000',
    }
    response = session.post("https://www.numilog.com/Accueil.aspx", data=payload)

    if response.status_code == 200:
        print("Successfully connected.")
        return True

    print("Failed to connect.")
    return False


def perform_downloads():
    try:
        driver.get("https://www.numilog.com/Pages/Livres/EbookGratuit.aspx")
        box = driver.find_element(By.CLASS_NAME, "Bloc_title")
        links = [_ for _ in [_.get_attribute('href') for _ in box.find_elements(By.TAG_NAME, "a")] if 'fltr' in _]

        for link in links:
            driver.execute_script(f"window.open('{link}', '_blank');")
            driver.switch_to.window(driver.window_handles[1])

            # Ensure the filter element is present
            selected_filter = driver.find_element(By.CLASS_NAME, "Bloc_title").find_element(By.CLASS_NAME, 'active')
            download_buttons = driver.find_elements(By.CLASS_NAME, "RemAddPanier")

            for button in download_buttons:
                try:
                    button.click()
                    time.sleep(1)  # Wait for the modal to appear
                    close_modal = driver.find_element(By.CLASS_NAME, "modal-dialogforCart").find_element(
                        By.CLASS_NAME, "modalClose")
                    close_modal.click()
                except (NoSuchElementException, ElementClickInterceptedException) as e:
                    print("Error:", e.msg)
                    continue

            # Process the download page
            redirection_link = driver.find_element(By.ID, "ctl02_ctrlPanier_HyperLink1").get_attribute("href")
            s_driver.get(redirection_link)
            link_to_dl_page = s_driver.find_element(By.ID, "ctl02_CentrePage_LinkButtonValiderCmd").get_attribute("href")
            s_driver.get(link_to_dl_page)
            dl_links = driver.find_elements(By.CLASS_NAME, "btn")

            for dl_link in dl_links:
                dl_link.click()
                try:
                    driver.find_element(By.CLASS_NAME, "modal-content").find_element(
                        By.CLASS_NAME, "modal-body").find_element(
                        By.CSS_SELECTOR, "div[class*='btn']").click()
                    time.sleep(5)
                except NoSuchElementException:
                    print("Download button or confirmation modal not found.")
                    continue

            print(selected_filter)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
        s_driver.quit()


if connect():
    perform_downloads()
else:
    print("Failed to establish a session.")


# edge webdriver link: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH#downloads
