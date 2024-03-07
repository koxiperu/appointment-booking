from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import http.client
import requests
from PIL import Image
import sys
driver = webdriver.Chrome()
driver.get("https://luxembourg.kdmid.ru/queue/orderinfo.aspx")

elem_n = driver.find_element(By.NAME, "ctl00$MainContent$txtID")
elem_n.clear()
elem_n.send_keys("44222")
elem_c = driver.find_element(By.NAME, "ctl00$MainContent$txtUniqueID")
elem_c.clear()
elem_c.send_keys("F3CBF7AD")
elem_p = driver.find_element(By.ID, "ctl00_MainContent_imgSecNum").get_attribute("src")
img_resp = requests.get(elem_p)
with open("captcha.png", "wb") as file:
    file.write(img_resp.content)
print("Image saved successfully.")




im = "captcha.png"
threshold=200
mask="letters.bmp"
alphabet="0123456789abcdef"

img = Image.open(im)
img = img.convert("RGB")
box = (8, 8, 58, 18)
img = img.crop(box)
pixdata = img.load()

# open the mask
letters = Image.open(mask)
ledata = letters.load()

def test_letter(img, letter):
    A = img.load()
    B = letter.load()
    mx = 1000000
    max_x = 0
    x = 0
    for x in range(img.size[0] - letter.size[0]):
        _sum = 0
        for i in range(letter.size[0]):
            for j in range(letter.size[1]):
                _sum = _sum + abs(A[x + i, j][0] - B[i, j][0])
        if _sum < mx:
            mx = _sum
            max_x = x
    return mx, max_x

# Clean the background noise, if color != white, then set to black.
for y in range(img.size[1]):
    for x in range(img.size[0]):
        if (pixdata[x, y][0] > threshold) \
                and (pixdata[x, y][1] > threshold) \
                and (pixdata[x, y][2] > threshold):

            pixdata[x, y] = (255, 255, 255, 255)
        else:
            pixdata[x, y] = (0, 0, 0, 255)

counter = 0
old_x = -1

letterlist = []

for x in range(letters.size[0]):
    black = True
    for y in range(letters.size[1]):
        if ledata[x, y][0] != 0:
            black = False
            break
    if black:
        box = (old_x + 1, 0, x, 10)
        letter = letters.crop(box)
        t = test_letter(img, letter)
        letterlist.append((t[0], alphabet[counter], t[1]))
        old_x = x
        counter += 1

box = (old_x + 1, 0, 140, 10)
letter = letters.crop(box)
t = test_letter(img, letter)
letterlist.append((t[0], alphabet[counter], t[1]))

t = sorted(letterlist)
t = t[0:6]  # 5-letter captcha

final = sorted(t, key=lambda e: e[2])

answer = ''.join(map(lambda l: l[1], final))
print(answer)
#assert "No results found." not in driver.page_source
driver.close()