import requests
import bs4
import webbrowser
import os, os.path
import subprocess
from tabulate import tabulate

global prevSearch
prevSearch = None


def generateURL(name):
    nameList = name.split(" ")
    url = "https://kat.cr/usearch/"
    for i in nameList[0:len(nameList) - 1]:
        url += (i + "%20")
    url += nameList[-1] + "/"
    # print("\nURL: ",url)
    return url


def transposeList(List):
    newL = []
    for i in range(len(List[0])):
        newL += [[]]
    for L in List:
        for j in range(len(L)):
            newL[j] += [L[j]]
    return newL


def listResults(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
    except:
        return None

    txt = bs4.BeautifulSoup(res.text, "html.parser")
    Torrents = txt.select("a[data-download]")

    Names = ["TITLE", " "] + txt.select('a[class="cellMainLink"]')
    for i in range(2, len(Names)):
        Names[i] = Names[i].text
        if len(Names[i]) > 100:
            Names[i] = Names[i][:100 - len(Names[i])] + " . . ."

    Sizes = ["SIZE", " "] + txt.select('td[class^="nobr"]')  # starts with nobr
    for i in range(2, len(Sizes)):
        Sizes[i] = Sizes[i].text

    Seeders = ["SEEDS", " "] + txt.select('td[class^="green"]')  # starts with green
    for i in range(2, len(Seeders)):
        Seeders[i] = Seeders[i].text

    Leechers = ["LEECHES", " "] + txt.select('td[class*="lasttd"]')  # contains lasttd
    for i in range(2, len(Leechers)):
        Leechers[i] = Leechers[i].text

    Dates = ["DATE", " "] + txt.select('td[title]')
    for i in range(2, len(Dates)):
        Dates[i] = Dates[i].get("title")

    N = ["", ""]
    for i in range(2, len(Names)):
        N += [i - 1]

    result = [N, Names, Sizes, Seeders, Leechers, Dates, Torrents]

    return result


def displayComments(n, txt):
    n -= 1
    Comments = txt.select('a[class^="icommentjs"]')  # starts with icommentjs
    comment = Comments[n - 1]
    # print("https://kat.cr"+comment.get("href"))
    res = requests.get("https://kat.cr" + comment.get("href"))
    res.raise_for_status()
    txt = bs4.BeautifulSoup(res.text, "html.parser")
    cmntsAV = txt.select('div[class^="commentAVRate"]')  # starts with commentAVRate
    cmnts = txt.select('div[class*="topmarg5px"]')  # contains topmarg5px

    L = min(len(cmnts), len(cmntsAV))

    Num, Audio, Video, Cmnt = [], [], [], []
    for i in range(L):
        Num += [str(i + 1) + "."]
        if len(cmntsAV[i].select('span')) == 2:
            Audio += [cmntsAV[i].select('span')[0].text]
            Video += [cmntsAV[i].select('span')[1].text]
        Cmnt += [cmnts[i].text]
        if len(Cmnt[i]) > 100:
            Cmnt[i] = Cmnt[i][:100]
    L = max(len(Audio), len(Video), len(Cmnt))
    Audio = Audio + [[" "]] * (L - len(Audio))
    Video = Video + [[" "]] * (L - len(Video))
    Cmnt = Cmnt + [[" "]] * (L - len(Cmnt))
    fullComments = [Num, Audio, Video, Cmnt]
    if (len(transposeList(fullComments)) == 0):
        print("   NO COMMENTS.")
    else:
        print("\nCOMMENTS ON TORRENT", n + 1, "\n")
        print(tabulate(transposeList(fullComments)))
    print("\n")


def click_on_file(filename):
    try:
        os.startfile(filename)
    except AttributeError:
        subprocess.call(['open', filename])


def mainRec(query):
    global prevSearch

    name = ""
    if query == None:
        name = input("TYPE 'P' AND PRESS ENTER TO REPEAT PREVIOUS SEARCH. \n\nEnter query: ")
    else:
        name = query

    if name in ["p", "P"]:
        if prevSearch == None:
            print("\n Previous search unavailable.\n")
            mainRec(None)
        else:
            print("REPEATING PREVIOUS SEARCH.\n")
            mainRec(prevSearch)

    prevSearch = name
    results = listResults(generateURL(name))
    if results == None:
        print("\nNO RESULTS FOUND.\n\nNEW SEARCH\n")
        mainRec(None)

    k = results[0]
    r = results[6]

    print("\nRESULTS\n", tabulate(transposeList(results[:-1])))
    print("\nPRESS ENTER TO MODIFY SEARCH.")
    print("TYPE <NUMBER> AND PRESS ENTER TO DOWNLOAD A TORRENT FILE.")
    print("TYPE 'C <NUMBER>' AND PRESS ENTER FOR COMMENTS.\n")

    n = len(k) + 2
    while n > len(k) + 1:
        n = (input("Enter choice: "))

        if n.split(" ")[0] == "c" or n.split(" ")[0] == "C":
            # print("T1")
            if len(n.split(" ")) == 2 and n.split(" ")[1].isdigit() == True and int(n.split(" ")[1]) < len(k) + 2:
                # print("T2")
                res = requests.get(generateURL(name))
                res.raise_for_status()
                txt = bs4.BeautifulSoup(res.text, "html.parser")
                displayComments(int(n.split(" ")[1]), txt)
                n = len(k) + 2
            n = len(k) + 2
        elif n.isdigit() == False:
            print("\n" + "#" * 100 + "\n\nNEW SEARCH\n")
            mainRec(None)
        else:
            n = int(n)

    print("Download in progress...")

    webbrowser.open("http:" + r[n - 1].get("href"))

    print("Torrent file downloaded.")

    '''
    os.chdir("C:\\Users\\Lord Daniel\\Downloads")
    time.sleep(5)
    latestFile = os.listdir()[0]
    for f in os.listdir():
         if time.ctime(os.path.getmtime(f)) > time.ctime(os.path.getmtime(latestFile)):
              latestFile = f
    os.rename(latestFile, "_".join(name.split(" "))+".torrent")
    click_on_file("_".join(name.split(" "))+".torrent")
    '''
    print("\n" + "#" * 100 + "\n\nNEW SEARCH\n")
    mainRec(None)


def main():
    print("WELCOME TO DANIEL'S TORRENT FINDER\n")
    try:
        mainRec(None)
    except:
        print("\nERROR\n" + "#" * 100 + "\n\nNEW SEARCH\n")
        mainRec(None)


main()

