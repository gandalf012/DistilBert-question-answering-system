'""" Search and scrappe from search page """'
import requests
import json, os
from dateutil import parser
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from time import sleep


def get_page_link(page=None, keywords=None):
    'Extract each page link in bs4 format'
    url = 'https://jingdaily.com/page/{}/?s={}'.format(page, keywords) 
    headers = {'User-Agent': UserAgent().random}
    return(requests.get(url, headers=headers))


def get_article_link(nb_article=None, keywords=None, tag_link=None, class_link=None):
    'Extract all link in all_page'
    app = 10                                # articles per page
    nb_page = (nb_article // app) + 2
    nb_last_article = nb_article % app
    links = []
    for page in range(1, nb_page):
        source = get_page_link(page, keywords)
        soup = BeautifulSoup(source.text, 'lxml')
        contents = soup.find_all('{}'.format(tag_link), class_=class_link)
        if page < (nb_page - 1):
            for content in contents:
                links.append(content.a['href'])
        else:
            for content in contents[0: nb_last_article]:
                links.append(content.a['href'])

        if len(contents) < app:
            break
    print('{} links available'.format(len(links)))
    return(links)


def get_summary(nb_article=10000, keywords=None, save_steps=50, tag_link='div', class_link='article-content', 
                    tag_title='h1', tag_sum='div', class_sum='article-content'):
    "Extract paragraph from article for article doesn't exist in keywords.json"

    all_link = get_article_link(nb_article=nb_article, keywords=keywords, tag_link=tag_link, class_link=class_link)
    print('scrapping in progress...')

    if not os.path.exists('./data'):
        os.makedirs('./data')

    all_contents = []
    filename = './data/{}.json'.format(keywords.replace(' ', '_'))
    # if filename doesn't exits in data, scrap nb_article and save in data/filename
    if not os.path.exists(filename):   
        for i, link in enumerate(all_link):
            headers = {'User-Agent': UserAgent().random}

            trials = 5
            source = None
            while True:
                if trials == 0 : break
                try:
                    source = requests.get(link, headers=headers)
                    break
                except:
                    sleep(6-trials)
                    trials -= 1
            if source is None : 
                print("Exiting tag: '{}'".format(keywords))
                return

            soup_link = BeautifulSoup(source.text, 'lxml')
            # Print link and http response status code
            if save_steps > 0 and i % save_steps == 0:
                print(i, link, source.status_code)

            title = soup_link.find('{}'.format(tag_title))
            meta = soup_link.find('li', class_='post-date')
            if meta is None:
                continue
            contents = soup_link.find('{}'.format(tag_sum), class_=class_sum)
            summary = []
            for content in contents.find_all('p'):
                summary.append(content.text)
            all_contents.append({'title':title.text,'meta':meta.text, 'paragraphs':summary})

        print("The {} datasets contains {} articles".format(keywords, len(all_contents)))

    else:
        with open('./data/{}.json'.format(keywords.replace(' ', '_'))) as json_file:
            datasets = json.load(json_file)

        last_article = datasets[0]  # last article date in datastets
        last_date = parser.parse(last_article['meta'])
        last_title = last_article['title']
        for i, link in enumerate(all_link):
            headers = {'User-Agent': UserAgent().random}
            source = requests.get(link, headers=headers)
            soup_link = BeautifulSoup(source.text, 'lxml')
            if save_steps > 0 and i % save_steps == 0:
                print(i, link, source.status_code)

            title = soup_link.find('{}'.format(tag_title))
            meta = soup_link.find('li', class_='post-date')
            if meta is None:
                continue
            if parser.parse(meta.text) > last_date:
                contents = soup_link.find('{}'.format(tag_sum), class_=class_sum)
                summary = []
                for content in contents.find_all('p'):
                    summary.append(content.text)
                all_contents.append({'title':title.text,'meta':meta.text, 'paragraphs':summary})

            elif parser.parse(meta.text) == last_date:
                if not title.text == last_title:
                    contents = soup_link.find('{}'.format(tag_sum), class_=class_sum)
                    summary = []
                    for content in contents.find_all('p'):
                        summary.append(content.text)
                    all_contents.append({'title':title.text,'meta':meta.text, 'paragraphs':summary})
                else:
                    continue
            else:
                break
        
        if len(all_contents) == 1: # To solve dict extended to list problem
            all_contents = [all_contents] + datasets
        else:
            all_contents.extend(datasets)

        print("The {} datasets now contains {} articles".format(keywords, len(all_contents)))

    # Save/Overwrite the new/updated datasets in json file
    with open(filename, 'w') as json_file:
        json.dump(all_contents, json_file)

    return (all_contents, len(all_link))


# if __name__ == "__main__":
#     get_summary(nb_article=1000, keywords='', save_steps=10)


