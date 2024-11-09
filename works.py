from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
from urllib.parse import urlparse, unquote
import json

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
    civitai_url = f"https://civitai.com/images?q={query}" if query != "" and query != None else "https://civitai.com/images"

    try:
        print(f"Loading {civitai_url}...")
        driver.get(civitai_url)

        # Update headers with authentication and cookies
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
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

                if new_height == last_height and new_scroll == current_scroll:
                    print("No new content loaded, moving to next attempt")
                    break

            print("\nSearching for images...")
            images = driver.find_elements(By.TAG_NAME, "img")
            print(f"Found {len(images)} total image elements")

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
                # All visible images are already downloaded, scroll for more
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

        if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            filename += '.jpg'

        filepath = os.path.join(output_dir, filename)

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
    download_civitai_images()