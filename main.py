import json
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Đọc URL và số lần chạy trực tiếp qua biến môi trường hoặc cấu hình sẵn để GitHub tự động hóa
VIEWFORM_URL = "ĐIỀN_URL_FORM_CỦA_BẠN_VÀO_ĐÂY"
TOTAL_RUNS = 10  # Số lượng lượt bạn muốn chạy mỗi lần trigger
FIXED_TEXT_ANSWER = "Không có ý kiến"

def run_automation():
    success_count = 0
    fail_count = 0

    for run in range(TOTAL_RUNS):
        print(f"\n--- Đang chạy lượt thứ {run + 1}/{TOTAL_RUNS} ---")
        
        # Cấu hình Chrome chạy ngầm (Headless) chuẩn Linux cho GitHub Actions
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            driver.get(VIEWFORM_URL)
            time.sleep(2)

            # Vòng lặp duyệt qua các trang
            for page in range(10):
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)

                # Điền câu hỏi
                question_blocks = driver.find_elements(By.XPATH, "//div[@role='listitem']")
                for block in question_blocks:
                    try:
                        # Trắc nghiệm
                        radio_options = block.find_elements(By.XPATH, ".//div[@role='radio']")
                        if radio_options:
                            chosen = random.choice(radio_options)
                            driver.execute_script("arguments[0].scrollIntoView(true);", chosen)
                            chosen.click()
                            continue

                        # Dạng Lưới
                        grid_rows = block.find_elements(By.XPATH, ".//div[@role='row']")
                        if grid_rows:
                            for row in grid_rows:
                                r_radios = row.find_elements(By.XPATH, ".//div[@role='radio']")
                                if r_radios:
                                    random.choice(r_radios).click()
                            continue

                        # Checkbox
                        checkbox_options = block.find_elements(By.XPATH, ".//div[@role='checkbox']")
                        if checkbox_options:
                            sampled = random.sample(checkbox_options, k=min(len(checkbox_options), random.randint(1, 2)))
                            for cb in sampled:
                                cb.click()
                            continue

                        # Tự luận
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
                    time.sleep(1)
                else:
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
                        print("-> Gửi thành công!")
                        success_count += 1
                    else:
                        print("-> Không tìm thấy nút Gửi!")
                        fail_count += 1
                    time.sleep(2)
                    break

            driver.quit()
        except Exception as ex:
            print(f"-> Lỗi: {ex}")
            fail_count += 1
            try:
                driver.quit()
            except:
                pass

    print(f"\n=== KẾT QUẢ HOÀN TẤT ===")
    print(f"Thành công: {success_count} | Thất bại: {fail_count}")

if __name__ == "__main__":
    run_automation()