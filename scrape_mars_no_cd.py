#dependencies
import time
import pandas as pd
from splinter import Browser
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import requests
import os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def scrape():
    
    
    
    options = webdriver.ChromeOptions()
    options.binary_location = os.environ['GOOGLE_CHROME_BIN']

    options.add_argument('--headless')


    print("before wd")

    wd = webdriver.Chrome(executable_path=os.environ['GOOGLE_CHROME_SHIM'], chrome_options=options)
    
    print("getting ready to visit the first url")
    wd.get('https://mars.nasa.gov/news/')

    # Wait for the dynamically loaded elements to show up
    WebDriverWait(wd, 1).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "content_title")))

    # And grab the page HTML source
    response = wd.page_source
    wd.quit()

    soup = bs(response, "lxml")
    print(soup.prettify())

    
    
#     options = webdriver.ChromeOptions()
#     options.binary_location = "/app/.apt/usr/bin/google-chrome-stable"
#     driver = webdriver.Chrome(chrome_options=options)
    
    
#     from selenium.webdriver.chrome.options import Options as ChromeOptions
#     chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)
#     print("chrome_bin: ", chrome_bin)
#     opts = ChromeOptions()
#     opts.binary_location = chrome_bin
#     self.selenium = webdriver.Chrome(executable_path="chromedriver", chrome_options=opts)


#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument('--headless')
#     chrome_options.add_argument('--disable-gpu')
#     chrome_options.add_argument('--no-sandbox')
#     chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)
#     print("chrome_bin1: ", chrome_bin)
    
     
    
#     executable_path = {'executable_path': chrome_bin}
#     browser = Browser('chrome', **executable_path, options=chrome_options)
    
     
    #executable_path = {"executable_path": chrome_bin}
    #browser = Browser("chrome", **executable_path, headless=True)

    
    #browser = Browser('chrome', headless=True)

    #store all the scraped data in a dictionary
    mars_dictionary = {}


    # PART 1 - NASA Mars News

    # URL of NASA Mars News website
    #url = 'https://mars.nasa.gov/news/'
    
    

    #browser.visit(url)

    #response = browser.html
    #soup = bs(response, "lxml")

    # extract the latest News Title and Paragragh Text.

    # get the title
    container = soup.find('div', class_="content_title")
    news_title = container.a.text

    # get the paragraph description
    container = soup.find('div', class_="image_and_description_container")
    text_tot = container.find('div', class_="rollover_description_inner")
    news_p = text_tot.text

    print("title: ", news_title)
    print("paragraph: ", news_p)

    #store in mars_dictionary
    mars_dictionary["news_title"] = news_title
    mars_dictionary["news_para"] = news_p


    # PART II - JPL Mars Space Images - Featured Image
    jpl_url = 'https://www.jpl.nasa.gov'

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # use splinter to get the URL of the image

    # HTML object
    html = browser.html

    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')

    # Retrieve the article with the featured image
    article = soup.find('article', class_='carousel_item')

    # Use Beautiful Soup's find() method to navigate and retrieve attributes
    h1 = article.find('h1', class_='media_feature_title').text
    print(h1)

    # Click the 'Full Image' button
    browser.click_link_by_partial_text('FULL IMAGE')


    # then click "more info" to get the full size image (wait for a few seconds first)
    time.sleep(1)

    browser.click_link_by_partial_text('more info')

    # get the URL of the large image

    # get the html of the new page
    # HTML object
    html = browser.html

    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')

    figure = soup.find('img', class_="main_image")
    print(figure)

    fig_url = figure['src']

    print(fig_url)

    featured_image_url = jpl_url + fig_url
    print(featured_image_url)

    # store in mars_dictionary
    mars_dictionary["featured_img_title"] = h1
    mars_dictionary["featured_img_url"] = featured_image_url


    # PART III - Mars Weather
    # Visit the Mars Weather twitter account here and scrape the latest Mars weather tweet from the page.
    # Save the tweet text for the weather report as a variable called mars_weather.
    url = 'https://twitter.com/marswxreport?lang=en'

    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, 'html.parser')


    tweets = soup.find_all('div', class_="tweet")
    for tweet in tweets:
        if (tweet['data-screen-name'] == "MarsWxReport"):
            #save the tweet
            mars_weather = tweet.find('p', class_="tweet-text").text
            print(mars_weather)
            break

    # store in mars_dictionary
    mars_dictionary["weather"] = mars_weather

    #PART IV - Mars Facts
    url = "https://space-facts.com/mars/"
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, 'html.parser')

    tables = pd.read_html(url)
    df = tables[0]
    #change the header
    header = pd.Series(["Type","Value"])
    df.rename(columns = header, inplace=True)
    df.set_index("Type", inplace=True)
    html_table = df.to_html()
    html_table.replace('\n', '')

    # store in mars_dictionary
    mars_dictionary["mars_facts"] = html_table



    #PART V - Mars Hemispheres
    # Visit the USGS Astrogeology site to obtain high resolution images for each of Mars' hemispheres.

    astro_url = "https://astrogeology.usgs.gov"
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, 'html.parser')


    browser.visit(url)

    # use splinter to get the URLs of the hemisphere pages

    # HTML object
    html = browser.html

    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')

    # results are returned as an iterable list
    hemispheres = soup.find_all('a', class_="itemLink")

    # Loop through returned results

    hemisphere_image_urls = []

    for result in hemispheres:

        # Error handling
        try:
            # Identify title
            title = result.find('h3').text

            # Identify link
            link = result['href']
            print("title: ", title)

            # use the full URL
            full_link = astro_url + link
            print("full-link: ", full_link)

            # go to the link to get to the page with the full image
            response = requests.get(full_link)
            # Create BeautifulSoup object; parse with 'html.parser'
            soup = bs(response.text, 'html.parser')

            try:

                # get full image url from href in the <a> in the div class='download'
                download = soup.find('div', class_='downloads')

                full_href = download.find('a')['href']

                print("full_href: ", full_href)

                # put title and image URL into dictionary
                hemisphere_image_urls.append({"title": title, "img_url": full_href})


            except Exception as f:
                print("f: ", f)

        except Exception as e:
            print("e: ", e)

    hemisphere_image_urls

    # store in mars_dictionary
    mars_dictionary["hemispheres"] = hemisphere_image_urls


    return mars_dictionary
