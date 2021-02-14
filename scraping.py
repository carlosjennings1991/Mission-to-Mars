# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import time


# Mac users
executable_path = {'executable_path': 'chromedriver'}
browser = Browser('chrome', **executable_path, headless=False)



def scrape_all():
   # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(), 
        "hemispheres": hemisphere(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data



def mars_news(browser):
    print("scraping Mars news")
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browswer html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
            return None, None

    return news_title, news_p




def featured_image(browser):
    # Visit url
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/SPL_Space/{img_url_rel}'

    return img_url



def mars_facts():
    try:
        # use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")



def hemisphere(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Parse the data
    html = browser.html
    hemispheres_soup = soup(html, 'html.parser')

    hemisphere_image_urls = []

    links = browser.find_by_css('a.product-item h3')

    for item in range(len(links)):
        hemispheres = {}
        print("scraping hemisphere")
        
        #click the links for each of the 4 hemispheres
        browser.find_by_css('a.product-item h3')[item].click()
        time.sleep(1)
        
        #get the hrefs
        sample_link = browser.links.find_by_text('Sample').first
        hemispheres['img_url'] = sample_link['href']
        
        hemispheres['title'] = browser.find_by_css('h2.title').text
        
        hemisphere_image_urls.append(hemispheres)
        # move browswer back
        browser.back()


    return hemisphere_image_urls



if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())



