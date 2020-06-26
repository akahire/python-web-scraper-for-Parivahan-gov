from io import BytesIO
from PIL import Image
from lxml import etree
import requests
import json
import sys

# pip install lxml
# pip install Pillow
# pip install requests


if len(sys.argv) != 3:
    raise Exception("Please specify DLno and Date_of_birth in following format\
        \n example:- python main.py DL-0420110149646 09-02-1976")

dlno = sys.argv[1]
dob = sys.argv[2]


print(dlno)
print(dob)
print('please enter the captcha, image will open in your default image viewer')


# pure


def get_url(url):
    return requests.get(url)


try:
    main_page = get_url('https://parivahan.gov.in/rcdlstatus/?pur_cd=101')
except:
    raise Exception(
        "error while GET request, check your internet connection or url")


jsession = main_page.cookies.get_dict().get('JSESSIONID')


def get_state(page):
    html = page.content
    dom = etree.HTML(html)
    return dom.xpath('//*[@id="j_id1:javax.faces.ViewState:0"]/@value')[0]


try:
    state = get_state(main_page)
except:
    raise Exception("Error while xpath, in 'get_state'")


def get_captcha(session_id):
    cookies = {
        'JSESSIONID': session_id
    }

    headers = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'image',
        'Referer': f"https://parivahan.gov.in/rcdlstatus/vahan/rcDlHome.xhtml;jsessionid=${session_id}",
        'Accept-Language': 'en-US,en;q=0.9',
    }

    params = (
        ('txtp_cd', '1'),
        ('bkgp_cd', '2'),
        ('noise_cd', '2'),
        ('gimp_cd', '3'),
        ('txtp_length', '5'),
        ('pfdrid_c', ['true?-1454719241', 'true']),
    )

    captcha_img = requests.get('https://parivahan.gov.in/rcdlstatus/DispplayCaptcha',
                               headers=headers, params=params, cookies=cookies)

    # opening image
    img = Image.open(BytesIO(captcha_img.content))
    img.show()
    captcha_img_name = 'captcha_img_data.png'

    try:
        img.save(captcha_img_name)
        print('if you cant view the captcha img, it is saved as ', captcha_img_name)
    except:
        print("can't save the image")

    print("Enter 5 Character Captcha: ", end='')
    my_captcha = input()
    return my_captcha


captcha = get_captcha(jsession)


def send_post(session_id, licence_number, birth_date, user_state, captcha_val):
    cookies = {
        'JSESSIONID': session_id,
        'has_js': '1',
    }

    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Faces-Request': 'partial/ajax',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://parivahan.gov.in',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://parivahan.gov.in/rcdlstatus/?pur_cd=101',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    data = {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'form_rcdl:j_idt43',
        'javax.faces.partial.execute': '@all',
        'javax.faces.partial.render': 'form_rcdl:pnl_show form_rcdl:pg_show form_rcdl:rcdl_pnl',
        'form_rcdl:j_idt43': 'form_rcdl:j_idt43',
        'form_rcdl': 'form_rcdl',
        'form_rcdl:tf_dlNO': licence_number,
        'form_rcdl:tf_dob_input': birth_date,
        'form_rcdl:j_idt32:CaptchaID': captcha_val,
        'javax.faces.ViewState': user_state
    }

    response = requests.post('https://parivahan.gov.in/rcdlstatus/vahan/rcDlHome.xhtml',
                             headers=headers, cookies=cookies, data=data)
    return response


post_response = send_post(jsession, dlno, dob, state, captcha)


def to_json(html_data):

    html = html_data.content
    dom = etree.HTML(html)
    div = dom.xpath('//*[@id="form_rcdl:j_idt124"]')[0]

    current_status = 'None'
    try:
        current_status = div.xpath('.//table[1]/tr[1]/td[2]/span/text()')[0]
    except:
        print('cant find Current status, parsing error')

    holder_name = 'None'
    try:
        holder_name = dom.xpath('.//table[1]/tr[2]/td[2]/text()')[0]
    except:
        print('cant find holder_name, parsing error')

    date_of_issue = 'None'
    try:
        date_of_issue = dom.xpath('.//table[1]/tr[3]/td[2]/text()')[0]
    except:
        print('cant find date_of_issue, parsing error')

    last_transaction_date = 'None'
    try:
        last_transaction_date = dom.xpath('.//table[1]/tr[4]/td[2]/text()')[0]
    except:
        print('cant find last_transaction_date, parsing error')

    old_new_dl_no = 'None'
    try:
        old_new_dl_no = dom.xpath('.//table[1]/tr[5]/td[2]/text()')[0]
    except:
        print('cant find old_new_dl_no, parsing error')

    non_transport_from = 'None'
    try:
        non_transport_from = dom.xpath('.//table[2]/tr[1]/td[2]/text()')[0]
    except:
        print('cant find non_transport_from, parsing error')

    non_transport_to = 'None'
    try:
        non_transport_to = dom.xpath('.//table[2]/tr[1]/td[3]/text()')[0]
    except:
        print('cant find non_transport_to, parsing error')

    transport_from = 'None'
    try:
        transport_from = dom.xpath('.//table[2]/tr[2]/td[2]/text()')[0]
    except:
        print('cant find transport_from, parsing error')

    transport_to = 'None'
    try:
        transport_to = dom.xpath('.//table[2]/tr[2]/td[3]/text()')[0]
    except:
        print('cant find transport_to, parsing error')

    hazardous_valid_till = 'None'
    try:
        hazardous_valid_till = dom.xpath('.//table[3]/tr/td[2]/text()')[0]
    except:
        print('cant find hazardous_valid_till, parsing error')

    hill_valid_till = 'None'
    try:
        hill_valid_till = dom.xpath('.//table[3]/tr/td[4]/text()')[0]
    except:
        print('cant find hill_valid_till, parsing error')

    table_data = []
    try:
        table = dom.xpath('//*[@id="form_rcdl:j_idt187_data"]')[0]
        for row in table.xpath('.//tr'):

            cov_category = row.xpath('.//td[1]/text()')[0]
            class_of_vehicle = row.xpath('.//td[2]/text()')[0]
            cov_issue_date = row.xpath('.//td[3]/text()')[0]

            row_data = {'COV Category': cov_category,
                        'Class Of Vehicle': class_of_vehicle,
                        'COV Issue Date': cov_issue_date}
            table_data.append(row_data)
    except:
        print('error parsing Class Of Vehicle Details')

    data = {
        'Current Status': current_status,
        "Holder's Name": holder_name,
        'Date Of Issue': date_of_issue,
        'Last Transaction At': last_transaction_date,
        "Old / New DL No.": old_new_dl_no,
        'Non-Transport': {
            'from': non_transport_from,
            'to': non_transport_to
        },
        'Transport': {
            'from': transport_from,
            'to': transport_to
        },
        'Hazardous Valid Till': hazardous_valid_till,
        'Hill Valid Till': hill_valid_till,
        'Class Of Vehicle Details': table_data

    }

    return json.dumps(data)


try:
    output = to_json(post_response)
except:
    raise Exception(
        "Error while xpath, in 'to_json', captcha or other input might be wrong try again")

print(output)
