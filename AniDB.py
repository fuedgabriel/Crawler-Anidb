from bs4 import BeautifulSoup, SoupStrainer
import requests
from sys import exit
import re
import requests_cache
from datetime import datetime
import threading
import time

headers =  {'authority': 'topauto.fun', 'method': 'GET', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36 Edg/83.0.478.45', 'referer': 'https://anidb.net/anime'}

'''Variável Global'''
tag_check  = ""; tag = [];
name_alternative_1_check = False; name_alternative_1 = ""; 
name_alternative_2_check = False;name_alternative_2 = "";
description_check = False; description = "";
image_check = False; image = "";
directly_related_check = False; directly_related_name = []; directly_related_links = []; directly_related_image = [];
indirectly_related_check = False; indirectly_related_name = []; indirectly_related_links = []; indirectly_related_image = [];
similar_anime_check = False; similar_anime_name = []; similar_anime_links = []; similar_anime_image = [];
episode_check = False; episode_ep = []; episode_title = []; episode_duration = []; episode_date = [];
song_check = False; song_local = []; song_name = []; song_href = [];


def busca(anime_name):
    anime_name = '%20'.join(anime_name.split())
    requests_cache.install_cache('primeiro')
    html = requests.get(f'https://anidb.net/anime/?adb.search={anime_name}%20&do.search=1', headers=headers)
    return html

def get_info(PATH, html):
    if(PATH != 0):
        url = 'https://anidb.net' + PATH
        requests_cache.install_cache('segundo')
        html = requests.get(url, headers=headers)


    print("__________________________")
    print(" 1 Requisição: "+ str(datetime.now()))      
    strainer = SoupStrainer('div', attrs={'class': 'g_content anime_all sidebar'})
    print(" 2 Requisição: "+ str(datetime.now()))      
    soup = BeautifulSoup(html.text, 'xml', parse_only=strainer)
    print(" 3 Requisição: "+ str(datetime.now()))  
    print("__________________________")
    print("\n\n")
    try:
        html_info = soup.find_all("div", {"class": "g_definitionlist"})[0]
    except IndexError as error:
        print("Anime não encontrado")
        exit()

    html_info = [x for x in html_info][1]
    html_info = [y for y in html_info][1]
    
    infs = {
    'Main_Title' : None,
    'Official_Title_Verified_Yes' : None,
    'Official_Title_Verified_No' : None,
    'Type' : None,
    'Year' : None,
    'Tags' : None,
    'Rating' : None,
    'Avarage' : None,
    'Description': None,
    'Image': None,
    'Directly related': None,
    'Indirectly related': None,
    'Similar anime': None, 
    'Songs': None,
    'Episodes': None
    }
    
    def get_tag():
        global tag_check, tag;
        try:
            itens = html_info.find_all('span', attrs={'class': 'tagname'})
            genres = [x.get_text() for x in itens]
            tag_check = True;
            tag = genres
            #return True, "".join(genres);
        except:
            tag_check = False;
            tag = False;
            #return False, False;

    def get_alternative_names():
        global name_alternative_1;
        global name_alternative_1_check;
        try:
            itens = html_info.find_all('label', attrs={'itemprop':"alternateName"})
            name_alternative_1 = itens[0].get_text()
            name_alternative_1_check = True;
 #           return True, names;
        except:
            name_alternative_1 = False
            name_alternative_1_check = False;
#            return False, False;
            
    def get_alternative_names_no():
        global name_alternative_2;
        global name_alternative_2_check
        try:
            itens = html_info.find_all('label', attrs={'itemprop':"alternateName"})
            if len(itens) >= 2:
                name_alternative_2 = itens[1].get_text()
                name_alternative_2_check = True
                return 0
                #return True, names
            name_alternative_2 = False
            name_alternative_2_check = False
            
            #return False, False;
        except:
            name_alternative_2 = False
            name_alternative_2_check = False
            #return False, False;
            
    def get_description():
        global description_check;
        global description;
        try:
            itens = soup.find_all('div', attrs={'itemprop': 'description'})
            text = [x.get_text() for x in itens]
            description_check = True;
            description = "".join(text);
            #return True, "".join(text);
        except:
            description_check = False;
            description = False;
            #return False, False;

    def get_image():
        global image_check;
        global image;
        try:
            itens = soup.find_all('img', attrs={'loading': 'lazy'})[0]['src']
            image_check = True;
            image = itens;
            #return True, itens;
        except:
            image_check = False;
            image = False;
            #return False, False;

    def get_directly_related_anime():
        global directly_related_check;
        global directly_related_name;
        global directly_related_links;
        global directly_related_image;
        try:
            #painel dos animes diretamente relacionados
            itens = soup.find('div', attrs={'class': 'pane directly_related'})
            #image
            direct_image = itens.find_all('img', attrs={'loading': 'lazy'})
            image = [x.get('src') for x in direct_image]
            #name
            direct_name = itens.find_all('a', attrs={'class': 'name-colored'})
            name = [x.get_text() for x in direct_name]
            links = [x.get('href') for x in direct_name]
            directly_related_check = True;
            directly_related_name = name;
            directly_related_links = links;
            directly_related_image = image;
            #return True, name, links, image;
        except:
            directly_related_check = False;
            directly_related_name = False;
            directly_related_links = False;
            directly_related_image = False;
            #return False, False, False, False;
        
    def get_indirectly_related_anime():
        global indirectly_related_check;
        global indirectly_related_name;
        global indirectly_related_links;
        global indirectly_related_image;
        try:
            #painel dos animes indiretamente relacionados
            itens = soup.find('div', attrs={'class': 'g_section relations indirect'})
            #image
            indirect_image = itens.find_all('img', attrs={'loading': 'lazy'})
            image = [x.get('src') for x in indirect_image]
            #name
            indirect_name = itens.find_all('a', attrs={'class': 'name-colored'})
            name = [x.get_text() for x in indirect_name]
            links = [x.get('href') for x in indirect_name]
            indirectly_related_check = True;
            indirectly_related_name = name;
            indirectly_related_links = links;
            indirectly_related_image = image;
            #return True, name, links, image;
        except:
            indirectly_related_check = False;
            indirectly_related_name = False;
            indirectly_related_links = False;
            indirectly_related_image = False;
            #return False, False, False, False;

    def get_similar_anime():
        global similar_anime_check;
        global similar_anime_name;
        global similar_anime_links;
        global similar_anime_image
        try:
            #painel dos animes diretamente similares
            itens = soup.find('div', attrs={'class': 'g_section similaranime resized'})
            #image
            similar_image = itens.find_all('img', attrs={'loading': 'lazy'})
            image = [x.get('src') for x in similar_image]
            #name
            similar_name = itens.find_all('div', attrs={'class': 'name'})
            name = [x.get_text().replace('\n','') for x in similar_name]
            #links
            links = []
            r = re.compile('(?<=href=").*?(?=")')
            for y in similar_name:
                links.append(r.findall(str(y))[0])
            similar_anime_check =  True;
            similar_anime_name = name;
            similar_anime_links = links;
            similar_anime_image = image;
            #return True, name, links, image;
        except:
            similar_anime_check =  False;
            similar_anime_name = False;
            similar_anime_links = False;
            similar_anime_image = False;
            #return False, False, False, False;

    def get_episodes():
            global episode_check;
            global episode_date;
            global episode_ep;
            global episode_title;
            global episode_duration;
            try:
                #painel dos episódios
                itens = soup.find_all('form', attrs={'action': '/perl-bin/animedb.pl'})
                #episode
                episode_html = itens[1].find_all('abbr', attrs={'itemprop': 'episodeNumber'})
                episode_ep = [x.get_text().replace('\n','').replace('\t','') for x in episode_html]
                #Title
                title_html = itens[1].find_all('label', attrs={'itemprop': 'name'})
                episode_title = [x.get_text().replace('\n','').replace('\t','') for x in title_html]
                #Duration
                duration_html = itens[1].find_all('td', attrs={'itemprop': 'timeRequired'})
                episode_duration = [x.get_text().replace('\n','').replace('\t','') for x in duration_html]
                #Air    -date
                date_html = itens[1].find_all('td', attrs={'itemprop': 'datePublished'})
                episode_date = [x.get_text().replace('\n','').replace('\t','') for x in date_html]
                episode_check = True;
                #return True, episode_ep, episode_title, episode_duration, episode_date;
            except:
                episode_check = False; episode_date = False; episode_duration = False; episode_ep = False; episode_title = False;
                #return False, False, False, False, False;


    def get_songs():
        global song_check;
        global song_href;
        global song_name;
        global song_local;
        try:
            #painel das músicas
            itens = soup.find_all('div', attrs={'class': 'pane hide songs'})
            #Name
            song_html = itens[0].find_all('td', attrs={'class': 'name song'})
            song_name = [x.get_text().replace('\n','').replace('\t','') for x in song_html]
            #href
            r = re.compile('(?<=href=").*?(?=")')
            for y in song_html:
                song_href.append(r.findall(str(y))[0])
            #Local
            song_local_html = itens[0].find_all('td', attrs={'class': 'eprange'})
            song_local = [x.get_text().replace('\n','').replace('\t','') for x in song_local_html]
            song_check = True;
            #return True, song_local, song_name, song_href;
        except:
            song_check = False;song_href = False; song_local = False; song_name = False;
            #return False, False, False, False;

    def start_all():
        #Definindo
        thread_tag = threading.Thread(target=get_tag)
        thread_name_alternative = threading.Thread(target=get_alternative_names);
        thread_name_alternative_no = threading.Thread(target=get_alternative_names_no);
        thread_description = threading.Thread(target=get_description);
        thread_image = threading.Thread(target=get_image);
        thread_directly_related = threading.Thread(target=get_directly_related_anime);
        thread_indirectly_related = threading.Thread(target=get_indirectly_related_anime);
        thread_similar_anime = threading.Thread(target=get_similar_anime);
        thread_episodes = threading.Thread(target=get_episodes)
        thread_songs = threading.Thread(target=get_songs);
        #iniciando
        thread_tag.start()
        thread_name_alternative.start()
        thread_name_alternative_no.start()
        thread_description.start()
        thread_image.start()
        thread_episodes.start()
        thread_directly_related.start()
        thread_indirectly_related.start()
        thread_similar_anime.start()
        thread_songs.start()



        while (thread_tag.is_alive() != False or thread_name_alternative.is_alive() != False or thread_name_alternative_no.is_alive() != False or thread_description.is_alive() != False or thread_image.is_alive() != False or thread_episodes.is_alive() != False or thread_directly_related.is_alive() != False or thread_indirectly_related.is_alive() != False or thread_similar_anime.is_alive() != False or thread_songs.is_alive() != False):
            time.sleep(0.5)


    start_all()
    infs['Tags'] = tag_check;
    infs['Official_Title_Verified_Yes'] = name_alternative_1_check;
    infs['Official_Title_Verified_No'] = name_alternative_2_check;
    infs['Description'] = description_check;
    infs['Image'] = image_check;
    infs['Directly related'] = directly_related_check;
    infs['Indirectly related'] = indirectly_related_check;
    infs['Similar anime'] = similar_anime_check;
    infs['Episodes'] = episode_check;
    infs['Songs'] = song_check;

    #infs['Added_By'], infs['Edited_By'] = get_added_and_edited()
    #infs['Resources'] = get_resources()
    for x in html_info:
        # MAIN TITLE
        if'itemprop="name"' in str(x):
            main_title = x.get_text().strip().split('\n')[1]; infs['Main_Title'] = main_title;
        # TYPE
        elif 'class="type"' in str(x):
            main_font = x.get_text().split('\n')[2]; infs['Type'] = main_font;
        elif 'itemprop="startDate"' in str(x):
            main_year = x.get_text().strip().split('\n')[1]; infs['Year'] = main_year;
        # RATING
        elif 'itemprop="ratingValue"' in str(x):
            main_rating = x.get_text().strip().split('\n')[1]; infs['Rating'] = main_rating;
        # AVARAGE
        elif 'class="rating tmpanime mid"' in str(x):
            main_avarage = x.get_text().strip().split('\n')[1]; infs['Avarage'] = main_avarage;    

    for x in infs.keys():
        pass
        print(x + ":", infs[x])
        

#iniciando programa

html = busca(input('Digite um anime: '))
soup = BeautifulSoup(html.text, 'xml')
html_nomes_animes = soup.find_all("td", {"class": "name main anime"})
if(str(html_nomes_animes).find(r'[<td class="name main anime" data-label="Title">') == -1):
    get_info(0, html)
    
else:
    nomes_animes = [x.find('a').text for x in html_nomes_animes]
    href_animes = [x.find('a')['href'] for x in html_nomes_animes]
    cont = 1 
    for x in nomes_animes:
        print([cont], x)
        cont += 1
    
    number = int(input('\nSelecione um número: ')) - 1
    print()
    get_info(href_animes[number], 1)











#elif 'class="rating attavg mid"' in str(x):
         #   infs['Review_Rating'] = x.get_text().strip().split('\n')[1]
        #elif 'class="rating attavg"' in str(x):
         #   infs['Review_Rating'] = x.get_text().strip().split('\n')[1]

#elif 'itemprop="datePublished"' in str(x):
         #   infs['Year'] = x.get_text().strip().split('\n')[1]
        # REVIEW RATING
'''
 #date_added
    #date_editade
    def get_added_and_edited():
        try:
            itens = html_info.find_all('span', attrs={'class':"date"})
            return True, itens[0].get_text(), itens[1].get_text();
        except:
            return False;

    def get_resources():
        try:
            itens = html_info.find_all('span', attrs={'class': 'text'})
            text = [x.get_text() for x in itens]
            resources = []
            for x in text:
                if(len(x) < 20):
                    if(x != ''):
                        resources.append(str(x+','))
            return True, "".join(resources);
        except:
            return False;
'''
