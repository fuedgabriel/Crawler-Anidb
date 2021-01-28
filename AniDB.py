from bs4 import BeautifulSoup, SoupStrainer
import requests
from sys import getsizeof
import re
from datetime import datetime
import threading
import time
from googletrans import Translator
from googletrans.gtoken import TokenAcquirer
import json
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


authenticator = IAMAuthenticator('b90vIrKPB0VvDxxGy6uTXBcEHmfoaRH1V-1BWLK5Kk1R')
language_translator = LanguageTranslatorV3(version='2018-05-01', authenticator=authenticator)
language_translator.set_service_url('https://api.us-south.language-translator.watson.cloud.ibm.com/instances/95ac7bac-3427-4ddd-9fc8-7d9fe8e909ed')


headers =  {'authority': 'topauto.fun', 'method': 'GET', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36 Edg/83.0.478.45', 'referer': 'https://anidb.net/anime'}
headers_android =  {'authority': 'topauto.fun', 'user-agent': 'Mozilla/5.0 (Linux; Android 11; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36'}
server = "http://localhost:7844/api/"
'''Variável Global'''
GlobalAnime = ""
tag_check  = False; tag = [];
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
    html = requests.get(f'https://anidb.net/anime/?adb.search={anime_name}%20&do.search=1', headers=headers)
    return html

def get_info(PATH, html):
    if(PATH != 0):
        url = 'https://anidb.net' + PATH
        html = requests.get(url, headers=headers)
  
    strainer = SoupStrainer('div', attrs={'class': 'g_content anime_all sidebar'})
    soup = BeautifulSoup(html.text, 'xml', parse_only=strainer)
    try:
        html_info = soup.find_all("div", {"class": "g_definitionlist"})[0]
    except IndexError as error:
        payload = {
            "Name": str(GlobalAnime),
            "Color":"",
            "Image":""
        }
        requests.post('http://localhost:7844/api/AnimeErro', json=payload)
        print("_____________________________________________")
        print('\033[31m'+'Erro, não encontrado: \033[33m'+ str(GlobalAnime))
        return 0
        

    html_info = [x for x in html_info][1]
    html_info = [y for y in html_info][1]
    
    infs = {
    'Main_Title' : None,
    'Official_Title_Verified_Yes' : None,
    'Official_Title_Verified_No' : None,
    'Episodios' : None,
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

    def tradutor_ibm_connect(array):
        translation = language_translator.translate(text=array, model_id='en-pt').get_result() 
        traducao = json.dumps(translation, indent=2, ensure_ascii=False)
        traducao = json.loads(traducao)
        title = []
        for x in traducao['translations']:
            title.append(x['translation']) 
        return title;

    def tradutor_ibm(array):
        if(len(array)>=500):
            num = len(array)/2
            array_um = array[:int(num)]
            array_dois = array[int(num):]
            um = tradutor_ibm_connect(array_um)
            dois = tradutor_ibm_connect(array_dois)
            title = array_um+array_dois
            return title
        else:
            return tradutor_ibm_connect(array)
        

    
    def tradutor(texto_en):
        translator = Translator()
        texto_en = texto_en.split('Source:', 1)[0]
        text_pt = translator.translate(texto_en, src='en', dest="pt")
        return text_pt.text;



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
            name_alternative_1 = ''
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
            name_alternative_2 = ''
            name_alternative_2_check = False
            
            #return False, False;
        except:
            name_alternative_2 = ''
            name_alternative_2_check = False
            #return False, False;
            
    def get_description():
        global description_check;
        global description;
        
        try:
            itens = soup.find_all('div', attrs={'itemprop': 'description'})
            text = [x.get_text() for x in itens]
            description_check = True;
            description = tradutor("".join(text));
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
            directly_related_name = '';
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
            indirectly_related_links = False;
            indirectly_related_image = False;
            indirectly_related_name = '';
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
            similar_anime_name = '';
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
                episode_title_en = [x.get_text().replace('\n','').replace('\t','') for x in title_html]
                if(episode_title_en == []):
                    ("1"+1)
                episode_title = tradutor_ibm(episode_title_en)
                #episode_title = tradutor(episode_title_en)
                #print(episode_title)
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
            song_check = False;song_href = False; song_local = False; song_name = '';
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
    global tag;
    for x in html_info:
        # MAIN TITLE
        if'itemprop="name"' in str(x):
            main_title = x.get_text().strip().split('\n')[1]; infs['Main_Title'] = main_title;
        # Episodios
        elif 'class="type"' in str(x):
            main_font = x.get_text().split('\n')[2];
            main_font = main_font.split(',')
            if(len(main_font) == 2):
                tag.append(main_font[0])
                infs['Episodios'] = main_font[1];
        elif 'class="g_odd type"' in str(x):
            main_font = x.get_text().split('\n')[2];
            main_font = main_font.split(',')
            if(len(main_font) == 2):
                tag.append(main_font[0])
                infs['Episodios'] = main_font[1];
        elif 'itemprop="startDate"' in str(x):
            main_year = x.get_text().strip().split('\n')[1]; infs['Year'] = main_year;
        # RATING
        elif 'itemprop="ratingValue"' in str(x):
            main_rating = x.get_text().strip().split('\n')[1]; infs['Rating'] = main_rating;
        # AVARAGE
        elif 'class="rating tmpanime mid"' in str(x):
            main_avarage = x.get_text().strip().split('\n')[1]; infs['Avarage'] = main_avarage;    
        
    if(tag_check == True and description_check == True and image_check == True and episode_check == True):
        print("_____________________________________________")
        print("Anime aprovado: " + str(main_title))
        AllCategory = requests.get('http://localhost:7844/api/Category/all')
        AllCategory = json.loads(AllCategory.content)
        Category = []
        for cat in AllCategory:
            Category.append(cat['Name'])
        cat_temp = []
        otherTag = []
        for x in tag:
            otherTag.append(x)
            if(x in Category):
                cat_temp.append(x)
        for x in cat_temp:
            tag.remove(x)
        for x in tag:
            payload = {
                "Name": str(x)
                }
            requests.post('http://localhost:7844/api/Category', json=payload)
        tagId = []
        for x in otherTag:
            link = 'http://localhost:7844/api/Category/search/'+str(x)
            tagRequest = requests.get(link)
            tagId.append(json.loads(tagRequest.content)[0]['_id'])
        Diretamente = []
        for x in range(0, len(directly_related_name)):
            Diretamente.append({
                "id":"",
                "Name":str(directly_related_name[x]),
                "Imagem":str(directly_related_image[x]),
                "Link":str(directly_related_links[x])
            })
        Indiretamente = []
        for x in range(0, len(indirectly_related_name)):
            Indiretamente.append({
                "id":"",
                "Name":str(indirectly_related_name[x]),
                "Imagem":str(indirectly_related_image[x]),
                "Link":str(indirectly_related_links[x])
            })
        Similares = []
        for x in range(0, len(similar_anime_name)):
            Similares.append({
                "id":"",
                "Name":str(similar_anime_name[x]),
                "Imagem":str(similar_anime_image[x]),
                "Link":str(similar_anime_links[x])
            })
        Musicas = []
        for x in range(0, len(song_name)):
            Musicas.append({
                "id":"",
                "Name":str(song_name[x]),
                "Local":str(song_local[x]),
                "Link":str(song_href[x])
            })
        animejson = {
            "Titulo_principal": str(main_title),
            "Titulo_verificado": str(name_alternative_1),
            "Titulo_nao_official": str(name_alternative_2),
            "Episodios": str(main_font[1]),
            "Ano": str(main_year),
            "Nota": str(main_rating),
            "Imagem": str(image),
            "Descricao": str(description),
            "Categorias": tagId,
            "Diretamente_relacionado": Diretamente,
            "Indiretamente_relacionado": Indiretamente,
            "Animes_similares": Similares,
            "Musicas":Musicas
            }
        insertAnime = requests.post('http://localhost:7844/api/Animes', json=animejson)
        _id = json.loads(insertAnime.content)['_id']
        print('\033[32m'+'Adicionado'+str(main_title)+'\033[0;0m')

        return _id;
    else:
        payload = {
            "Name": str(GlobalAnime),
            "Color":"",
            "Image":""
        }
        requests.post('http://localhost:7844/api/AnimeErro', json=payload)
        print("_____________________________________________")
        print("Erro: \033[33m"+ str(GlobalAnime))
        return False;
    '''
    for x in infs.keys():
        pass
        print(x + ":", infs[x])
    '''
        

#iniciando programa
def search(anime):
    global GlobalAnime
    GlobalAnime = anime;
    html = busca(anime)
    soup = BeautifulSoup(html.text, 'xml')
    html_nomes_animes = soup.find_all("td", {"class": "name main anime"})
    if(str(html_nomes_animes).find(r'[<td class="name main anime" data-label="Title">') == -1):
        return get_info(0, html);
    else:
        nomes_animes = [x.find('a').text for x in html_nomes_animes]
        href_animes = [x.find('a')['href'] for x in html_nomes_animes]
        cont = 1 
        for x in nomes_animes:
            print([cont], x)
            cont += 1
        number = int(input('\nSelecione um número: ')) - 1
        return get_info(href_animes[number], 1);



def GetList():    
    page = requests.get('http://appanimeplus.tk/api-animesbr-11.php?letra=', headers=headers_android)
    page = json.loads(page.content)
    return page

def GetAnime():
    lista = GetList()
    for x in lista:
        _id = search(x['category_name'])
        if(_id !=False):
            print('\033[34m'+'_id:'+ str(_id))
            link = ('http://appanimeplus.tk/api-animesbr-11.php?cat_id='+str(x['id']))
            episodes = requests.get(link, headers=headers_android)
            episodes = json.loads(episodes.content)
            for y in episodes:
                ep = y['title'].split(" ")
                ep_num = []
                for z in range(len(ep)):
                    ep_num.append(re.sub('[^0-9]', '', ep[z]))
                num = 0;
                for z in range(len(ep_num), -1, -1):
                    try:
                        num = int(ep_num[z-1])
                        break
                    except:
                        pass
                for z in range(len(episode_ep)):
                    if(str(episode_ep[z]) == str(num)):
                        num = z
                    else:
                        pass
                link = ('http://appanimeplus.tk/api-animesbr-11.php?episodios='+y['video_id']+'&token=8.142435781128E13&r=25260.0')
                videos = requests.get(link, headers=headers_android)
                videos = json.loads(videos.content)
                bg = videos[0]['location']
                sd = videos[0]['locationsd']
                hd = videos[0]['locationhd']
                animejson = {
                    "Anime": str(_id),
                    "Episode": str(episode_ep[num]),
                    "Name": str(episode_title[num]),
                    "Duracao": str(episode_duration[num]),
                    "Data": str(episode_date[num]),
                    "Link_BG": str(bg),
                    "Link_SD": str(sd),
                    "Link_HD": str(hd)
                    }
                insertAnime = requests.post('http://localhost:7844/api/Episodes', json=animejson)
            print('\033[32m'+'Episódio adicionado'+'\033[0;0m')
            print("_____________________________________________")
        else:
            print('\033[31m'+'Episódio não adicionado'+'\033[0;0m')
            print("_____________________________________________")
            pass

GetAnime()
#search('subete ga f')




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
