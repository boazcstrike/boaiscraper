from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
from urllib.parse import urlparse, unquote

def download_civitai_images(output_dir="downloaded_images"):
    os.makedirs(output_dir, exist_ok=True)

    # Setup Selenium with Chrome
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)  # Add explicit wait

    try:
        # Load the page
        driver.get("https://civitai.com/images")

        # Wait for images to be present
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img[src*='image/']")))
        time.sleep(8)  # Additional wait for images to load

        processed_urls = set()
        scroll_count = 0

        while scroll_count < 10:  # Limit to 10 scrolls for testing
            # Find all image elements before scrolling
            images = driver.find_elements(By.CSS_SELECTOR, "img[src*='image/']")
            print(f"Found {len(images)} images")

            # Process images
            for img in images:
                try:
                    img_url = img.get_attribute('src')
                    if not img_url or img_url in processed_urls:
                        continue
                    print(f"Processing URL: {img_url}")  # Debug print

                    # Skip thumbnails and placeholders
                    if '_xs' in img_url or 'placeholder' in img_url.lower():
                        continue

                    processed_urls.add(img_url)

                    # Extract filename from URL
                    parsed_url = urlparse(img_url)
                    filename = unquote(os.path.basename(parsed_url.path))

                    # Ensure filename has an extension
                    if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        filename += '.jpg'

                    filepath = os.path.join(output_dir, filename)

                    # Download image
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                    if not os.path.exists(filepath):
                        img_response = requests.get(img_url, headers=headers)
                        img_response.raise_for_status()

                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)

                    print(f"Downloaded: {filename}")
                    time.sleep(0.75)  # Delay between downloads

                except Exception as e:
                    print(f"Error downloading image: {str(e)}")
                    continue

            # Scroll
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(5)  # Wait for new images to load

            scroll_count += 1
            print(f"Completed scroll {scroll_count}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        driver.quit()

    print("Download completed!")

if __name__ == "__main__":
    download_civitai_images()  # Adjust scroll_times as needed