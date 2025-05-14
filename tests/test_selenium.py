from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# You can use ChromeOptions to hide the browser
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # or "--headless" to run without UI

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)

base_url = "http://127.0.0.1:5000"  # make sure your Flask app is running

# ==== LOGIN TEST ====
def test_login():
    driver.get(f"{base_url}/login-page")

    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")

    test_email = "test@example.com"
    test_password = "Test1234"  # make sure this user exists in your database

    email_input.send_keys(test_email)
    password_input.send_keys(test_password)

    login_btn = driver.find_element(By.ID, "loginBtn")
    login_btn.click()

    time.sleep(2)
    assert driver.current_url.endswith('/home') or driver.current_url.endswith('/'), "Login failed or did not redirect properly"
    print("✅ Login test passed")

# ==== SESSION CHECK TEST ====
def test_session_check():
    driver.get(f"{base_url}/check-session")
    assert '"logged_in": true' in driver.page_source or 'true' in driver.page_source
    print("✅ Session check passed")

# ==== LOGOUT TEST ====
def test_logout():
    driver.get(f"{base_url}/logout")
    time.sleep(1)
    driver.get(f"{base_url}/check-session")
    assert '"logged_in": false' in driver.page_source or 'false' in driver.page_source
    print("✅ Logout test passed")

# ==== RUN TESTS ====
if __name__ == "__main__":
    try:
        test_login()
        test_session_check()
        test_logout()
    finally:
        driver.quit()
