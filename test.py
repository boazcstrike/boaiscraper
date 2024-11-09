from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
from urllib.parse import urlparse, unquote
import json

def scroll_civitai(output_dir="downloaded_images"):
    print("Starting download process...")
    os.makedirs(output_dir, exist_ok=True)

    print("Setting up Chrome driver...")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        print("Loading civitai.com/images...")
        driver.get("https://civitai.com/images")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        processed_urls = set()
        last_processed_count = 0
        stagnant_count = 0
        stagnant_threshold = 10
        main_element = driver.find_element(By.CSS_SELECTOR, ".scroll-area.flex-1")

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

                # Check if we hit bottom or no new content loaded
                if new_scroll >= new_height - main_element.size['height']:
                    print("Reached the bottom of the container")
                    break
                if new_height == last_height and new_scroll == current_scroll:
                    print("No new content loaded")
                    break

            # Find and count all images
            print("\nCounting images...")
            images = driver.find_elements(By.CSS_SELECTOR, ".scroll-area.flex-1 img")
            total_images = len(images)
            print(f"Found {total_images} total images")

    except Exception as e:
        print(f"Major error occurred: {str(e)}")

    finally:
        print("\nClosing browser...")
        driver.quit()

    print("Download process completed!")

if __name__ == "__main__":
    scroll_civitai()