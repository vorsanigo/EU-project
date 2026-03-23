import logging
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import csv

import time
from selenium.webdriver.support.ui import WebDriverWait


class WebScraping:


    def find_city_chrome_geo(self, city, driver):
        '''
        Search for a name of a city (which could be mispelled or anything) in google and retrieve the first result from google (with often the autocorrection -> suggested result)
        '''
        
        # Navigate to Google
        driver.get("https://www.google.com")

        # Perform a Google search
        try:
            search_box = driver.find_element(By.NAME, "q")
            driver.execute_script("arguments[0].value = '" + city + "';", search_box)
            driver.execute_script("arguments[0].form.submit();", search_box)
            # Wait for search results to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'search')))
            # Extract the city name
            # Locate the city name element using an XPath (adjust this depending on the actual structure of the page)
            try:
                #city_name = driver.find_element(By.XPATH, '//div[@role="heading//h2/span"]').text#
                #print(f"City Name: {city_name}")
                city_name = driver.find_element(By.XPATH, '//div[@class="DoxwDb"]').text#
                #city_name = driver.find_element(By.XPATH, '//div[@class="QqPSMb"]').text#
                print(f"City Name: {city_name}")
            except:
                city_name = None
                print("City name not found.") 
        except:
            city_name = None
        
        
        return city_name

    

    def find_city_chrome_wiki(self, city, driver):
        '''
        Search for a name of a city in google and retrieve the first result from wikipedia
        '''
        
        # Navigate to Google
        driver.get("https://www.google.com")

        city_name = None
        print('input city', city)
        # Perform a Google search
        try:
            search_box = driver.find_element(By.NAME, "q")
            driver.execute_script("arguments[0].value = '" + city + "';", search_box)
            driver.execute_script("arguments[0].form.submit();", search_box)
            # Wait for search results to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'search')))
            try:
                search_results = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]')
                print('results', search_results)
                for result in search_results:
                    city_name = None
                    title = result.find_element("tag name", "h3").text
                    link = result.find_element("tag name", "a").get_attribute("href")
                    print(f"Title: {title}\nLink: {link}\n")
                    print(' ? link wiki', link[11:24])
                    if link[11:24] == "wikipedia.org":
                        city_name = link[30:]
                        city_name = city_name.replace('_', ' ')
                        print('city', city_name)
                        break   
            except Exception as e:
                print(f"Error 2")
                city_name = None

        except:
            print(f"Error 1")
            city_name = None

        return city_name


    def find_city_chrome_loop(self, city_list, type, output_path):
        '''
        Loop to apply find_city_chrome_geo and/or find_city_chrome_wiki
        '''

        #df = pd.DataFrame()

        # Set up the Selenium WebDriver
        # Make sure you have the path to your downloaded ChromeDriver
        chrome_driver_path = "/usr/bin/chromedriver"

        # Create a Service object for the ChromeDriver
        service = Service(executable_path=chrome_driver_path)

        # Initialize the WebDriver using the Service object
        driver = webdriver.Chrome(service=service)

        csv_file = output_path
        csv_columns = ['old city', 'chrome city']
        
        logger = logging.StreamHandler()
        logger.setLevel(logging.ERROR)
        pbar = tqdm(total=len(city_list), position=1)
        pbar.set_description("Web scraping")

        with open(csv_file, mode='w', newline='') as csvfile:

            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()

            print(city_list)
            
            if type == 'geo':
                for city in city_list:
                    print(city)
                    time.sleep(3)
                    chrome_city = self.find_city_chrome_geo(city + ' city', driver)
                    try:
                        writer.writerow({'old city': city, 'chrome city': chrome_city})
                    except:
                        print('I/O error')
                        pass
                    pbar.update(1)
            
            elif type == 'wiki':
                print('wiki')
                for city in city_list:
                    print('city', city)
                    time.sleep(3)
                    chrome_city = self.find_city_chrome_wiki(city + ' city', driver)
                    try:
                        writer.writerow({'old city': city, 'chrome city': chrome_city})
                    except:
                        print('I/O error')
                        pass
                    pbar.update(1)
                
            elif type == 'mix':
                print('mix')
                for city in city_list:
                    time.sleep(3)
                    print('geo')
                    chrome_city = self.find_city_chrome_wiki(city + ' city', driver)
                    if chrome_city == None:
                        print('wiki')
                        chrome_city = self.find_city_chrome_wiki(city + ' city', driver)
                    try:
                        writer.writerow({'old city': city, 'chrome city': chrome_city})
                    except:
                        print('I/O error')
                        pass
                    pbar.update(1)

                pbar.close()

        driver.quit()



# Example
'''df_cities = pd.read_csv('analysis/organizations/updated_new_nan_7.csv')#update_5_nominatim_dist.csv
city_list = df_cities['user']
city_finder = WebScraping()
city_finder.find_city_chrome_loop(city_list, 'mix', 'analysis/organizations/chrome_updated_new_nan_7.csv')'''

'''df_cities = pd.read_csv('cleaned organizations/intermediate res/org_9_nominatim_output_NAN.csv')#update_5_nominatim_dist.csv
city_list = df_cities['location']
city_finder = WebScraping()
city_finder.find_city_chrome_loop(city_list, 'mix', 'cleaned organizations/intermediate res/org_9_chrome_updated.csv')'''