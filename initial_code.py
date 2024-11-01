

# # Freshdesk API details


# # Article related -
# # url = f'https://{domain}.freshdesk.com/api/v2/solutions/articles'    # Check articles 
# # url = f'https://{domain}.freshdesk.com/support/solutions/articles/6000262116-website-links-not-working-can-t-navigate' #Specific article - Note - can access images as well
# # url = f'https://{domain}.freshdesk.com/solution/categories.json'




import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class FreshDeskSolutionsDataFetcher:
    def __init__(self):
        # Initialize with API credentials from environment variables
        self.api_key = os.getenv('API_KEY')
        self.domain = os.getenv('DOMAIN')

    class Article:
        def __init__(self, id, name, content, images_url):
            self.id = id
            self.name = name
            self.content = content
            self.images_url = images_url

    class Folder:
        def __init__(self, id, name):
            self.id = id
            self.name = name
            self.articles = []

        def add_article(self, article):
            self.articles.append(article)

    class Category:
        def __init__(self, id, name):
            self.id = id
            self.name = name
            self.folders = []

        def add_folder(self, folder):
            self.folders.append(folder)

    # Method to fetch categories, folders, and articles
    def fetch_data(self):
        categories_list = []  # Store categories here

        # Fetch categories
        categories_url = f'https://{self.domain}.freshdesk.com/solution/categories.json'
        response = requests.get(categories_url, auth=HTTPBasicAuth(self.api_key, 'X'))

        if response.status_code == 200:
            categories = response.json()
            for category_data in categories:
                category_id = category_data['category']['id']
                category_name = category_data['category']['name']
                category_obj = self.Category(category_id, category_name)

                folders = category_data['category']['folders']

                for folder in folders:
                    folder_id = folder['id']
                    folder_name = folder['name']
                    folder_obj = self.Folder(folder_id, folder_name)

                    article_url = f'https://{self.domain}.freshdesk.com/solution/categories/{category_id}/folders/{folder_id}.json'
                    response = requests.get(article_url, auth=HTTPBasicAuth(self.api_key, 'X'))

                    if response.status_code == 200:
                        articles = response.json()
                        articles_data = articles['folder']['articles']
                        for article in articles_data:
                            article_id = article['id']
                            article_name = article['title']
                            article_html_description = article['description']

                            soup = BeautifulSoup(article_html_description, 'html.parser')
                            text_content = ' '.join([p.get_text() for p in soup.find_all('p')])
                            image_urls = [img['src'] for img in soup.find_all('img')]  #Fetching Image URLS 

                            article_obj = self.Article(article_id, article_name, text_content, image_urls)
                            folder_obj.add_article(article_obj)
                    category_obj.add_folder(folder_obj)
                categories_list.append(category_obj)
        return categories_list

    # Method to display fetched data
    def display_data(self, categories_data):
        for category in categories_data:
            print(f'Category: {category.name}')
            for folder in category.folders:
                print(f'  Folder: {folder.name}, Articles: {len(folder.articles)}')

if __name__ == "__main__":
    fetcher = FreshDeskSolutionsDataFetcher()
    categories_data = fetcher.fetch_data()
    fetcher.display_data(categories_data)


# Sample Output - 
# (myenv) (base) vaishnavidaber@Vaishnavis-MacBook-Air Files % python3 initial_code.py       

# Category: Troubleshooting
#   Folder: Troubleshooting, Articles: 8
# Category: Training
#   Folder: Training/Beginner Resources, Articles: 1
# Category: Event Calendar (Modern Tribe)
#   Folder: How to Create a Single Event, Articles: 6
#   Folder: Recurring Events, Articles: 6
#   Folder: Event Details, Articles: 5
#   Folder: Event List Widgets, Articles: 2
#   Folder: Event Calendar Settings, Articles: 4
#   Folder: Video Tutorials, Articles: 3
#   Folder: Series vs Recurring Events, Articles: 1