from bs4 import BeautifulSoup
import requests
from sys import exit
import re


headers =  {'authority': 'topauto.fun', 'method': 'GET', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36 Edg/83.0.478.45', 'referer': 'https://anidb.net/anime'}

def busca(anime_name):
    anime_name = '%20'.join(anime_name.split())
    html = requests.get(f'https://anidb.net/anime/?adb.search={anime_name}%20&do.search=1', headers=headers)
    return html

def get_info(PATH, html):
    if(PATH != 0):
        url = 'https://anidb.net' + PATH
        html = requests.get(url, headers=headers)
        
    soup = BeautifulSoup(html.text, 'html.parser')
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
        try:
            itens = html_info.find_all('span', attrs={'class': 'tagname'})
            genres = [x.get_text() for x in itens]
            return True, "".join(genres);
        except:
            return False, False;


    def get_alternative_names():
        try:
            itens = html_info.find_all('label', attrs={'itemprop':"alternateName"})
            names = itens[0].get_text()
            return True, names;
        except:
            return False, False;
            
        

    def get_alternative_names_no():
        try:
            itens = html_info.find_all('label', attrs={'itemprop':"alternateName"})
            print(len(itens))
            if len(itens) >= 2:
                names = itens[1].get_text()
                return True, names
            return False, False;
        except:
            return False, False;

    def get_description():
        try:
            itens = soup.find_all('div', attrs={'itemprop': 'description'})
            text = [x.get_text() for x in itens]
            return True, "".join(text);
        except:
            return False, False;

    def get_image():
        try:
            itens = soup.find_all('img', attrs={'loading': 'lazy'})[0]['src']
            return True, itens;
        except:
            return False, False;

    def get_directly_related_anime():
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
            return True, name, links, image;
        except:
            return False, False, False, False;
        


    def get_indirectly_related_anime():
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
            return True, name, links, image;
        except:
            return False, False, False, False;

    
    def get_similar_anime():
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
            return True, name, links, image;
        except:
            return False, False, False, False, ;

    
    
    def get_episodes():
        try:
            #painel dos episódios
            itens = soup.find_all('form', attrs={'action': '/perl-bin/animedb.pl'})
            #episode
            episode_html = itens[4].find_all('abbr', attrs={'itemprop': 'episodeNumber'})
            episode_ep = [x.get_text().replace('\n','').replace('\t','') for x in episode_html]
            #Title
            title_html = itens[4].find_all('label', attrs={'itemprop': 'name'})
            episode_title = [x.get_text().replace('\n','').replace('\t','') for x in title_html]
            #Duration
            duration_html = itens[4].find_all('td', attrs={'itemprop': 'timeRequired'})
            episode_duration = [x.get_text().replace('\n','').replace('\t','') for x in duration_html]
            #Air-date
            date_html = itens[4].find_all('td', attrs={'itemprop': 'datePublished'})
            episode_date = [x.get_text().replace('\n','').replace('\t','') for x in date_html]
            return True, episode_ep, episode_title, episode_duration, episode_date;
        except:
            return False, False, False, False, False;

    def get_songs():
        try:
            #painel das músicas
            itens = soup.find_all('div', attrs={'class': 'pane hide songs'})
            #Name
            song_html = itens[0].find_all('td', attrs={'class': 'name song'})
            song_name = [x.get_text().replace('\n','').replace('\t','') for x in song_html]
            #href
            song_href = []
            r = re.compile('(?<=href=").*?(?=")')
            for y in song_html:
                song_href.append(r.findall(str(y))[0])
            #Local
            song_local_html = itens[0].find_all('td', attrs={'class': 'eprange'})
            song_local = [x.get_text().replace('\n','').replace('\t','') for x in song_local_html]
            return True, song_local, song_name, song_href;
        except:
            return False, False, False, False;
        
        
        
        
        
    #tag
    #name_alternative_1
    #name_alternative_2
    #description
    #image
    #directly_related_name, directly_related_links, directly_related_image
    #indirectly_related_name, indirectly_related_links, indirectly_related_image
    #similar_anime_name, similar_anime_links, similar_anime_image
    #episode_ep, episode_title, episode_duration, episode_date
    #song_local, song_name, song_href
    tag_check, tag = get_tag(); infs['Tags'] = tag_check;
    name_alternative_1_check, name_alternative_1 = get_alternative_names(); infs['Official_Title_Verified_Yes'] = name_alternative_1_check;
    name_alternative_2_check, name_alternative_2 = get_alternative_names_no(); infs['Official_Title_Verified_No'] = name_alternative_2_check;
    description_check, description = get_description(); infs['Description'] = description_check;
    image_check, image = get_image(); infs['Image'] = image_check;
    directly_related_check, directly_related_name, directly_related_links, directly_related_image = get_directly_related_anime(); infs['Directly related'] = directly_related_check;
    indirectly_related_check, indirectly_related_name, indirectly_related_links, indirectly_related_image = get_indirectly_related_anime(); infs['Indirectly related'] = indirectly_related_check;
    similar_anime_check, similar_anime_name, similar_anime_links, similar_anime_image = get_similar_anime(); infs['Similar anime'] = similar_anime_check;
    episode_check, episode_ep, episode_title, episode_duration, episode_date = get_episodes(); infs['Episodes'] = episode_check;
    song_check, song_local, song_name, song_href = get_songs(); infs['Songs'] = song_check;
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
        print()




#iniciando programa

html = busca(input('Digite um anime: '))
soup = BeautifulSoup(html.text, 'html.parser')
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
