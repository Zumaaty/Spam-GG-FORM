import json
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# --- CẤU HÌNH TRỰC TIẾP ---
RAW_URL = "DÁN_LINK_GOOGLE_FORM_CỦA_MÀN_HÌNH_BẠN_VÀO_ĐÂY"
TOTAL_RUNS = 20  # Số lượng lượt chạy mong muốn
FIXED_TEXT_ANSWER = "Không có ý kiến"

# Xử lý tự động chuẩn hóa URL để ép Google Form nhận diện điểm gửi phản hồi
if "/viewform" in RAW_URL:
    viewform_url = RAW_URL.split("/viewform")[0] + "/viewform"
elif "/edit" in RAW_URL:
    viewform_url = RAW_URL.split("/edit")[0] + "/viewform"
else:
    viewform_url = RAW_URL.strip("/") + "/viewform"

def run_automation():
    success_count = 0
    fail_count = 0

    print(f"Bắt đầu khởi tạo phiên làm việc tốc độ cao cho {TOTAL_RUNS} lượt...")

    # MỞ CHROME 1 LẦN DUY NHẤT ĐỂ TĂNG TỐC TỐI ĐA
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        for run in range(TOTAL_RUNS):
            print(f"Đang gửi lượt thứ {run + 1}/{TOTAL_RUNS}...", end=" ")
            try:
                driver.get(viewform_url)
                time.sleep(1) # Chờ form load nhanh

                # Duyệt qua các trang của form
                for page in range(10):
                    time.sleep(0.3)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.2)

                    # Điền câu hỏi
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

                    # Xử lý nút Tiếp theo / Gửi
                    next_buttons = driver.find_elements(By.XPATH, "//div[@role='button']//span[contains(translate(text(), 'TẤP', 'tap'), 'tiếp') or contains(translate(text(), 'NEXT', 'next'), 'next')]")
                    valid_next = [btn for btn in next_buttons if btn.is_displayed()]

                    if valid_next:
                        driver.execute_script("arguments[0].click();", valid_next[0])
                        time.sleep(0.5)
                    else:
                        time.sleep(0.3)
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
                            print("Gửi thành công!")
                            success_count += 1
                        else:
                            print("Không tìm thấy nút Gửi!")
                            fail_count += 1
                        time.sleep(0.5)
                        break

            except Exception as e:
                print(f"Lỗi lượt này: {e}")
                fail_count += 1

    finally:
        driver.quit()

    print(f"\n=== KẾT QUẢ HOÀN TẤT ===")
    print(f"Thành công: {success_count} | Thất bại: {fail_count}")

if __name__ == "__main__":
    run_automation()
