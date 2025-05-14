from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException
import time

# === Setup ===
driver = webdriver.Chrome()
driver.implicitly_wait(5)

base_url = "http://127.0.0.1:5000"

def log(msg):
    print(f"\n🔍 {msg}")

def success(msg, start_time):
    duration = time.time() - start_time
    print(f"✅ {msg} (Ran in {duration:.2f}s)")

def handle_possible_alert():
    try:
        alert = driver.switch_to.alert
        print(f"[⚠️ ALERT] {alert.text}")
        alert.accept()
        time.sleep(0.5)
    except:
        pass

def wait_for_redirect(expected_keyword, timeout=5):
    for _ in range(timeout * 2):
        time.sleep(0.5)
        if expected_keyword in driver.current_url:
            return True
    return False

# ==== SIGN UP TEST ====
log("Testing Signup")
start = time.time()

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
success("Signup test passed", start)

# ==== LOGIN TEST ====
log("Testing Login")
start = time.time()

driver.get(f"{base_url}/login-page")
driver.find_element(By.ID, "email").send_keys(test_email)
driver.find_element(By.ID, "password").send_keys(test_password)
driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

handle_possible_alert()
assert wait_for_redirect("/home"), "❌ Login failed or did not redirect to /home"
success("Login test passed", start)

# ==== LOGOUT TEST ====
log("Testing Logout")
start = time.time()

driver.get(f"{base_url}/logout")
time.sleep(1)
assert "login" in driver.current_url, "❌ Logout did not redirect to login"
success("Logout test passed", start)

# ==== LOGIN WITH INVALID PASSWORD ====
log("Testing invalid password login")
start = time.time()

driver.get(f"{base_url}/login-page")
driver.find_element(By.ID, "email").send_keys(test_email)
driver.find_element(By.ID, "password").send_keys("WrongPassword123")
driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

handle_possible_alert()
assert "login" in driver.current_url, "❌ Invalid login should not redirect"
success("Invalid password login test passed", start)

# ==== VISIT FORGOT PASSWORD PAGE ====
log("Testing forgot password page")
start = time.time()

driver.get(f"{base_url}/forgot-password")
assert "forgot-password" in driver.current_url, "❌ Forgot password page not reachable"
success("Forgot password page test passed", start)

# ==== EMPTY LOGIN SUBMISSION ====
log("Testing empty login submission")
start = time.time()

driver.get(f"{base_url}/login-page")
driver.find_element(By.ID, "email").clear()
driver.find_element(By.ID, "password").clear()
driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

handle_possible_alert()
assert "login" in driver.current_url, "❌ Empty form submission should not redirect"
success("Empty form login test passed", start)

# ==== DONE ====
print("\n🎉 All tests completed.")
driver.quit()
