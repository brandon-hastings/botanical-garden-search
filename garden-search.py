import pandas as pd
import argparse
import requests
import numpy as np
from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse, urljoin


def main(project_folder, output_path):
    # link to garden explorer website
    website = 'https://www.gardenexplorer.org'
    # user input of column in data set holding names of plants
    plant_column = input('Enter column name holding plant names from the input dataset(project folder)')
    # set path to project folder
    data = Path(project_folder)
    # read in data set
    data_array = pd.read_csv(data, delimiter=',', dtype=str)
    # link sets for internal and external links on the main web page
    internal_urls = set()
    external_urls = set()

    # checks whether a url is a valid url by seeing if both the scheme and network are true
    def valid(url):
        # break url into separate sections that are checked below
        parsed = urlparse(url)
        # ie. the web site must have 'https' and 'a domain name' in the url
        return bool(parsed.netloc) and bool(parsed.scheme)

    # find and return all urls in supplied website url
    def website_links(url):
        # store found urls in set to deal with repeated links
        urls = set()
        # domain name of url without protocol
        domain_name = urlparse(url).netloc
        # set up html parser using beautiful soup
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        # find all a html tags, for each one, find href holding website link
        for a_tag in soup.findAll('a'):
            href = a_tag.attrs.get("href")
            # check if href is empty, if yes skip it
            if href == "" or href is None:
                continue
            # join url if it is relative
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # reassemble each url by fragments
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            # if url is not valid, skip it
            if not valid(href):
                continue
                # check if href is already in set
            if href in internal_urls:
                continue
            # check if href is to external link
            if domain_name not in href:
                if href not in external_urls:
                    external_urls.add(href)
                continue
            urls.add(href)
            internal_urls.add(href)
        print(external_urls)
        # return external urls only to search through
        return external_urls

    def search(main_url):
        # find column holding pant names from user input
        plants = data_array[plant_column]
        # empty list to hold plants held by each institution
        holdings = []
        # establish webdriver
        driver = webdriver.Safari()
        try:
            # driver = webdriver.Safari()
            # initiate driver and point to searchable website of each institution (from get_url function)
            driver.get(main_url)
            # make sure the web site is correct
            assert "Explorer" in driver.title
            # take web site table and use it as filename to store the matching plants as
            title = driver.title
            filename = ""
            # remove spaces and special characters from page title to use as filename
            for char in title:
                if char.isalnum():
                    filename += char
            print(filename)
            driver.close()
            for i in plants:
                while True:
                    try:
                        # get genus and species separately
                        print(i.split())
                        genus = i.split()[0]
                        species = i.split()[1]
                        # initiate driver and point to searchable website of each institution (from get_url function)
                        # open selenium automated browser
                        driver = webdriver.Safari()
                        # load url for each botanical garden search site
                        driver.get(main_url)
                        # find search field
                        search_field = driver.find_element_by_id(
                            "ctl00_ContentPlaceHolder1_TaxaFinder1_txtTaxonName")
                        # clear search field
                        search_field.clear()
                        # if species name is undefined, just search for genus
                        if species == "sp.":
                            search_field.send_keys(genus)
                        # else, search for genus and species normally
                        else:
                            search_field.send_keys(genus + " " + species)
                        # tell automaated browser to hit return key and return search result
                        search_field.send_keys(Keys.RETURN)
                        # Wait until "no results" is found
                        try:
                            WebDriverWait(driver, 3).until(EC.presence_of_element_located(
                                (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_TaxaFinder1_NoResult"]')))
                            driver.close()
                        # If not found, try statement exits and assumes the plant is
                        # returned by the search. Plant is then added to holdings list for that garden
                        except TimeoutException:
                            holdings.append(genus + " " + species)
                            driver.close()
                    except IndexError:
                        pass
                    except TimeoutException:
                        driver.close()
                        continue
                    break
            # save list of holdings to a txt file at output path as folder and garden name as filename
            np.savetxt(output_path + filename + ".txt", holdings, delimiter=',', fmt='%s')
        except AssertionError:
            driver.close()
            pass
    # for each url link returned after searching the main site, perform the search function on it
    for url in website_links(website):
        search(url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='matches csv holding plant names to botanical gardens')
    parser.add_argument('project_folder', type=str, help='input csv holding plant names')
    parser.add_argument('output_path', type=str, help='enter path for saving, only go folder level, the name'
                                                      ' "garden_matches.txt" will be added. Will overwrite '
                                                      'if already exist.')

    args = parser.parse_args()

    main(args.project_folder, args.output_path)
