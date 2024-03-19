import os

from selenium.webdriver.firefox.service import Service
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import pyautogui

# URL of the webpage
url = 'https://login.canvas.cornell.edu/'

# Time delay between each action (adjust as needed)
dt_typing = .1
dt_other = 1
dt_pause = 5

'''
RETURNS array of tuples of len 2 with the instructions associated with the login sequence
'''
#TODO authentication can be set to manual / not google hello
def processLogin(user, pas, auth):
    actions = [("Mleft", "/html/body/div[3]/main/div/article/section/div[1]/p[1]/a")]
    for letter in user:
        actions.append((str(letter),str(letter)))
    actions.append(("Special key pressed: Key.tab", Keys.TAB))
    actions.append(("Special key pressed: Key.shift", Keys.SHIFT))
    for letter in pas:
        actions.append((str(letter), str(letter)))
    actions.append(("Special key pressed: Key.enter", Keys.ENTER))
    actions.append(("pause", "pauto"))
    for letter in auth:
        actions.append((str(letter), str(letter)))
    actions.append(("pause", "pauto"))
    actions.append(("Mouse button Button.left pressed at (9, 649)", '//button[@id="trust-browser-button"]'))
    return actions


def processFile(filepath):
    if not os.path.exists(filepath):
        file1 = open('loginseq', 'w')
        file1.writelines(["User:\n","Pass:\n","Auth:\n"])
        raise Exception("Login file loginseq.txt not filled out")
    file1 = open(filepath, 'r')
    Lines = file1.readlines()
    user = ""
    password = ""
    auth = ""
    for line in Lines:
        if len(line) > 5 and line[:5].lower() == "user:":
            user = line[5:]
        elif len(line) > 5 and line[:5].lower() == "pass:":
            password = line[5:]
        elif len(line) > 5 and line[:5].lower() == "auth:":
            auth = line[5:]
    if user == "" or password == "" or auth == "":
        raise Exception("Failure in reading login from loginseq.txt")
    return processLogin(user, password, auth)

def log_in(loginactions, driver):
    """
    Peforms the log-in procedure with the credentials from loginactions and on the webdriver driver
    RETURNS nothing
    """
    pauto = False  # pyauto mode for windows security'
    for action, key in loginactions:
        print(action)
        if action == "pause":
            time.sleep(dt_pause)
            if key == "pauto":
                pauto = True
            elif key == "pautooff":
                pauto = False
        elif isinstance(key, str) and key[0] != '/':
            if pauto:
                pyautogui.press(key)
            else:
                driver.switch_to.active_element.send_keys(key)
                time.sleep(dt_typing)
        else:
            try:
                ActionChains(driver).move_to_element(driver.find_elements(By.XPATH,key)[0]).click().perform()
                ActionChains(driver).release().perform()
            except:
                print("Failure to control mouse")
            # Perform mouse button up at coordinates
            time.sleep(dt_other)


def grabGradescope(driver):
    """
    Should be a set of functions that BOTH begin and end at the canvas home page
    Should return a list of tuples formatted ((Course, Assignment Name [], Due Date []), (...), ...), where
    corresponding indices between name and date lists match
    """
    gradeHome = "https://www.gradescope.com/"

    course_with_gscope = "https://canvas.cornell.edu/courses/60088"
    driver.get(course_with_gscope)
    apps = driver.find_element(By.XPATH,"//ul[contains(@id, 'section-tabs')]")

    fails = 0
    for button in apps.find_elements(By.XPATH, ".//*"):
        try:
            if str(button.text) == "Gradescope":
                ActionChains(driver).move_to_element(button).click().perform()
                break
        except:
            fails += 1
    # print("Failures: " + str(fails))
    time.sleep(4)
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    driver.get(gradeHome)

    elems = driver.find_element(By.XPATH,'//*[@id="account-show"]/div/div[2]')
    listofelems = elems.find_elements(By.CLASS_NAME, "courseBox")
    j = 0
    output = []
    for k in range(len(listofelems)-1):
        # print(listofelems)
        ActionChains(driver).move_to_element(listofelems[j]).click().perform()
        time.sleep(3)
        course = str(driver.find_element(By.XPATH,'//*[@id="main-content"]/div[2]/div/header/div[1]/h1').text)
        # print(course)
        table = driver.find_element(By.XPATH,'//*[@id="assignments-student-table"]/tbody')
        set = (course,[],[])
        for asmt in table.find_elements(By.TAG_NAME, "tr"):
            name = ""
            submission_status = ""
            due_date = ""
            i = 0
            validAssignments = 0
            done = False
            temp1 = asmt.find_elements(By.TAG_NAME, "th")
            temp2 = asmt.find_elements(By.TAG_NAME, "td")
            lis = [temp1[0],temp2[0],temp2[1]]
            for data in lis:
                if i == 0:
                    # All homework due is a button for the name
                    namesFound = data.find_elements(By.TAG_NAME,"button")
                    if len(namesFound) == 0:
                        name = "Assignment not due"
                        done = True
                        i += 999
                    else:
                        name = str(namesFound[0].text)
                elif i == 1:
                    # Not really used because assignments that are a button => due, not button => not due (as far as ik...)
                    elem = data.find_element(By.CLASS_NAME,"submissionStatus--text")
                    submission_status = str(elem.text)
                elif i == 2:
                    elems = data.find_elements(By.CLASS_NAME,"submissionTimeChart--dueDate") # <- Should have a size of 2
                    due_date = str(elems[0].get_attribute("datetime"))
                else:
                    break
                i+=1
            if done:
                break
            else:
                set[1].append(name)
                set[2].append(due_date)

        if len(set[1]) > 0:
            output.append(set)
        driver.get(gradeHome)
        time.sleep(2)
        listofelems = driver.find_element(By.XPATH,'//*[@id="account-show"]/div/div[2]').find_elements(By.CLASS_NAME, "courseBox")
        j += 1


    print("Assignments finalized")
    print(output)
    driver.get("https://canvas.cornell.edu/courses")
    return output


def grabAssignmentsTab(driver):
    # TODO
    raise Exception("Unsupported Operation")


def main():
    # Initialize the Firefox webdriver
    webdriver_path = "C:/Users/kevin/Downloads/geckodrive/geckodriver.exe"
    service = Service(executable_path=webdriver_path)
    driver = webdriver.Firefox(service=service)
    driver.maximize_window()  # Maximize the window to fullscreen

    # Open the webpage
    driver.get(url)

    loginactions = processFile("loginseq")
    log_in(loginactions, driver)

    while "duosecurity.com" in driver.current_url:
        print("waiting")
        time.sleep(2)
    out = grabGradescope(driver)
    return out
    # driver.quit()?


if __name__ == "__main__":
    main()