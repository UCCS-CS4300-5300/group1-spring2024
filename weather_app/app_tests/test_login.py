from os import path
from django.test import TestCase
from django.test.testcases import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# class SeleniumTests(LiveServerTestCase):
#   @classmethod
#   def setUpClass(cls):
#     super(SeleniumTests, cls).setUpClass()

#     chrome_options = Options()
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument('--disable-dev-shm-usage')
#     chrome_options.add_argument('--headless')
#     chrome_options.add_argument("start-maximized"); 
#     chrome_options.add_argument("disable-infobars"); 
#     chrome_options.add_argument("--disable-extensions"); 
#     chrome_options.add_argument("--disable-gpu"); 
#     chrome_options.add_argument("--disable-dev-shm-usage"); 
#     # pkgs.chromedriver
#     # pkgs.chromium
#     # pkgs.python39Packages.selenium

    
#     cls.driver = webdriver.Chrome(options=chrome_options) #test says failed but it is using the driver correctly, no clue why but this works in VS Code

#   @classmethod
#   def tearDownClass(cls):
#     cls.driver.quit()
#     super(SeleniumTests, cls).tearDownClass()

#   #creates account correctly
#   def test_register(self):
#     self.driver.get(self.live_server_url + '/accounts/register/')
#     self.driver.find_element(By.NAME, "username").send_keys("test1")
#     self.driver.find_element(By.NAME, "email").send_keys("test1@123.123")
#     self.driver.find_element(By.NAME, "password1").send_keys("omenxiii2")
#     self.driver.find_element(By.NAME, "password2").send_keys("omenxiii2")
#     self.driver.find_element(By.NAME, "Create User").click()

#   #creates account with out passwords matching
#   def test_bad_register(self):
#     self.driver.get(self.live_server_url + '/accounts/register/')
#     self.driver.find_element(By.NAME, "username").send_keys("test2")
#     self.driver.find_element(By.NAME, "email").send_keys("test2@123.123")
#     self.driver.find_element(By.NAME, "password1").send_keys("omenxiii2")
#     self.driver.find_element(By.NAME, "Create User").click()

#   #logs into created account with the correct credentials
#   def test_login_page(self):
#     self.driver.get(self.live_server_url + '/accounts/login/')
#     self.driver.find_element(By.NAME, "username").send_keys("test1")
#     self.driver.find_element(By.NAME, "password").send_keys("omenxiii2")
#     self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='login']").click()

#   #logs into created account without the correct credentials
#   def test_login_page_with_invalid_credentials(self):
#     self.driver.get(self.live_server_url + '/accounts/login/')
#     self.driver.find_element(By.NAME, "username").send_keys("test1")
#     self.driver.find_element(By.NAME, "password").send_keys("invalid_password")
#     self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='login']").click()
