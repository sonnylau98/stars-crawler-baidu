import re
import os
import requests
from graphviz import Digraph
from bs4 import BeautifulSoup

def Crawl(url):
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    req=requests.get(url,headers=headers)
    return req

def BS4(req):
    soup=BeautifulSoup(req.text,"html.parser")
    return soup

def InformationOfFriends(soup):
    raw_taglist=soup.body.find_all('div',attrs={'class':'name','title':re.compile("\w*")})
    taglist=[]
    dic={}
    for i in range(len(raw_taglist)):
        if len(raw_taglist[i])==2:
            taglist.append(raw_taglist[i])
    for j in range(len(taglist)):
        information_of_friend=[]
        information_of_friend.append(taglist[j].contents[0])
        information_of_friend.append("https://baike.baidu.com"+taglist[j].parent.attrs['href'])
        information_of_friend.append(taglist[j].previous_sibling.previous_sibling.attrs['src'])
        dic[taglist[j].contents[1].string]=information_of_friend
    return dic

def SaveTheText(soup,name):
    array=soup.body.find_all('div',attrs={'class':"lemma-summary",'label-module':"lemmaSummary"})
    string=array[0].text
    name_of_file=".\\texts\\"+name+".txt"
    with open(name_of_file,'w',encoding='utf-8') as f:
        f.write(string)
        
def SaveTheImage(soup,name):
    array=soup.body.find_all('img',attrs={'src':re.compile("https://bkimg.cdn.bcebos.com/pic/.*/resize,m_lfit,w_268,limit_1/format,f_jpg")})
    if (array==[]):
        url="https://baike.baidu.com/static/lemma/view3/img/guanxi-default.png"
    else:
        url=array[0].attrs['src']
    date_of_image=requests.get(url)
    name_of_image=".\\images\\"+name+".jpg"
    with open(name_of_image,'wb') as f:
        f.write(date_of_image.content)

def SaveTheImage2(dic):
    for key,value in dic.items():
        url=value[2]
        date_of_image=requests.get(url)
        name_of_image=".\\images\\"+key+".jpg"
        with open(name_of_image,'wb') as f:
            f.write(date_of_image.content)
        
def Graphing(name,dic,dot):
    dot.node(name=name+"文档",color='blue',fontname="FangSong",URL=".//texts//"+name+".txt",shape="diamond")
    dot.node(name=name+"图片",color='green',fontname="FangSong",URL=".//images//"+name+".jpg",shape="egg")
    dot.edge(name,name+"文档")
    dot.edge(name,name+"图片")
    for key,value in dic.items():
        dot.node(name=key,color='red',fontname="FangSong",shape="box")
        dot.edge(name,key,value[0])

def Function(dic,count,names):
    if (count==0):
	    return 0
    SaveTheImage2(dic)
    count=count-1    
    for key,value in dic.items():
        if (key in names):
            continue
        iter_url=value[1]
        iter_soup=BS4(Crawl(iter_url))
        iter_name=key
        iter_dic=dic=InformationOfFriends(iter_soup)
        SaveTheText(iter_soup,iter_name)        
        Graphing(iter_name,iter_dic,dot)
        names.add(key)
        Function(iter_dic,count,names)
    return 1

if __name__=="__main__":
    names={0}
    url=input("请输入人物的百度百科URL：")
    count=int(input("请输入迭代次数："))
    soup=BS4(Crawl(url))
    titles=soup.body.find_all('h1')
    main_name=titles[0].string
    if not os.path.exists("texts"):
        os.mkdir("texts")
    if not os.path.exists("images"):
        os.mkdir("images")
    dic=InformationOfFriends(soup)
    SaveTheText(soup,main_name)    
    SaveTheImage(soup,main_name)
    SaveTheImage2(dic)
    dot=Digraph("Graph"+main_name,format="svg")
    dot.node(name=main_name,color='red',fontname="FangSong",shape="box")
    Graphing(main_name,dic,dot)
    names.add(main_name)
    Function(dic,count,names)
    dot.view()
