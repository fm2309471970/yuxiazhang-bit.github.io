import requests
import re
from bs4 import BeautifulSoup
import math


search_url = 'https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword='

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'
}

# cve_obj_list = []
# cve_all = []
# producer = ''
# software = 'mysql'
# banner = '5.7.21'

class CveObject:
    cve_no = ''                     # 漏洞编号
    cve_url = ''                    # 漏洞cve url链接地址
    # cve_nvd_url = ''                # 漏洞nvd url链接地址
    cve_description = ''            # 漏洞描述
    cve_create_time = ''            # 创建时间
    # cve_modify_time = ''            # 修改时间
    # cve_level = ''                  # 威胁等级
    # cve_score = ''                  # 威胁评分
    cve_cna = ''                    # 漏洞分配的机构

    def show(self):
        """
        Show basic vul information
        :return: None
        """
        print('----------------------------------')
        print('编号：', self.cve_no)
        print('漏洞地址：', self.cve_url)
        print('漏洞描述：', self.cve_description[:10])
        print('创建时间:', self.cve_create_time)
        # print('修改时间:', self.cve_modify_time)
        print('CNA:', self.cve_cna)
        # print('漏洞等级：', self.cve_level)
        # print('漏洞评分：', self.cve_score)
        print('\n\n')

def fill_with_cve(cve, cve_obj):
    """
    Fetch detailed information by search cve to fill cve_obj that can be fetch from CVE
    :param cve: cve no
    :param cve_obj: cve object to fill
    :return: None
    """

    # construct cve url
    cve_url = 'https://cve.mitre.org/cgi-bin/cvename.cgi?name='
    url = '{}{}'.format(cve_url, cve)
    # print(url)

    # fill cve obj with cve_no & cve_url
    cve_obj.cve_no = cve
    cve_obj.cve_url = url
    # print(cve_obj.cve_url)

    try:
        response = requests.get(url=url, timeout=15, headers=headers)
        soup = BeautifulSoup(response.text, features="lxml")

        # to get cve description or detail information
        result = soup.select('body > div#Page > div#CenterPane > div#GeneratedTable > table > tr')
        description = result[3].td.string
        cve_obj.cve_description = description

        # to get cve create time
        result = soup.select('body > div#Page > div#CenterPane > div#GeneratedTable > table > tr > td > b')
        time = result[1].string
        time = '{}-{}-{}'.format(time[:4], time[4:6], time[6:])
        # print('time...', time)

        # to get assgining cna
        result = soup.select('body > div#Page > div#CenterPane > div#GeneratedTable > table > tr')
        cna = result[8].td.string

        cve_obj.cve_create_time = time
        cve_obj.cve_cna = cna
    except Exception as e:
        print('something bad happen when searching cve...')
        print(f"发生异常: {e}")
    finally:
        pass
def fetch_all_cves(software,banner):
    """
    Query NVD to get specific version of software vulnerabilities
    :return: None
    """
    # contruct query string
    cve_all=[]
    producer=''
    if banner:
        keyword = '{}%3a{}'.format(software, banner)
    else:
        keyword = software
    url = 'https://nvd.nist.gov/vuln/search/results?form_type=Advanced&' \
          'cves=on&cpe_version=cpe%3a%2fa%3a{}%3a{}'.format(producer, keyword)
    # url = 'https://nvd.nist.gov/vuln/search/results?form_type=Advanced&' \
    #       'cves=on&cpe_version=cpe%3a%2fa%3a{}'.format(keyword)
    print(url)

    # to get cve number
    try:
        response = requests.get(url, timeout=60, headers=headers)
        if response.status_code == 200:
            num = re.findall('"vuln-matching-records-count">(.*)?</strong>', response.text)[0]
            msg = 'There are {} cves with {} {}...'.format(num, software, banner)
            print(msg)
    except:
        pass


    # fetch all cve no
    start_index = index = 0
    while start_index < int(num):
        url = 'https://nvd.nist.gov/vuln/search/results?form_type=Advanced&' \
              'cves=on&cpe_version=cpe%3a%2fa%3a{}%3a{}&' \
              'startIndex={}'.format(producer, keyword, start_index)
        msg = 'processing page {}/{}...'.format(index+1, math.ceil(int(num) / 20))
        print(msg)
        index += 1
        start_index = index * 20
        try:
            response = requests.get(url, timeout=60, headers=headers)
            if response.status_code == 200:
                cves = re.findall('"vuln-detail-link-\d+">(.*)?</a>', response.text)
                cve_all.extend(cves)
        except:
            pass
    print('\n-------- CVEs ---------\n')
    for line in cve_all:
        print(line)
    print()
    return cve_all
def fetch_vul_info(software,banner):

    # get all cves

    cve_all=fetch_all_cves(software,banner)
    cve_obj_list = []
    i = 0
    for cve in cve_all:
        i += 1
        cve_obj = CveObject()

        # if i == 4:
        #     break
        msg = '[{}/{}] Fetching {} ...'.format(i, cve_all.__len__(), cve)
        print(msg)
        # fill cve object with information from cve and nvd
        fill_with_cve(cve, cve_obj)
        # fill_with_nvd(cve, cve_obj)
        cve_obj_list.append(cve_obj)
    return cve_obj_list


# if __name__ == '__main__':
#     # use '+' to connect keyword, eg. mysql+5.7.21
#     fetch_vul_info()
#     print(cve_all)
#     print(cve_obj_list)
#     pass

def get_cve(pack,version):
    software=pack
    banner=version
    cve_obj_list=fetch_vul_info(software,banner)
    return cve_obj_list