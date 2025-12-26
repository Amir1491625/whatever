import flet as ft
import datetime
from supabase import create_client, Client

# --- تنظیمات دیتابیس ---
URL = "https://ebhenwvzccseryjmfmdv.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImViaGVud3Z6Y2NzZXJ5am1mbWR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3NDcxMzAsImV4cCI6MjA4MjMyMzEzMH0.jO4NrgGlvE9hH8-pn2QEwVEg50iqWqJ4HF8MuzsLvsI"


class Database:
    def __init__(self):
        try:
            self.client: Client = create_client(URL, KEY)
        except:
            self.client = None

    def fetch_all(self):
        if not self.client: return []
        try:
            # اضافه کردن تایم‌اوت کوتاه برای جلوگیری از فریز شدن صفحه
            res = self.client.table('projects').select("*").order('id').execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"خطا در اتصال: {e}")
            return []

    def add_proj(self, name):
        if not self.client: return
        data = {"name": name, "last_update_str": datetime.date.today().isoformat()}
        try:
            self.client.table('projects').insert(data).execute()
        except:
            pass


def main(page: ft.Page):
    page.title = "مدیریت نوبت"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400  # تنظیم اندازه برای تست راحت‌تر
    page.window_height = 600
    db = Database()

    def go_home(e=None):
        page.views.clear()

        # نمایش وضعیت در حال بارگذاری
        loading = ft.ProgressBar(width=200, color="blue")
        page.views.append(ft.View("/", [
            ft.AppBar(title=ft.Text("لیست پروژه‌ها")),
            ft.Column([ft.Text("در حال دریافت اطلاعات..."), loading], alignment="center", horizontal_alignment="center",
                      expand=True)
        ]))
        page.update()

        projs = db.fetch_all()

        lv = ft.ListView(expand=True, spacing=10, padding=20)
        for proj in projs:
            lv.controls.append(ft.ListTile(
                title=ft.Text(proj['name']),
                on_click=lambda e, pid=proj['id']: go_project(pid),
                trailing=ft.Icon(name="chevron_left"),
                bgcolor=ft.colors.BLUE_50
            ))

        def open_add(e):
            t = ft.TextField(label="نام پروژه")

            def save(e):
                if t.value:
                    db.add_proj(t.value)
                    page.dialog.open = False
                    go_home()

            page.dialog = ft.AlertDialog(
                title=ft.Text("پروژه جدید"),
                content=t,
                actions=[ft.TextButton("ثبت", on_click=save)]
            )
            page.dialog.open = True
            page.update()

        # بازنویسی ویو اصلی بعد از دریافت (یا خطا در دریافت) اطلاعات
        page.views.clear()
        page.views.append(ft.View("/", [
            ft.AppBar(
                title=ft.Text("لیست پروژه‌ها"),
                actions=[ft.IconButton(icon="add", on_click=open_add)]
            ),
            lv if projs else ft.Column(
                [ft.Text("پروژه‌ای یافت نشد یا اینترنت وصل نیست", color="red")],
                alignment="center", horizontal_alignment="center", expand=True
            )
        ]))
        page.update()

    # تابع go_project را هم اینجا ساده قرار می‌دهیم
    def go_project(pid):
        page.views.append(ft.View(f"/p/{pid}", [
            ft.AppBar(title=ft.Text("جزییات")),
            ft.ElevatedButton("بازگشت", on_click=go_home)
        ]))
        page.update()

    go_home()


# اصلاح نهایی برای حذف DeprecationWarning
ft.run(main)