import time
import uuid
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

TARGET_URL = "https://h8nsg1-ltcm4i61r-arcadawebapps2.vercel.app/m/b48a66f23021bd2875fc"

MESSAGE_COUNT = 500  # تعداد پیام‌های انبوه

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        print("در حال باز کردن سایت...")

        # اولین بارگذاری صفحه
        page.goto(
            TARGET_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("HTML اولیه دریافت شد.")

        for i in range(1, MESSAGE_COUNT + 1):
            print(f"\n--- ارسال پیام {i} از {MESSAGE_COUNT} ---")

            # دور زدن محدودیت نرخ سمت کلاینت
            page.evaluate("localStorage.clear();")
            page.evaluate("sessionStorage.clear();")

            # رفرش صفحه برای بارگذاری دوباره فرم با state پاک‌شده
            page.reload(wait_until="domcontentloaded", timeout=60000)

            # منتظر آماده شدن فرم
            message_box = page.locator(
                "textarea[placeholder='اینجا بنویس...']"
            )
            message_box.wait_for(
                state="visible",
                timeout=60000
            )

            # ساخت متن یکتا برای هر پیام
            unique_id = uuid.uuid4().hex[:8]
            message_text = f"پیام تست شماره {i} - {unique_id}"

            # وارد کردن پیام
            message_box.fill(message_text)

            # دکمه ارسال
            submit_button = page.get_by_text(
                "ارسال ناشناس",
                exact=True
            )
            submit_button.wait_for(
                state="visible",
                timeout=15000
            )

            # کلیک روی دکمه
            submit_button.click()

            # کمی صبر برای پردازش و ذخیره پیام
            page.wait_for_timeout(800)

            print(f"پیام {i} با موفقیت ارسال شد: {message_text}")

    except PlaywrightTimeoutError as e:
        print("❌ Playwright Timeout")
        print(e)
        print("URL هنگام خطا:")
        print(page.url)

    except Exception as e:
        print("❌ خطای غیرمنتظره:")
        print(type(e).__name__)
        print(e)

    finally:
        browser.close()
        print("Browser بسته شد.")
