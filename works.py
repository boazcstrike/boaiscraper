import os
import requests
import time
from dotenv import load_dotenv

from urllib.parse import urlparse, unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BoAIScraper():
    def __init__(self, driver):
        self.driver = driver

    def set_cookies(self):
        """cookies updated as of March 14, 2025"""
        try:
            cookies = [
                {
                    "name": "__Secure-civitai-token",
                    "value": os.getenv("CIVIT_TOKEN"),
                    "domain": ".civitai.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": True,
                },
                {
                    "name": "__Secure-next-auth.callback-url",
                    "value": os.getenv("NEXT_AUTH_CALLBACK_URL"),
                    "domain": ".civitai.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": True,
                },
                {
                    "name": "__eoi",
                    "value": os.getenv("EOI"),
                    "domain": ".civitai.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False,
                },
                {
                    "name": "__gads",
                    "value": os.getenv("GADS"),
                    "domain": ".civitai.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False,
                },
                {
                    "name": "__gpi",
                    "value": os.getenv("GPI"),
                    "domain": ".civitai.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False,
                },
                {
                    "name": "_sharedID",
                    "value": os.getenv("SHARED_ID"),
                    "domain": ".civitai.com",
                    "path": "/",
                    "secure": False,
                    "httpOnly": False,
                },
                {
                    "name": "_sharedID_cst",
                    "value": os.getenv("SHARED_ID_CST"),
                    "domain": ".civitai.com",
                    "path": "/",
                    "secure": False,
                    "httpOnly": False,
                },
                {
                    "name": "_sharedID_last",
                    "value": os.getenv("SHARED_ID_LAST"),
                    "domain": ".civitai.com",
                    "path": "/",
                    "secure": False,
                    "httpOnly": False,
                },
                {
                    "name": "cto_bundle",
                    "value": os.getenv("CTO_BUNDLE"),
                    "domain": ".civitai.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False,
                }
            ]
            for cookie in cookies:
                print(f"Setting cookie: {cookie['name']} = {cookie['value']}")
                self.driver.add_cookie(cookie)
            print("Cookies set successfully.")
        except Exception as e:
            print(f"Error setting cookies: {str(e)}")

    def authenticate_civit(self):
        self.set_cookies()
        # self.navigate_to_login()

    def navigate_to_login(self):
        try:
            print("Waiting for sign in button...")
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[@href='/login?returnUrl=/']")
                )
            )
            print("Found sign in button, clicking...")
            sign_in_button.click()
        except Exception as e:
            print(f"Error clicking sign in button: {str(e)}")


def download_civitai_images(output_dir="downloaded_images"):
    print("Starting download process...")
    os.makedirs(output_dir, exist_ok=True)

    print("Setting up Chrome driver...")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    query = input("\nEnter a search query (leave blank if none): ")

    tags = [
        {"name": "photorealistic", "url": "https://civitai.com/images?tags=172"},
    ]

    civitai_url = f"https://civitai.com/images?q={query}" if query != "" and query != None else "https://civitai.com/images"
    # civitai_url = tags[0]["url"] if query == "tags" or query == None else civitai_url
    # civitai_url = "https://civitai.com/videos"

    try:
        print(f"Loading {civitai_url}...")
        driver.get(civitai_url)
        ai = BoAIScraper(driver=driver)

        ai.authenticate_civit()
        driver.refresh()
        print("Website reloaded successfully.")
        time.sleep(2)

        try:
            print("Waiting for filter button...")
            filter_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Filters')]"))
            )
            print("Found filter button, clicking...")
            filter_button.click()


            # starting here - 3-14-2025 these dont work
            print("Waiting for month option...")
            month_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@role='radio' and @value='Month']")
                )
            )
            print("Found month option, trying to click...")
            month_option.click()

            print("trying period filter again...")
            print("Waiting for month option...")
            month_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='mantine-r5f']"))
            )
            print("Found month option, clicking...")
            month_option.click()
            # end here - 3-14-2025 these dont work


            print("Waiting 4 seconds for filter to apply...")
            time.sleep(4)  # Wait for the filter to apply
            print("Filter applied successfully")
        except Exception as e:
            print(f"Error applying time filter: {str(e)}")

        # Update headers with authentication and cookies
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,fil;q=0.8,zh-TW;q=0.7,zh;q=0.6,it;q=0.5",
            "Content-Type": "application/json",
            "Priority": "u=1, i",
            "Referer": "https://civitai.com/images",
            "Sec-Ch-Ua": '"Chromium";v="134", "NotA;Brand";v="24", "Google Chrome";v="134"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "X-Client": "web",
            "X-Client-Date": "1741877879835",
            "X-Client-Version": "5.0.552",
            # there is one more, unsure what it looks like, unsure if needed
            # "X-Fingerprint": "xxx"
        }

        processed_urls = set()
        last_processed_count = 0
        stagnant_count = 0
        stagnant_threshold = 10

        main_element = driver.find_element(By.CSS_SELECTOR, ".scroll-area.flex-1")

        downloaded_images = []

        while True:
            print("\n=== Starting new scroll cycle ===")
            # Scroll logic for infinite scroll within container
            for i in range(6):
                print(f"Scroll attempt {i+1}/6 within cycle")

                # Get current scroll position and height
                last_height = driver.execute_script("return arguments[0].scrollHeight", main_element)
                current_scroll = driver.execute_script("return arguments[0].scrollTop", main_element)

                # Scroll down within the container
                driver.execute_script("""
                    arguments[0].scrollTo({
                        top: arguments[0].scrollTop + arguments[0].clientHeight,
                        behavior: 'smooth'
                    });
                """, main_element)

                # Wait for content to load
                time.sleep(10)

                # Check if we've reached the bottom
                new_height = driver.execute_script("return arguments[0].scrollHeight", main_element)
                new_scroll = driver.execute_script("return arguments[0].scrollTop", main_element)

                print(f"Scroll position: {new_scroll}/{new_height}")

                if new_scroll >= new_height - main_element.size['height']:
                    print("Reached the bottom of the container")
                    break

                if new_height == last_height and new_scroll == current_scroll:
                    print("No new content loaded, moving to next attempt")
                    break

            print("\nSearching for images...")
            if 'video' in civitai_url:
                videos = driver.find_elements(By.TAG_NAME, "video")
                images = []
                for video in videos:
                    sources = video.find_elements(By.TAG_NAME, "source")
                    for source in sources:
                        src = source.get_attribute('src')
                        if src and src.endswith('.mp4'):
                            images.append(source)
                            break
            else:
                images = driver.find_elements(By.TAG_NAME, "img")

            print(f"Found {len(images)} total <img ...> <video ...> elements")

            all_images_downloaded = True
            new_images = 0
            for img in images:
                img_url = img.get_attribute('src')
                if img_url in downloaded_images:
                    continue
                all_images_downloaded = False
                if download_single_image(img, headers, output_dir, processed_urls):
                    downloaded_images.append(img_url)
                    new_images += 1

            if all_images_downloaded:
                for i in range(5):
                    print(f"Scroll attempt {i+1}/5 within cycle")

                    # Get current scroll position and height
                    last_height = driver.execute_script("return arguments[0].scrollHeight", main_element)
                    current_scroll = driver.execute_script("return arguments[0].scrollTop", main_element)

                    # Scroll down within the container
                    driver.execute_script("""
                        arguments[0].scrollTo({
                            top: arguments[0].scrollTop + arguments[0].clientHeight,
                            behavior: 'smooth'
                        });
                    """, main_element)

                    # Wait for content to load
                    time.sleep(2)

                    # Check if we've reached the bottom
                    new_height = driver.execute_script("return arguments[0].scrollHeight", main_element)
                    new_scroll = driver.execute_script("return arguments[0].scrollTop", main_element)

                    print(f"Scroll position: {new_scroll}/{new_height}")

                    if new_scroll >= new_height - main_element.size['height']:
                        print("Reached the bottom of the container")
                        break

                    if new_height == 120000:  # i set this because this is too much image data for me
                        print("Reached the bottom of the container")
                        break

                    if new_height == last_height and new_scroll == current_scroll:
                        print("No new content loaded, moving to next attempt")
                        break

            print(f"\nNew images this cycle: {new_images}")
            print(f"Total unique images processed so far: {len(processed_urls)}")

            if len(processed_urls) == last_processed_count:
                stagnant_count += 1
                print(f"No new images found. Stagnant count: {stagnant_count}/{stagnant_threshold}")
                if stagnant_count >= stagnant_threshold:
                    print("No new images found after multiple scrolls. Stopping.")
                    break
            else:
                stagnant_count = 0
                print("Found new images, resetting stagnant count")

            last_processed_count = len(processed_urls)

    except Exception as e:
        print(f"Major error occurred: {str(e)}")

    finally:
        print("\nClosing browser...")
        driver.quit()

    print("Download process completed!")

def download_single_image(img, headers, output_dir, processed_urls):
    """Downloads a single image and returns True if successful, False otherwise"""
    # return False
    try:
        img_url = img.get_attribute('src')

        # Convert thumbnail URL to full-size image URL
        img_url = img_url.replace('width=450', 'width=1920')

        if not img_url or img_url in processed_urls:
            return False

        if 'placeholder' in img_url.lower() or '_xs' in img_url:
            return False

        processed_urls.add(img_url)

        parsed_url = urlparse(img_url)
        filename = unquote(os.path.basename(parsed_url.path))
        file_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4']
        if not any(filename.lower().endswith(ext) for ext in file_exts):
            for file_ext in file_exts:
                if file_ext in img_url.lower():
                    filename += file_ext
                
        date_folder = time.strftime("%m%d%Y")
        dated_output_dir = os.path.join(output_dir, date_folder)
        os.makedirs(dated_output_dir, exist_ok=True)

        filepath = os.path.join(dated_output_dir, filename)

        print(f"\nAttempting to download image: {filename}")
        if os.path.exists(filepath):
            print(f"Not downloaded: {filename}")
        else:
            print(f"From URL: {img_url}")

            img_response = requests.get(img_url, headers=headers)
            img_response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(img_response.content)

            print(f"Successfully downloaded: {filename}")
        time.sleep(0.5)
        return True

    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    download_civitai_images()
