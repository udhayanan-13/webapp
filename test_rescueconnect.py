from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Browser setup
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

# Pause between actions
PAUSE = 0.3

passed = 0
failed = 0


def pause():
    time.sleep(PAUSE)


def report_test(test_name, action):
    global passed, failed

    print(f"\n{test_name}")

    try:
        action()
        pause()
        print(f"PASS: {test_name}")
        passed += 1
    except Exception as e:
        print(f"FAIL: {test_name}")
        print(f"Reason: {e}")
        failed += 1
        pause()


def find_visible_input(placeholder):
    elements = driver.find_elements(
        By.XPATH,
        f"//input[@placeholder='{placeholder}']"
    )

    for element in elements:
        if element.is_displayed() and element.is_enabled():
            return element

    raise Exception(f"Visible, enabled input not found: {placeholder}")


def test_application_open():
    driver.get("http://localhost:5500/frontend/index.html")
    driver.maximize_window()

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Username']")
        )
    )


def test_login_interface():
    assert find_visible_input("Username").is_displayed()
    pause()

    assert find_visible_input("Password").is_displayed()
    pause()

    buttons = driver.find_elements(
        By.XPATH, "//button[contains(normalize-space(), 'Login')]"
    )

    assert any(button.is_displayed() for button in buttons)


def test_login_usability():
    username = find_visible_input("Username")
    password = find_visible_input("Password")

    assert username.get_attribute("placeholder") == "Username"
    pause()

    assert password.get_attribute("placeholder") == "Password"


def test_login_functionality():
    username = find_visible_input("Username")
    username.clear()
    username.send_keys("admin")
    pause()

    password = find_visible_input("Password")
    password.clear()
    password.send_keys("1234")
    pause()

    login_buttons = driver.find_elements(
        By.XPATH,
        "//button[contains(normalize-space(), 'Login')]"
    )

    login_button = None

    for button in login_buttons:
        if button.is_displayed() and button.is_enabled():
            login_button = button
            break

    assert login_button is not None, "Login button is not interactable"

    login_button.click()

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h2[contains(text(),'Volunteer Management')]")
        )
    )


def test_volunteer_interface():
    assert find_visible_input("Search volunteer").is_displayed()
    pause()

    assert find_visible_input("Name").is_displayed()
    pause()

    assert find_visible_input("City").is_displayed()
    pause()

    selects = driver.find_elements(By.TAG_NAME, "select")
    assert any(s.is_displayed() for s in selects)
    pause()

    buttons = driver.find_elements(
        By.XPATH,
        "//button[contains(normalize-space(), 'Add Volunteer')]"
    )

    assert any(b.is_displayed() for b in buttons)


def test_volunteer_form_usability():
    assert find_visible_input("Name").get_attribute("placeholder") == "Name"
    pause()

    assert find_visible_input("City").get_attribute("placeholder") == "City"
    pause()

    select_element = next(
        s for s in driver.find_elements(By.TAG_NAME, "select")
        if s.is_displayed()
    )

    options = [option.text for option in Select(select_element).options]

    assert "Beginner" in options
    pause()

    assert "Experienced" in options


def test_add_volunteer():
    global volunteer_name

    volunteer_name = "TestVolunteer" + str(int(time.time()))

    find_visible_input("Name").send_keys(volunteer_name)
    pause()

    find_visible_input("City").send_keys("Chennai")
    pause()

    select_element = next(
        s for s in driver.find_elements(By.TAG_NAME, "select")
        if s.is_displayed()
    )

    Select(select_element).select_by_visible_text("Experienced")
    pause()

    add_buttons = driver.find_elements(
        By.XPATH,
        "//button[contains(normalize-space(), 'Add Volunteer')]"
    )

    add_button = next(
        b for b in add_buttons if b.is_displayed() and b.is_enabled()
    )

    add_button.click()

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//p[contains(text(),'Volunteer added successfully')]")
        )
    )

    pause()

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//td[normalize-space()='{volunteer_name}']")
        )
    )


def test_search_volunteer():
    search = find_visible_input("Search volunteer")
    search.clear()
    search.send_keys(volunteer_name)
    pause()

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//tr[td[normalize-space()='{volunteer_name}']]")
        )
    )


def test_empty_form_validation():
    find_visible_input("Search volunteer").clear()
    pause()

    find_visible_input("Name").clear()
    pause()

    find_visible_input("City").clear()
    pause()

    add_buttons = driver.find_elements(
        By.XPATH,
        "//button[contains(normalize-space(), 'Add Volunteer')]"
    )

    add_button = next(
        b for b in add_buttons if b.is_displayed() and b.is_enabled()
    )

    add_button.click()
    pause()

    alert = wait.until(EC.alert_is_present())

    print("Validation message:", alert.text)

    assert alert.text == "Fill all fields"
    alert.accept()


def test_logout():
    logout_buttons = driver.find_elements(
        By.XPATH,
        "//button[contains(normalize-space(), 'Logout')]"
    )

    logout_button = next(
        b for b in logout_buttons if b.is_displayed() and b.is_enabled()
    )

    logout_button.click()
    pause()

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Username']")
        )
    )


try:
    # Test 1
    report_test("TEST 1: Open RescueConnect Application",
                test_application_open)

    # Only continue the login-dependent tests if the application opened.
    if passed == 1:
        report_test("TEST 2: Login Interface Testing",
                    test_login_interface)

        report_test("TEST 3: Login Usability Testing",
                    test_login_usability)

        report_test("TEST 4: Login Functional Testing",
                    test_login_functionality)

        # Run these only if login succeeded.
        if driver.find_elements(
            By.XPATH, "//h2[contains(text(),'Volunteer Management')]"
        ):
            report_test("TEST 5: Volunteer Management Interface Testing",
                        test_volunteer_interface)

            report_test("TEST 6: Volunteer Form Usability Testing",
                        test_volunteer_form_usability)

            report_test("TEST 7: Add Volunteer Functional Testing",
                        test_add_volunteer)

            if "volunteer_name" in globals():
                report_test("TEST 8: Search Volunteer Functional Testing",
                            test_search_volunteer)

                report_test("TEST 9: Empty Form Validation Testing",
                            test_empty_form_validation)

            report_test("TEST 10: Logout Functional Testing",
                        test_logout)

    print("\n========================================")
    print("RESCUECONNECT SELENIUM TEST SUMMARY")
    print("========================================")
    print("Passed:", passed)
    print("Failed:", failed)
    print("========================================")

finally:
    time.sleep(0.5)
    driver.quit()