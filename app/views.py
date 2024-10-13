import json
import os

import google.generativeai as genai
from flask import Blueprint, request
from playwright.sync_api import sync_playwright

views = Blueprint("views", __name__, url_prefix='/api')


def get_html_content(page_url):
    """
    Method to initialize playwright and extract HTML content from the web page.
    :param page_url: URL of the product page
    :return: HTML content of the product page
    """

    with sync_playwright() as p:
        webkit = p.webkit
        browser = webkit.launch()
        context = browser.new_context()
        page = context.new_page()

        print("Playwright initialized")
        page.goto(page_url, timeout=0)
        html_content = page.content()

        browser.close()
    print("Done fetching html")
    return html_content


def get_reviews_from_llm(html_content):
    """
    Method to initialize Gemini LLM and scrape user reviews from HTML content provided by playwright.
    :param html_content: HTML content from playwright
    :return: User reviews string in the specifies format
    """

    model = genai.GenerativeModel(os.getenv('GEMINI_MODEL'))
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    print("Gemini model initialized")

    response_format = """{"reviews_count": 100,"reviews": [{"title": "Review Title","body": "Review body text",
                        "rating": 5,"reviewer": "Reviewer Name"}]}"""

    model_response = model.generate_content(f"Extract all user reviews from this html content - {html_content}. Avoid "
                                            f"generating any new text. Return the response strictly in this JSON format"
                                            f"without any explanations - {response_format}").text
    json_object = model_response[model_response.find('{'): model_response.rfind('}') + 1]

    print("Gemini response received")
    return json_object


@views.route('/reviews', methods=['GET'])
def scrape_reviews():
    """
    Endpoint to scrape user reviews from product page whose URL to be passed as page_url query param.
    :return: JSON object containing the total number of reviews and a list of review objects containing details.
    """

    page_url = request.args.get('page_url')
    print("Extracting user reviews for - ", page_url)

    with open('app/html_content.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    # html_content = get_html_content(page_url)

    reviews = get_reviews_from_llm(html_content)
    response = json.loads(reviews)

    print(f"Extracted {response['reviews_count']} reviews")
    return response
