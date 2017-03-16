# -*- coding: utf-8 -*-
import sys
sys.path.append('/Library/Python/2.7/site-packages')
from lxml import html
import dryscrape
import time
import urllib.request
import urllib.parse
import requests
import os
import shelve
import atexit

def download_file(download_url,stack):
    urlDecoded=urllib.parse.unquote(download_url)
    file_name = urlDecoded.split("/")[-1] #nome do arquivo avulso
    tree = "/".join(str(x) for x in stack) #diretorio
    tree1 = tree.replace("/1", "")
    tree2 = tree1.replace("/2", "") #removem indicadores de semetre
    print (tree2)
    file_name_final = (tree2 + "/" + file_name) #diretorio + nome do arquivo
    final=urllib.parse.unquote(file_name_final) # encodado acabei de remover
    if not os.path.exists(tree2):
        os.makedirs(tree2) #cria o diretorio se necessario
    if not os.path.exists(final) and file_name_final and file_name.endswith (extensions) and not file_name.startswith ("PNAD"):
        r = session_requests.get(download_url, stream=True)
        with open(final, 'wb') as fd:
            for chunk in r.iter_content(2000):
                fd.write(chunk)
    return

def prepareUrl(url): #prepara a URL para ser acessada
    if url.startswith("this"):
        url4 = url[11:-1]
        url = url4
    url1 = url.strip()
    newUrl = "https://insper.blackboard.com" + url1
    newUrl.strip()
    return newUrl

def exit_handler(): #executa quando script é interrompido, salva urls intermediarias no DB
    sh=shelve.open('/tmp/shelve.tmp')
    sh['urls']=urls
    sh.close()
    print (urls)

#setar login e senha como string
login = input("Digite seu usuário do Blackoard: ")
senha = input("Digite sua senha do Blackoard: ")


payload = {
	"user_id": login,
	"password": senha,
	"action": "login"
}

fileSystem = [] #stack para as materias e pastas

#cria o DB
if not os.path.exists("/tmp/shelve.tmp.db"):
    sh=shelve.open('/tmp/shelve.tmp')  # Retrieve set from file
    urlsJaVisitadas=[]
    urls=[] #tmp database para nao processar o mesmo arquivo repetidamente
    sh['urls']=urlsJaVisitadas
    sh.close()

#carrega as URLS ja acessadas do DB
else:
    sh=shelve.open('/tmp/shelve.tmp')
    urlsJaVisitadas=sh['urls']
    urls=sh['urls'] #tmp database para nao processar o mesmo arquivo repetidamente
    sh.close()

print (urlsJaVisitadas)

#inicia sessão do requests para acessar paginas simples
session_requests = requests.session()
login_url = "https://insper.blackboard.com/webapps/login/"
result = session_requests.get(login_url)
result = session_requests.post(
	login_url,
	data = payload,
	headers = dict(referer=login_url)
)

#extensoes que queremos baixar e nome de pastas desnecessarios (lado esquerdo do BB)
extensions = (".pdf",".doc",".ppt",".dox",".xlsx",".pptx",".docx","ipynb")
tabIndesejaveis = ("Conteudo", "Conteúdos", "Avisos", "Notas", "Enviar", "Conte\xfados","Central de ajuda")

#inicia sessão do dryscrape para acessar pagina inicial c/ JavaScript
session = dryscrape.Session(base_url='https://insper.blackboard.com')
session.set_attribute('auto_load_images', False)
session.visit('/webapps/login/')
name = session.at_xpath('//*[@name="user_id"]')
name.set(login)
password = session.at_xpath('//*[@name="password"]')
password.set(senha)
name.form().submit()
session.visit("https://insper.blackboard.com/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_226_1")
session.set_error_tolerant(True)
session.set_attribute('auto_load_images', False)

#registra função para executar em caso de término preoce/manual do script
atexit.register(exit_handler)

time.sleep(5)

for curso in session.xpath("//div[@id='_26_1termCourses_noterm']/ul/li/a"): #pega todos os cursos e seus links
    url =  curso.get_attr("href")
    courseName = curso.text()
    print (courseName)
    if (courseName != None and courseName != "None"):
        name = urllib.parse.unquote(courseName)
        print (name)
        fileSystem.append(name)
        print (fileSystem)
    urlNew = prepareUrl(url)
    a = session_requests.get(urlNew)
    tree = html.fromstring(a.content)
    print ("1")
    for contudo in tree.xpath("//*[@id='courseMenuPalette_contents']/li/a"): #procura pagina Conteudo (ou outras)
        url =  contudo.attrib.get("href")
        tab = contudo.find('span').text
        print (tab)
        if not any(s in tab for s in tabIndesejaveis):
            name = urllib.parse.unquote(tab)
            fileSystem.append(name)
        urlNew = prepareUrl(url)
        b = session_requests.get(urlNew)
        tree1 = html.fromstring(b.content)
        print ("2")
        for anexo in tree1.xpath("//*[@class='details']/div/p/a"): #procura arquivos na pagina
            url = anexo.attrib.get("href")
            print ("3")
            if url and not url.endswith("xid-1522183_2") and not url.endswith(".html") and url not in urlsJaVisitadas: #TODO: salvar links html separadamente:
                if url.startswith("%20"):
                    url = url [3:]
                if not url.startswith("https://proofwiki") and not url.startswith("mailto"):
                    url1=prepareUrl(url)
                    f = session_requests.get(url1)
                time.sleep(4)
                baixar = f.url
                download_file(baixar,fileSystem)
                urls.append(url)
        for anexo in tree1.xpath("//*[@class='details']/div/div[2]/ul/li/a"): #procura arquivos anexados na pagina
            url = anexo.attrib.get("href")
            print ("4")
            if url and not url.endswith("xid-1522183_2") and not url.endswith(".html") and url not in urlsJaVisitadas: #TODO: salvar links html separadamente:
                if url.startswith("%20"):
                    url = url [3:]
                url1=prepareUrl(url)
                f = session_requests.get(url1)
                time.sleep(4)
                baixar = f.url
                download_file(baixar,fileSystem)
                urls.append(url)
        for pasta in tree1.xpath("//*[@class='contentList']/li/div/h3/a"): #procura pastas dentro dos conteudos
            pastaNome = pasta.find('span').text
            url =  pasta.attrib.get("href")
            if (pastaNome != None and pastaNome != "None"):
                pasta = urllib.parse.unquote(pastaNome)
                fileSystem.append(pasta)
            urlNew = prepareUrl(url)
            c = session_requests.get(urlNew)
            tree2 = html.fromstring(c.content)
            print ("5")
            for anexo in tree2.xpath("//*[@class='details']/div/p/a"): #procura arquivos anexados
                ## print(html.tostring(anexo, pretty_# print=True))
                url = anexo.attrib.get("href")
                print ("6")
                if url and not url.endswith("xid-1522183_2") and not url.endswith(".html") and not url.endswith("book.pdf") and url not in urlsJaVisitadas: #TODO: salvar links html separadamente:
                    if url.startswith("%20"):
                        url = url [3:]
                    f = session_requests.get(url)
                    time.sleep(4)
                    baixar = f.url
                    download_file(baixar,fileSystem)
                    urls.append(url)
            if c.url.endswith (extensions):
                print ("opa")
                download_file(c.url, fileSystem)
                urls.append(c.url)
            for arquivo in tree2.xpath("//*[@class='contentList']/li/div/h3/a"): #procura arquivos dentro das pastas
                print ("7")
                for anexo in tree2.xpath("//*[@class='details']/div/p/a"): #procura arquivos anexados
                    url = anexo.attrib.get("href")
                    if url and not url.endswith("dip_gw_chap1_3.pdf") and not url.endswith("book.pdf") and url not in urlsJaVisitadas:
                        if url.startswith("%20"):
                            url = url [3:]
                        f = session_requests.get(url)
                        time.sleep(4)
                        baixar = f.url
                        download_file(baixar,fileSystem)
                        urls.append(url)
                        urls.append(f.url)
                url =  arquivo.attrib.get("onclick")
                if not url:
                    break
                urlNew = prepareUrl(url)
                d = session_requests.get(urlNew)
                tree3 = html.fromstring(d.content)
                for doc in tree3.xpath("//*[@id='PDFEmbedID']"): #extrai o link de download dos arquivos
                    print ("8")
                    url =  doc.attrib.get("src")
                    if url not in urlsJaVisitadas:
                        urlNew = prepareUrl(url)
                        e = session_requests.get(urlNew)
                        time.sleep(4)
                        baixar = e.url
                        download_file(baixar,fileSystem)
                        urls.append(url)
            fileSystem.pop()
    fileSystem.pop()
    print (urls)
    sh=shelve.open('/tmp/shelve.tmp')  # Dump set (as one unit) to shelve file
    sh['urls']=urls
    sh.close()
    if fileSystem:
        fileSystem = []
