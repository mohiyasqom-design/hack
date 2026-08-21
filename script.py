import time
import uuid
from playwright.sync_api import sync_playwright

TARGET_URL = "https://h8nsg1-ltcm4i61r-arcadawebapps2.vercel.app/m/b48a66f23021bd2875fc"
MESSAGE_COUNT = 500

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.goto(TARGET_URL, wait_until="networkidle")

    for i in range(1, MESSAGE_COUNT + 1):
        # دور زدن محدودیت نرخ سمت کلاینت
        page.evaluate("localStorage.clear();")
        page.evaluate("sessionStorage.clear();")

        # رفرش صفحه برای بارگذاری دوباره فرم با state پاک‌شده
        page.reload(wait_until="networkidle")

        # سلکتورهای دقیق استخراج‌شده از سایت
        message_box = page.locator("textarea[placeholder='اینجا بنویس...']")
        submit_btn = page.get_by_text("ارسال ناشناس", exact=True)

        message_box.wait_for(state="visible", timeout=10000)

        unique_id = uuid.uuid4().hex[:8]
        message_text = f"پیام تست شماره {i} - {unique_id}"

        message_box.fill(message_text)
        submit_btn.click()

        print(f"پیام {i} ارسال شد: {message_text}")

        # فاصله کوتاه برای اعمال تغییرات
        page.wait_for_timeout(800)

    browser.close()
