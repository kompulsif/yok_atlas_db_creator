from selenium import webdriver
from time import sleep
from argparse import ArgumentParser
from sqlite3 import connect
from os import path, name as osName, system


def data_spliter(unis):

    for i in unis:

        x = i.text.splitlines()
        id = x[0]
        name = x[3].strip()

        if ("Yüksekokulu" in x[4]):
            s = x[4].split("Yüksekokulu ", 1)
            vocational = s[0] + "Yüksekokulu"
            department = s[1]

        elif ("Fakültesi" in x[4]):
            s = x[4].split("Fakültesi ", 1)
            vocational = s[0] + "Fakültesi"
            department = s[1]

        else:
            raise ValueError(f"Error! = {x[4]}")

        city, u_type, pay, t_type = x[5].replace(
            "İndirimli ", "").rsplit(" ", 4)[-4:]

        u_type_values = ("Vakıf", "Devlet", "KKTC", "Yabancı", "Yurtdışı")

        pay_values = ("%25", "%50", "%75", "Burslu", "Ücretsiz", "Ücretli",
                      "AÖ-Ücretli", "İÖ-Ücretli", "UE-Ücretli", "UÖ-Ücretli")

        t_type_values = ("Açıköğretim", "Uzaktan", "Örgün", "İkinci")

        if (city.strip() == "Vakıf") or (u_type not in u_type_values) or \
                (pay not in pay_values) or (t_type not in t_type_values):
            print(f"{x}   data has error, please let me know.")
            quit()

        point = x[10].replace(",", ".")
        rank = x[12].replace(".", "")

        university_datas[id] = (name, vocational, department,
                                city, u_type, pay, t_type, point, rank)


def database_creator(d_path):

    database = connect(d_path)
    dCursor = database.cursor()

    dCursor.execute("""
    CREATE TABLE UniversityDatas(
        uniID TEXT,
        name TEXT,
        vocational TEXT,
        department TEXT,
        city TEXT,
        uniType TEXT,
        pay TEXT,
        teachType TEXT,
        point TEXT,
        rank INT
    )
                    """)

    for u_id, data in university_datas.items():

        data = (u_id, ) + data
        dCursor.execute(
            "INSERT INTO UniversityDatas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)

    database.commit()
    database.close()


def find_and_next():

    while True:

        try:
            university_informations = browser.find_elements_by_css_selector(
                '#mydata > tbody > tr')

            if (len(university_informations) == 0):
                raise ValueError

            browser.find_element_by_css_selector('#mydata_next > a').click()
            sleep(0.3)
            data_spliter(university_informations)

        except:

            print(
                "\n\nAn error has been caught. Please check your internet connection!\n")

            if (error_handling):
                return True

            sleep(2)
            return None

        else:
            return None


def getArguments():

    parser = ArgumentParser()
    parser.add_argument("--driver", help="Browser Driver Path")
    parser.add_argument("--cooldown", help="Cooldown, default 3")
    parser.add_argument("--database", help="Database Name/Path")
    parser.add_argument(
        "--quit", help="Give 1 if you want to exit when an error occurs")
    return parser.parse_args()


def progressBar(iterable, prefix='', suffix=''):

    decimals = 1
    printEnd = "\r"
    length = 100
    total = len(iterable)
    fill = '█'

    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                         (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)

    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)

    print()


def clear_terminal():

    if (osName == "nt"):
        system("cls")

    else:
        system("clear")


if __name__ == '__main__':

    args = getArguments()

    if (args.driver) and (args.database):

        if (args.cooldown):

            if (args.cooldown.isnumeric()):
                cooldown = abs(int(args.cooldown))

            elif ((args.cooldown.count(".") == 1) and
                  (args.cooldown.replace(".", "").isnumeric())):

                cooldown = abs(float(args.cooldown))

            else:
                print("\n[!]-> Invalid cooldown parameter! <-[!]\n")
                quit()

        else:
            cooldown = 3

        print(f"\n[*]-> Cooldown set to {cooldown} <-[*]\n")

        error_handling = True if (args.quit == "1") else False

        try:
            browser = webdriver.Chrome(args.driver)
            browser.get(
                "https://yokatlas.yok.gov.tr/tercih-sihirbazi-t3-tablo.php?p=tyt")

            sleep(4)

            browser.maximize_window()

            sleep(1)

            browser.execute_script(
                'document.getElementById("top-link-block").remove();')

            university_datas = {}

            last_page_number = int(
                browser.find_element_by_css_selector(
                    '#mydata_paginate > ul > li:nth-child(8) > a').text) + 1

            clear_terminal()

            print("\nSTARTED!\n")

            for p in progressBar(list(range(1, last_page_number)), "Progress", "Complete"):

                if (find_and_next()):
                    break

                sleep(cooldown)

            database_creator(args.database)

        except KeyboardInterrupt:
            print("CTRL + C detected!")
            quit()

    else:
        print("\n[!]-> Missing parameter! <-[!]\n")
