from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

# === Step 1: Get ad code from ktoja ===
driver.get("https://ktoja.mybb.ru/viewtopic.php?id=1")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.code-box pre")))
first_post = driver.find_element(By.CSS_SELECTOR, "div.post")
code_block = first_post.find_element(By.CSS_SELECTOR, "div.code-box pre")
foreign_ad = code_block.text.strip()

# === Step 2: Try to detect PR.nick / PR.pass or PiarNik/PiarPas from page script ===
html_source = driver.page_source
pr_nick = None
pr_pass = None

pr_script_match = re.search(r"PR\.nick\s*=\s*['\"](.*?)['\"]", html_source)
pr_pass_match = re.search(r"PR\.pass\s*=\s*['\"](.*?)['\"]", html_source)
alt_nick_match = re.search(r"PiarNik\s*=\s*['\"](.*?)['\"]", html_source)
alt_pass_match = re.search(r"PiarPas\s*=\s*['\"](.*?)['\"]", html_source)

if pr_script_match and pr_pass_match:
    pr_nick = pr_script_match.group(1)
    pr_pass = pr_pass_match.group(1)
elif alt_nick_match and alt_pass_match:
    pr_nick = alt_nick_match.group(1)
    pr_pass = alt_pass_match.group(1)

if pr_nick and pr_pass:
    driver.get("https://ktoja.mybb.ru/login.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "req_username")))
    driver.find_element(By.NAME, "req_username").send_keys(pr_nick)
    driver.find_element(By.NAME, "req_password").send_keys(pr_pass)
    driver.find_element(By.NAME, "login").click()
    time.sleep(2)
else:
    print("❌ PR вход не найден. Прерываем.")
    driver.quit()
    exit()

# === Step 3: Login to miabella ===
driver.get("https://miabella.mybb.ru/login.php")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "req_username")))
driver.find_element(By.NAME, "req_username").send_keys("Mello")
driver.find_element(By.NAME, "req_password").send_keys("2345")
driver.find_element(By.NAME, "login").click()
time.sleep(2)

# === Step 4: Post the foreign ad to miabella ===
driver.get("https://miabella.mybb.ru/viewtopic.php?id=1")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "req_message")))
driver.find_element(By.NAME, "req_message").send_keys(foreign_ad)
driver.find_element(By.NAME, "submit").click()
time.sleep(3)

# === Step 5: Get LAST permalink on the page
permalinks = driver.find_elements(By.CSS_SELECTOR, "a.permalink")
last_permalink = permalinks[-1].get_attribute("href")

# === Step 6: Post back to ktoja
driver.get("https://ktoja.mybb.ru/viewtopic.php?id=1")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "req_message")))
reply_message = f"THIS IS magic and tea is missing\n{last_permalink}"
driver.find_element(By.NAME, "req_message").send_keys(reply_message)
driver.find_element(By.NAME, "submit").click()
time.sleep(3)

print("📦 Обе стороны опубликованы успешно.")
print("Ссылка на сообщение в miabella:", last_permalink)
driver.quit()
