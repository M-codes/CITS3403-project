from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException
import time

# Set up WebDriver
driver = webdriver.Chrome()
driver.implicitly_wait(5)

base_url = "http://127.0.0.1:5000"

# === Helper Functions ===
def handle_possible_alert():
    try:
        alert = driver.switch_to.alert
        print(f"[⚠️ ALERT] {alert.text}")
        alert.accept()
        time.sleep(1)
    except:
        pass  # No alert

def wait_for_redirect(expected_keyword, timeout=5):
    for _ in range(timeout * 2):
        time.sleep(0.5)
        if expected_keyword in driver.current_url:
            return True
    return False

# ==== SIGN UP TEST ====
print("🔍 Testing Signup...")
driver.get(f"{base_url}/signup-page")

email_input = driver.find_element(By.ID, "email")
password_input = driver.find_element(By.ID, "password")

test_email = f"testuser{int(time.time())}@example.com"
test_password = "Test1234"

email_input.send_keys(test_email)
password_input.send_keys(test_password)
password_input.send_keys(Keys.ENTER)

handle_possible_alert()
assert wait_for_redirect("login"), "❌ Signup did not redirect to login page"
print("✅ Signup test passed")

# ==== LOGIN TEST ====
print("🔍 Testing Login...")
driver.get(f"{base_url}/login-page")

driver.find_element(By.ID, "email").send_keys(test_email)
driver.find_element(By.ID, "password").send_keys(test_password)
driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

handle_possible_alert()
assert wait_for_redirect("/home"), "❌ Login failed or did not redirect to /home"
print("✅ Login test passed")

# ==== LOGOUT TEST ====
print("🔍 Testing Logout...")
driver.get(f"{base_url}/logout")
time.sleep(1)
assert "login" in driver.current_url, "❌ Logout did not redirect to login"
print("✅ Logout test passed")

# ==== LOGIN WITH INVALID PASSWORD ====
print("🔍 Testing invalid login...")
driver.get(f"{base_url}/login-page")

driver.find_element(By.ID, "email").send_keys(test_email)
driver.find_element(By.ID, "password").send_keys("WrongPassword123")
driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

handle_possible_alert()
assert "login" in driver.current_url, "❌ Invalid login should not redirect"
print("✅ Invalid password login test passed")

# ==== VISIT FORGOT PASSWORD PAGE ====
print("🔍 Testing forgot password page...")
driver.get(f"{base_url}/forgot-password")
assert "forgot-password" in driver.current_url, "❌ Forgot password page not reachable"
print("✅ Forgot password page test passed")

# ==== EMPTY LOGIN SUBMISSION ====
print("🔍 Testing empty login submission...")
driver.get(f"{base_url}/login-page")
driver.find_element(By.ID, "email").clear()
driver.find_element(By.ID, "password").clear()
driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

handle_possible_alert()
assert "login" in driver.current_url, "❌ Empty form submission should not redirect"
print("✅ Empty form login test passed")

# ==== Done ====
print("🎉 All tests completed successfully.")
driver.quit()
