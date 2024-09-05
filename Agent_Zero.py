import requests
from requests.exceptions import HTTPError, RequestException, Timeout, ConnectionError
import time
import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import random
import os
import json


class Agent:
    def __init__(self, conversation_history_file, system_prompt, print_response, model="llama3.1"):
        self.conversation_history_file = conversation_history_file
        self.print_response = print_response
        self.templates = []
        self.system_prompt = "This is the history of our chat.\n" + system_prompt
        self.headers = {"Content-Type": "application/json"}
        self.model = model

    def prompt_for_input(self, user_input=None):
        if user_input is None:
            user_input = input("Me: ")
        
        if user_input.lower() == 'exit':
            print("Exiting...")
            return
        
        self.write_to_file(f"Me: {user_input}")
        print("Thinking...")
        
        conversation_history = self.read_from_file()

        #Get the template
        user_input_transformed = self.get_template_prompt(user_input)
        print(f"user_input_transformed: {user_input_transformed}")
        prompt_string = f"{self.system_prompt}\n{conversation_history}\nMe: {user_input_transformed}"

        response = self.generate_response(prompt_string)
        
        if response:
            self.write_to_file(f"You: {response}")
            if self.print_response:
                print(f"AI: {response}")
            return response

    def generate_response(self, prompt_string):
        data = {
            "model": self.model,
            "prompt": prompt_string,
            "stream": False
        }
        
        try:
            response = requests.post("http://localhost:11434/api/generate", headers=self.headers, data=json.dumps(data))
            response.raise_for_status()  # This will raise an error for bad HTTP codes
            return json.loads(response.text).get("response")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
        
    def get_template_prompt(self, prompt):
        #prompt_template = "Prompt Template: <user prompt> return or write a response based on the following template <template>"
        allTemplates = ""
        if len(self.templates) > 0:
            for t in self.templates:
                allTemplates += t
            return prompt+" return or write a response based on the following python script template "+allTemplates
        return prompt

            
    def get_template(self, template_list):
        for template in template_list:
            content = self.read_file_content(template)
            if content:
                self.templates.append(content)
        #print(f"Templates: {self.templates}")

    def write_to_file(self, text):
        with open(self.conversation_history_file, 'a') as file:
            file.write(text + "\n")

    def read_from_file(self):
        return self.read_file_content(self.conversation_history_file)

    def read_file_content(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        print(f"Error: File not found - {file_path}")
        return ""

# Example usage
if __name__ == "__main__":
    agent = Agent("create Crew.txt", 
                  "You are a business strategist. Your goal is to research and put together the most effective team for creating marketing campaigns.",
                  True)
    #agent.get_template(["Team/Team_Template.txt"])
    
    agent.prompt_for_input("create a team to market cold tea")





# class WebScraper:
#     def __init__(self, api_key, search_engine_id, user_agent=None, delay_range=(1, 3)):
#         self.api_key = api_key
#         self.search_engine_id = search_engine_id
#         self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
#         self.results = []
#         self.delay_range = delay_range
#         self.session = requests.Session()  # Reuse connections

#     def google_custom_search(self, query, num_results=10):
#         """Performs a Google Custom Search."""
#         if not self.api_key or not self.search_engine_id:
#             logging.error("API key or Search Engine ID is not set.")
#             return []

#         base_url = "https://www.googleapis.com/customsearch/v1"
#         params = {
#             'key': self.api_key,
#             'cx': self.search_engine_id,
#             'q': query,
#             'num': num_results
#         }

#         try:
#             response = self.session.get(base_url, params=params)
#             response.raise_for_status()
#             search_results = response.json()
#             self._parse_search_results(search_results)
#         except HTTPError as http_err:
#             logging.error(f"HTTP error occurred: {http_err}")
#         except RequestException as err:
#             logging.error(f"Error occurred: {err}")

#     def _parse_search_results(self, search_results):
#         """Extracts and stores relevant information from search results."""
#         items = search_results.get('items', [])
#         self.results = [
#             {
#                 'title': item.get('title'),
#                 'link': item.get('link'),
#                 'snippet': item.get('snippet')
#             }
#             for item in items
#         ]

#     def is_scraping_allowed(self, url):
#         """Checks if scraping is allowed on the target URL via robots.txt."""
#         parsed_url = urlparse(url)
#         robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

#         rp = RobotFileParser()
#         rp.set_url(robots_url)
#         rp.read()

#         return rp.can_fetch("*", url)

#     def fetch_website_content(self, url, timeout=10):
#         """Fetches website content with respect to robots.txt rules and delay."""
#         headers = {'User-Agent': self.user_agent}

#         if not self.is_scraping_allowed(url):
#             logging.warning(f"Scraping is not allowed by the site's robots.txt: {url}")
#             return None

#         try:
#             delay = random.uniform(*self.delay_range)
#             time.sleep(delay)

#             response = self.session.get(url, headers=headers, timeout=timeout)
#             response.raise_for_status()

#             return self._handle_response_content(response)
#         except Timeout:
#             logging.error("The request timed out.")
#         except ConnectionError:
#             logging.error("A connection error occurred.")
#         except HTTPError as http_err:
#             logging.error(f"HTTP error occurred: {http_err}")
#         except RequestException as err:
#             logging.error(f"An error occurred: {err}")

#     def _handle_response_content(self, response):
#         """Handles different content types returned by the server."""
#         content_type = response.headers.get('Content-Type', '')
#         if 'text/html' in content_type:
#             return response.text
#         elif 'application/json' in content_type:
#             return response.json()
#         else:
#             return response.content

# # Example usage:
# if __name__ == "__main__":
#     api_key = os.getenv("GOOGLE_API_KEY", "")
#     search_engine_id = os.getenv("SEARCH_ENGINE_ID", "")

#     scraper = WebScraper(api_key, search_engine_id)
#     query = "Who is Lehlohonolo Mosoang"
#     scraper.google_custom_search(query)

#     if scraper.results:
#         for index, result in enumerate(scraper.results):
#             print(f"Result {index + 1}:")
#             print(f"Title: {result['title']}")
#             print(f"Link: {result['link']}")
#             print(f"Snippet: {result['snippet']}\n")
#     else:
#         print("No results found or an error occurred.")
