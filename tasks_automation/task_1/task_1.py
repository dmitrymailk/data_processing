from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

service = Service("./geckodriver.exe")
driver = webdriver.Firefox(
    service=service
)
initial_web_page = "http://bi.gks.ru/biportal/contourbi.jsp?allsol=1&solution=Dashboard&project=%2FDashboard%2FPrices_week"
driver.get(initial_web_page)

links = driver.find_elements(by=By.TAG_NAME, value="td")

for link in links:
    link.click()
    time.sleep(5000)


driver.close()
