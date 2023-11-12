import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import threading

def setup(url):
    if sys.version_info >= (3, 11, 0):
        driver = webdriver.Chrome()
    else:
        driver = webdriver.Chrome(executable_path="chromedriver.exe")
    driver.get("https://sv.haui.edu.vn")
    driver.maximize_window()
    username = driver.find_element(By.ID, ("ctl00_inpUserName"))
    password = driver.find_element(By.ID, ("ctl00_inpPassword"))
    login_btn = driver.find_element(By.ID, ("ctl00_butLogin"))
    username.send_keys("2021602643")
    password.send_keys("Phuong phuong1")
    sleep(10)
    login_btn.click()
    driver.get(url)
    return driver

def get_list(driver, str):
    ls1 = driver.find_elements(By.CLASS_NAME, ("kTableRow"))
    ls2 = driver.find_elements(By.CLASS_NAME, ("kTableAltRow"))
    ls = []
    links = []
    for i in range(len(ls1)):
        ls.append(ls1[i].text.split(' ', 2)[2].rsplit(' ', 1))
        ls.append(ls2[i].text.split(' ', 2)[2].rsplit(' ', 1))
    ls = ls[0:(len(ls)-8)]
    fullname = [i[0] for i in ls]
    df = pd.DataFrame(fullname, columns=['Họ và tên'])
    df['Lớp'] = str
    df['Lớp'].ffill(inplace=True)
    for i in range(len(ls1)):
        links.append(ls1[i].find_elements(By.CSS_SELECTOR, '[href]'))
        links.append(ls2[i].find_elements(By.CSS_SELECTOR, '[href]'))
    links = links[0:(len(links)-8)]
    links = [link[0].get_attribute('href') for link in links]
    return df, links, len(ls)

def get_info(driver, links, len_ls):
    total_credits = []
    gpa = []
    total_accumulated_credits = []
    classified = []
    xpath = '/html/body/div[1]/div[2]/div/form/div[3]/div[3]/div/div/div/div/div/div/table/tbody/tr'
    for i in range(len_ls):
        driver.get(links[i])
        sleep(2)
        num_rows = driver.find_elements(By.XPATH, (xpath))
        total_credits.append(driver.find_elements(By.XPATH, (f"{xpath}[{len(num_rows) - 1}]/td[1]/span"))[0].text)
        gpa.append(driver.find_elements(By.XPATH, (f"{xpath}[{len(num_rows) - 1}]/td[2]/span"))[0].text)
        total_accumulated_credits.append(driver.find_elements(By.XPATH, (f"{xpath}[{len(num_rows)}]/td[1]/span"))[0].text)
        classified.append(driver.find_elements(By.XPATH, (f"{xpath}[{len(num_rows)}]/td[2]/span"))[0].text)
    for i in range(len(total_credits)):
        total_credits[i] = total_credits[i].replace("Tổng số tín chỉ: ", "")
    for i in range(len(gpa)):
        gpa[i] = gpa[i].replace("Trung bình chung tích lũy: ", "")
    for i in range(len(total_accumulated_credits)):
        total_accumulated_credits[i] = total_accumulated_credits[i].replace("Tổng số tín chỉ tích lũy: ", "")
    for i in range(len(classified)):
        classified[i] = classified[i].replace("Xếp loại tốt nghiệp: ", "")
    data = {'Tổng số tín': total_credits,
            'GPA': gpa,
            'Tổng số tín tích lũy': total_accumulated_credits,
            'Loại': classified}

    df = pd.DataFrame(data)
    return df

def main(str, url):
    global result
    driver = setup(url=url)
    df_list, links, len_ls = get_list(driver=driver, str=str)
    df_info = get_info(driver=driver, links=links, len_ls=len_ls)
    df = pd.concat([df_list, df_info], axis=1)
    driver.quit()
    return df

if __name__ == "__main__":
    url_list = ["https://sv.haui.edu.vn/student/result/viewexamresultclass?id=168244&t=fdc0d272b071aae62ec5a39b2f2095125333c65e", #1
                "https://sv.haui.edu.vn/student/result/viewexamresultclass?id=168245&t=011325e244ea7fa04e4020daa26831615c59699c", #2
                "https://sv.haui.edu.vn/student/result/viewexamresultclass?id=168264&t=c6e0e7d0c9ee5d01ac37aa8ffa69efaed5f8e220", #3
                "https://sv.haui.edu.vn/student/result/viewexamresultclass?id=168265&t=6ed251d57e43904cdfaf5dde3124fb100499deae", #4
                "https://sv.haui.edu.vn/student/result/viewexamresultclass?id=168246&t=9bc4e6e29fed5832e4d263f1be0780f551e63af2", #5
                "https://sv.haui.edu.vn/student/result/viewexamresultclass?id=168247&t=bd5bd0730f45055b161d932a3eac2f35332b356d", #6
                "https://sv.haui.edu.vn/student/result/viewexamresultclass?id=168266&t=8cc05c1eea330157d30bf3d5801258bfd52db712"] #7
    for i in range(len(url_list)):
        main(f"CNTT{i+1}", url_list[i]).to_csv(f"output\\CNTT{i+1}.csv")