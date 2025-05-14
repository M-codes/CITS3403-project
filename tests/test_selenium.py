from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set up WebDriver
driver = webdriver.Chrome()
driver.implicitly_wait(5)

base_url = "http://127.0.0.1:5000"

# ==== SIGN UP TEST ====
driver.get(f"{base_url}/signup-page")

email_input = driver.find_element(By.ID, "email")
password_input = driver.find_element(By.ID, "password")

test_email = f"testuser{int(time.time())}@example.com"
test_password = "Test1234"

email_input.send_keys(test_email)
password_input.send_keys(test_password)

# Recaptcha must be handled manually or disabled for testing

password_input.send_keys(Keys.ENTER)

time.sleep(2)
assert "login" in driver.current_url, "Signup did not redirect to login page"
print("✅ Signup test passed")

# ==== LOGIN TEST ====
driver.get(f"{base_url}/login-page")

driver.find_element(By.ID, "email").send_keys(test_email)
driver.find_element(By.ID, "password").send_keys(test_password)
driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

time.sleep(2)
assert "/home" in driver.current_url or "signup" not in driver.current_url, "Login failed"
print("✅ Login test passed")

# ==== LOGOUT TEST ====
driver.get(f"{base_url}/logout")
time.sleep(2)
assert "login" in driver.current_url, "Logout did not redirect to login"
print("✅ Logout test passed")

# ==== LOGIN WITH INVALID PASSWORD ====
driver.get(f"{base_url}/login-page")

driver.find_element(By.ID, "email").send_keys(test_email)
driver.find_element(By.ID, "password").send_keys("WrongPassword123")
driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

time.sleep(2)
assert "login" in driver.current_url, "Invalid login should not proceed"
print("✅ Invalid password login test passed")

# ==== VISIT FORGOT PASSWORD PAGE ====
driver.get(f"{base_url}/forgot-password")

assert "forgot-password" in driver.current_url, "Forgot password page not reachable"
print("✅ Forgot password page test passed")

# ==== TRY TO LOGIN WITH EMPTY FIELDS ====
driver.get(f"{base_url}/login-page")
driver.find_element(By.ID, "email").clear()
driver.find_element(By.ID, "password").clear()
driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

time.sleep(2)
assert "login" in driver.current_url, "Empty form submission should not redirect"
print("✅ Empty form login test passed")

# ==== Done ====
driver.quit()
