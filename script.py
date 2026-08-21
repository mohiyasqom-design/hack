import time
import random
import string
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

TARGET_URL = "https://h8nsg1-ltcm4i61r-arcadawebapps2.vercel.app/m/6e1995b186b8c262842b"

MESSAGE_COUNT = 1000000  # تعداد پیام‌های انبوه

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        print("در حال باز کردن سایت...")
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        print("HTML اولیه دریافت شد.")

        for i in range(1, MESSAGE_COUNT + 1):
            print(f"\n--- ارسال پیام {i} از {MESSAGE_COUNT} ---")

            try:
                # ۱) دور زدن محدودیت نرخ سمت کلاینت
                page.evaluate("localStorage.clear();")
                page.evaluate("sessionStorage.clear();")

                # ۲) رفرش صفحه برای بارگذاری فرم با state پاک‌شده
                page.reload(wait_until="domcontentloaded", timeout=60000)

                # ۳) انتظار برای آماده شدن کادر پیام
                message_box = page.locator("textarea[placeholder='اینجا بنویس...']")
                message_box.wait_for(state="visible", timeout=60000)

                # ۴) ساخت رشته تصادفی با دقیقاً ۱۰۰۰ کاراکتر
                random_message = ''.join(
                    random.choices(string.ascii_letters + string.digits, k=1000)
                )

                # ۵) وارد کردن پیام
                message_box.fill(random_message)

                # ۶) دکمه ارسال
                submit_button = page.get_by_text("ارسال ناشناس", exact=True)
                submit_button.wait_for(state="visible", timeout=15000)

                # ۷) کلیک روی دکمه ارسال
                submit_button.click()

                # ۸) بررسی واقعی موفقیت با منتظر ماندن برای پیام تأیید سایت
                try:
                    success_message = page.get_by_text(
                        "پیامت با موفقیت ارسال شد",
                        exact=False
                    )
                    success_message.wait_for(state="visible", timeout=30000)
                    print(f"✅ پیام {i} واقعاً توسط سایت تأیید شد")

                except PlaywrightTimeoutError:
                    print(f"❌ پیام {i} تأیید نشد")
                    print("URL:", page.url)
                    print("متن صفحه:")
                    print(page.locator("body").inner_text()[:2000])
                    # بدون re-raise؛ تا حلقه ادامه یابد

            except PlaywrightTimeoutError as e:
                print(f"⚠️ پیام {i} با خطای Timeout مواجه شد: {e}")
                # تلاش برای بازیابی صفحه تا ارسال بعدی از وضعیت سالم شروع شود
                try:
                    page.reload(wait_until="domcontentloaded", timeout=60000)
                except Exception:
                    pass
                continue

            except Exception as e:
                print(f"❌ خطا در پیام {i}: {type(e).__name__} - {e}")
                try:
                    page.reload(wait_until="domcontentloaded", timeout=60000)
                except Exception:
                    pass
                continue

        print("\nپایان اجرای تست.")

    finally:
        browser.close()
        print("Browser بسته شد.")
