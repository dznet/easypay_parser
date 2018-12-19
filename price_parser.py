import requests
from time import sleep
import lxml.html


API_KEY = 'a355337a93c7f217ede47c5dacc1f19b'  # Your 2captcha API KEY
site_key = '6LefhCUTAAAAAOQiMPYspmagWsoVyHyTBFyafCFb'  # always constant
url = 'https://partners.easypay.ua/auth/signin'
login = 'login'
password = 'password'
wallet_link = 'https://partners.easypay.ua/wallets/buildreport?walletId=906309&month=10&year=2018&orderBy=undefined'

#proxy = '127.0.0.1:6969'  # example proxy
#proxy = {'http': 'http://' + proxy, 'https': 'https://' + proxy}


def get_recaptcha_answer(s):
    # here we post site key to 2captcha to get captcha ID (and we parse it here too)

    #WITHOUT PROXY
    captcha_id = s.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key, url)).text.split('|')[1]

    # then we parse gresponse from 2captcha response

    #WITHOUT PROXY
    recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text

    print("solving ref captcha...")
    while 'CAPCHA_NOT_READY' in recaptcha_answer:
        sleep(5)
        # WITHOUT PROXY
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
    recaptcha_answer = recaptcha_answer.split('|')[1]

    return recaptcha_answer


s = requests.Session()
sign_page = s.get(url)

l_html = lxml.html.fromstring(sign_page.text)

RequestVerificationToken = l_html.xpath('//input[@name="__RequestVerificationToken"]/@value')[1]


payload = {
    'login': login,
    'password': password,
    '__RequestVerificationToken': RequestVerificationToken,
}

while True:
    try:
        response = s.post(url, payload)
        #print(response.text)
        l_html = lxml.html.fromstring(response.text)
        security_error = l_html.xpath('//script[contains(text(), "Ошибка проверки безопасности")]/text()')

        if security_error:
            print("Form consists captcha\nTry to sign in with captcha...")
            recaptcha_answer = get_recaptcha_answer(s)
            payload['gresponse'] = recaptcha_answer
            payload['g-recaptcha-response'] = recaptcha_answer
            response = s.post(url, payload)
        break
    except Exception as e:
        print(e)

# get price
data = list()
page = s.get(wallet_link)
l_html = lxml.html.fromstring(page.text)
prices = l_html.xpath('//table[@class="table-layout"]/tr/td[@align="right"][1]/text()')
dates = l_html.xpath('//table[@class="table-layout"]/tr/td[@align="center"][2]/text()')

prices = [price.split(",")[0] for price in prices]
dates = [".".join(reversed(date.replace(":", ".").split(" "))) for date in dates]

data = ["{}.{}".format(a, b) for a, b in zip(prices, dates)]

#return data
print(data)




