import json
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CẤU HÌNH TRỰC TIẾP ---
RAW_URL = "DÁN_LINK_GOOGLE_FORM_CỦA_BẠN_VÀO_ĐÂY"
TOTAL_RUNS = 10  # Chạy thử 10 lượt trước để kiểm tra log
FIXED_TEXT_ANSWER = "Không có ý kiến"

if "/viewform" in RAW_URL:
    viewform_url = RAW_URL.split("/viewform")[0] + "/viewform"
elif "/edit" in RAW_URL:
    viewform_url = RAW_URL.split("/edit")[0] + "/viewform"
else:
    viewform_url = RAW_URL.strip("/") + "/viewform"

def run_automation():
    success_count = 0
    fail_count = 0

    print(f"Bắt đầu chạy form: {viewform_url}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    try:
        for run in range(TOTAL_RUNS):
            print(f"\n--- Lượt {run + 1}/{TOTAL_RUNS} ---")
            try:
                driver.get(viewform_url)
                
                # Chờ cho đến khi danh sách câu hỏi xuất hiện hẳn trên trang
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='listitem']")))
                time.sleep(1)

                # Duyệt qua các trang (tối đa 10 trang)
                for page in range(10):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.5)

                    # Điền câu hỏi trên trang hiện tại
                    question_blocks = driver.find_elements(By.XPATH, "//div[@role='listitem']")
                    for block in question_blocks:
                        try:
                            radio_options = block.find_elements(By.XPATH, ".//div[@role='radio']")
                            if radio_options:
                                chosen = random.choice(radio_options)
                                driver.execute_script("arguments[0].scrollIntoView(true);", chosen)
                                chosen.click()
                                continue

                            grid_rows = block.find_elements(By.XPATH, ".//div[@role='row']")
                            if grid_rows:
                                for row in grid_rows:
                                    r_radios = row.find_elements(By.XPATH, ".//div[@role='radio']")
                                    if r_radios:
                                        random.choice(r_radios).click()
                                continue

                            checkbox_options = block.find_elements(By.XPATH, ".//div[@role='checkbox']")
                            if checkbox_options:
                                sampled = random.sample(checkbox_options, k=min(len(checkbox_options), random.randint(1, 2)))
                                for cb in sampled:
                                    cb.click()
                                continue

                            text_inputs = block.find_elements(By.XPATH, ".//input[@type='text'] | .//textarea")
                            if text_inputs:
                                text_inputs[0].clear()
                                text_inputs[0].send_keys(FIXED_TEXT_ANSWER)
                        except:
                            continue

                    # Kiểm tra nút "Tiếp theo" hoặc nút "Gửi"
                    next_buttons = driver.find_elements(By.XPATH, "//div[@role='button']//span[contains(translate(text(), 'TẤP', 'tap'), 'tiếp') or contains(translate(text(), 'NEXT', 'next'), 'next')]")
                    valid_next = [btn for btn in next_buttons if btn.is_displayed()]

                    if valid_next:
                        driver.execute_script("arguments[0].click();", valid_next[0])
                        time.sleep(1)
                    else:
                        # Đã đến trang cuối, tìm nút Gửi
                        time.sleep(1)
                        all_buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
                        submit_clicked = False
                        if all_buttons:
                            for btn in reversed(all_buttons):
                                try:
                                    btn_text = btn.text.strip().lower()
                                    if "xóa" not in btn_text and btn.is_displayed():
                                        driver.execute_script("arguments[0].click();", btn)
                                        submit_clicked = True
                                        break
                                except:
                                    continue

                        if submit_clicked:
                            print("-> Đã bấm Gửi thành công!")
                            success_count += 1
                        else:
                            print("-> Thất bại: Không tìm thấy nút Gửi trên trang cuối!")
                            fail_count += 1
                        time.sleep(2)
                        break

            except Exception as e:
                print(f"-> Lỗi ngoại lệ ở lượt này: {e}")
                fail_count += 1

    finally:
        driver.quit()

    print(f"\n=== KẾT QUẢ HOÀN TẤT ===")
    print(f"Thành công: {success_count} | Thất bại: {fail_count}")

if __name__ == "__main__":
    run_automation()
