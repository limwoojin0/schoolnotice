from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont
import time
import requests
import json
import random
from comcigan import School
import datetime

key = "나이스api 키"
school_code = "행정표준코드"
sc_name = "학교이름"
insta_id = "인스타그램아이디"
insta_pw = "인스타그램비밀번호"

pdate = ""
mdate = ""


def draw(content="오류", date="", mode="story"):
    if mode == "story":
        size = (50, 100)
        title = f"{date} 급식"
        name = "save_meal.jpg"
    else:
        size = (50, 50)
        title = "행사 알림"
        name = "save_party.jpg"
    target_img = Image.open("bg.jpg")
    out_img = ImageDraw.Draw(target_img)
    out_img.text(
        xy=size,
        text=title,
        fill=(255, 255, 255),
        font=ImageFont.truetype(font="GmarketSansTTFMedium.ttf", size=90),
    )
    out_img.text(
        xy=tuple(sum(elem) for elem in zip(size, (0, 120))),
        text=content,
        fill=(255, 255, 255),
        font=ImageFont.truetype(font="GmarketSansTTFMedium.ttf", size=50),
    )
    target_img.save(name)


def get_meal():
    date = str(
        (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%y%m%d")
    )
    meal_params = {
        "KEY": key,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": "B10",
        "SD_SCHUL_CODE": school_code,
        "MLSV_YMD": date,
    }
    meal_url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    try:
        response = (json.loads(requests.get(meal_url, params=meal_params).text))[
            "mealServiceDietInfo"
        ]
        if response[0]["head"][0]["list_total_count"] == 1:
            response = response[1]["row"][0]
        else:
            response = response[1]["row"]
        string = response["DDISH_NM"].replace("<br/>", "\n") + "\n\n"
        characters = "1234567890./-*[]+()"
        for x in range(len(characters)):
            string = string.replace(characters[x], "")
        return string
    except:
        return "급식이 없습니다\n\n"


def get_party(mode="all"):
    if mode == "all":
        date = time.strftime("%y%m")
    else:
        date = str(
            (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%y%m%d")
        )
    party_params = {
        "KEY": key,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": "B10",
        "SD_SCHUL_CODE": school_code,
        "AA_YMD": date,
    }
    party_url = "https://open.neis.go.kr/hub/SchoolSchedule"
    try:
        response = (json.loads(requests.get(party_url, params=party_params).text))[
            "SchoolSchedule"
        ][1]["row"]
        party_string = ""
        for i in response:
            date = f"{i['AA_YMD'][4:6]}월 {i['AA_YMD'][6:8]}일 "
            party_string += date + i["EVENT_NM"] + "\n"
        return party_string
    except:
        return "행사가 없습니다"


def time_table():
    try:
        myschool = School(sc_name)
    except:
        myschool = School(sc_name[:-2])
    date = time.localtime().tm_wday
    if date == 6:
        date = -1
    for i in range(3):
        content = []
        for j in range(9):
            b = f"{j+1}반\n"
            for f in range(len(myschool[i + 1][j + 1][date + 1])):
                b = b + myschool[i + 1][j + 1][date + 1][f][0] + "\n"
            if len(myschool[i + 1][j + 1][date + 1]) == 0:
                b += "시간\n표가\n없습\n니다."
            content.append(b)
        size = (40, 100)
        date1 = datetime.datetime.now() + datetime.timedelta(days=1)
        title = f"{date1.month}월 {int(date1.day)}일 {i+1}학년 시간표"
        target_img = Image.open("bg.jpg")
        out_img = ImageDraw.Draw(target_img)
        out_img.text(
            xy=size,
            text=title,
            fill=(255, 255, 255),
            font=ImageFont.truetype(font="GmarketSansTTFMedium.ttf", size=70),
        )
        for l in content:
            if content.index(l) < 4:
                c_size = (
                    (content.index(l) + 1) * 95 + (content.index(l) - 1) * 95,
                    100,
                )
            else:
                c_size = (
                    (content.index(l) - 3) * 75 + (content.index(l) - 5) * 75,
                    500,
                )
            out_img.text(
                xy=tuple(sum(elem) for elem in zip(size, c_size)),
                text=l,
                fill=(255, 255, 255),
                font=ImageFont.truetype(font="GmarketSansTTFMedium.ttf", size=50),
            )
        target_img.save(f"time_table{i+1}.jpg")


print("start")

while True:
    if ((time.localtime().tm_hour == 21) or (time.localtime().tm_hour == 22)) and (
        mdate != time.strftime("%y%m%d")
    ):
        pdata = get_party("today")
        data = f"{get_meal()}\n{pdata}"
        date = datetime.datetime.now() + datetime.timedelta(days=1)
        date = f"{date.month}월 {int(date.day)}일"
        draw(data, date, "story")
        time_table()
        client = Client()
        client.login(insta_id, insta_pw)
        print("logined")
        time.sleep(random.uniform(5.0, 7.0))
        client.photo_upload_to_story(path="save_meal.jpg")
        for i in range(3):
            time.sleep(random.uniform(5.0, 9.0))
            client.photo_upload_to_story(path=f"time_table{i+1}.jpg")
        print("finished story")
        mdate = time.strftime("%y%m%d")
        client.logout()
        print("logout")

    if (time.localtime().tm_mday == 1) and (pdate != time.strftime("%y%m%d")):
        data = get_party()
        draw(data, "", "post")
        client = Client()
        client.login(insta_id, insta_pw)
        print("logined")
        time.sleep(random.uniform(5.0, 7.0))
        client.photo_upload(path="save_party.jpg", caption="행사 알림")
        print("finished post")
        pdate = time.strftime("%y%m%d")
        client.logout()
        print("logout")

    if time.localtime().tm_hour == 3:
        pdate, mdate = "", ""
    time.sleep(60)
