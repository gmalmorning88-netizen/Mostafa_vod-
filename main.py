#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mostafa - Vodafone Charge App
Works directly on Vodafone data
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
import requests
import json
import threading
import os
from datetime import datetime

# ==================== REGISTER ARABIC FONT ====================
FONT_NAME = 'Roboto'

FONT_PATHS = [
    'Cairo-Regular.ttf',
    'fonts/Cairo-Regular.ttf',
    os.path.join(os.path.dirname(__file__), 'Cairo-Regular.ttf'),
    os.path.join(os.path.dirname(__file__), 'fonts', 'Cairo-Regular.ttf'),
]

for path in FONT_PATHS:
    if os.path.exists(path):
        try:
            LabelBase.register(name='ArabicFont', fn_regular=path)
            FONT_NAME = 'ArabicFont'
            print(f"[INFO] Arabic font loaded from: {path}")
            break
        except Exception as e:
            print(f"[WARNING] Failed to load font from {path}: {e}")

# ==================== CONFIG ====================
SUPABASE_URL = 'https://qippgvyupkeruvzkfdkz.supabase.co'
SUPABASE_KEY = 'sb_publishable_zUyj8k4QKYqognMAL6I1Qw_8cBGPFyf'
VODAFONE_CLIENT_SECRET = 'b86e30a8-ae29-467a-a71f-65c73f2ff5e3'
VODAFONE_CLIENT_ID = 'cash-app'
ADMIN_PHONE = '01019502983'

# ==================== PRODUCTS ====================
FAKKA_PRODUCTS = [
    {"id": "Fakka_2.5_Unite", "name": "فكة 2.5 جنيه", "price": 2.5, "units": 45, "validity": "24 ساعة"},
    {"id": "Fakka_4.25_Unite", "name": "فكة 4.25 جنيه", "price": 4.25, "units": 190, "validity": "24 ساعة"},
    {"id": "Fakka_5_Unite", "name": "فكة 5 جنيه", "price": 5, "units": 225, "validity": "24 ساعة"},
    {"id": "Fakka_7_Unite", "name": "فكة 7 جنيه", "price": 7, "units": 300, "validity": "3 أيام"},
    {"id": "Fakka_10_Unite", "name": "فكة 10 جنيه", "price": 10, "units": 450, "validity": "7 أيام"},
    {"id": "Fakka_15_Unite", "name": "فكة 15 جنيه", "price": 15, "units": 550, "validity": "7 أيام"},
    {"id": "Fakka_20_Unite", "name": "فكة 20 جنيه", "price": 20, "units": 0, "validity": "10 أيام"},
    {"id": "Fakka_26_Unite", "name": "فكة 26 جنيه", "price": 26, "units": 0, "validity": "شهر"},
]

MARED_PRODUCTS = [
    {"id": "Mared_10_Minuts", "name": "مارد 10 دقائق", "price": 10, "units": 10, "type": "دقائق", "validity": "24 ساعة"},
    {"id": "Mared_10_Flexs", "name": "مارد 10 فليكس", "price": 10, "units": 10, "type": "فليكس", "validity": "24 ساعة"},
    {"id": "Mared_10_Social", "name": "مارد 10 سوشيال", "price": 10, "units": 10, "type": "سوشيال", "validity": "24 ساعة"},
]

ALL_PRODUCTS = FAKKA_PRODUCTS + MARED_PRODUCTS

POINTS_PACKAGES = [
    {"points": 10, "price": 20, "label": "10 نقاط - 20 جنيه"},
    {"points": 25, "price": 50, "label": "25 نقطة - 50 جنيه"},
    {"points": 50, "price": 100, "label": "50 نقطة - 100 جنيه"},
    {"points": 100, "price": 200, "label": "100 نقطة - 200 جنيه"},
]

# ==================== APP ====================
class VodafoneApp(App):
    user_phone = StringProperty('')
    points = NumericProperty(0)
    is_admin = False

    def build(self):
        Window.clearcolor = (0.03, 0, 0, 1)
        self.title = 'Mostafa - شحن كروت فودافون'
        self.main_layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        self.show_login()
        return self.main_layout

    def show_login(self):
        self.main_layout.clear_widgets()

        # ====== شعار ======
        logo_container = BoxLayout(size_hint_y=None, height=200, padding=30)

        logo_text = '[b][color=E60000]VODAFONE[/color][/b]\n[color=FFFFFF]Mostafa[/color]'
        logo = Label(
            text=logo_text,
            markup=True,
            font_size='40sp',
            font_name=FONT_NAME
        )
        logo_container.add_widget(logo)
        self.main_layout.add_widget(logo_container)

        title = Label(
            text='[b]شحن كروت فودافون[/b]',
            markup=True,
            font_size='26sp',
            size_hint_y=None,
            height=70,
            font_name=FONT_NAME,
            color=(1, 1, 1, 1)
        )
        self.main_layout.add_widget(title)
        self.main_layout.add_widget(Label(size_hint_y=0.4))

        self.phone_input = TextInput(
            hint_text='رقم الهاتف (01XXXXXXXXX)',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=80,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            padding=(25, 20),
            font_size='22sp',
            font_name=FONT_NAME
        )
        self.main_layout.add_widget(self.phone_input)
        self.main_layout.add_widget(Label(size_hint_y=0.2))

        login_btn = Button(
            text='دخول',
            size_hint_y=None,
            height=80,
            background_color=(0.9, 0, 0, 1),
            color=(1, 1, 1, 1),
            font_size='22sp',
            bold=True,
            font_name=FONT_NAME
        )
        login_btn.bind(on_press=self.do_login)
        self.main_layout.add_widget(login_btn)
        self.main_layout.add_widget(Label(size_hint_y=0.6))

    def do_login(self, instance):
        phone = self.phone_input.text
        if len(phone) != 11 or not phone.startswith('01'):
            self.show_popup('خطأ', 'رقم الهاتف غير صحيح\nيجب أن يكون 11 رقم ويبدأ بـ 01')
            return

        self.user_phone = phone
        self.is_admin = (phone == ADMIN_PHONE)
        self.load_user_data()
        self.show_home()

    def load_user_data(self):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/users?phone=eq.{self.user_phone}&select=*',
                headers=headers,
                timeout=10
            )
            data = response.json()
            if data:
                self.points = data[0].get('points', 0)
            else:
                requests.post(
                    f'{SUPABASE_URL}/rest/v1/users',
                    headers={**headers, 'Content-Type': 'application/json'},
                    json={'phone': self.user_phone, 'points': 0},
                    timeout=10
                )
                self.points = 0
        except Exception as e:
            print(f'Error loading user: {e}')
            self.points = 0

    def show_home(self):
        self.main_layout.clear_widgets()

        # ====== Header ======
        header = BoxLayout(size_hint_y=None, height=100, spacing=15)

        points_btn = Button(
            text=f'⭐ {self.points} نقطة',
            size_hint_x=0.35,
            background_color=(0.97, 0.79, 0.28, 0.2),
            color=(0.97, 0.79, 0.28, 1),
            font_size='16sp',
            bold=True,
            font_name=FONT_NAME
        )
        points_btn.bind(on_press=self.show_points_dialog)
        header.add_widget(points_btn)

        history_btn = Button(
            text='📋 سجل',
            size_hint_x=0.25,
            background_color=(0.2, 0.5, 0.9, 0.3),
            color=(1, 1, 1, 1),
            font_size='14sp',
            font_name=FONT_NAME
        )
        history_btn.bind(on_press=self.show_history)
        header.add_widget(history_btn)

        recharge_btn = Button(
            text='شحن نقاط',
            size_hint_x=0.25,
            background_color=(0.97, 0.79, 0.28, 0.3),
            color=(0.97, 0.79, 0.28, 1),
            font_size='14sp',
            bold=True,
            font_name=FONT_NAME
        )
        recharge_btn.bind(on_press=self.show_recharge_dialog)
        header.add_widget(recharge_btn)

        if self.is_admin:
            admin_btn = Button(
                text='⚙️',
                size_hint_x=0.15,
                background_color=(0.2, 0.6, 1, 1),
                color=(1, 1, 1, 1),
                font_size='24sp',
                font_name=FONT_NAME
            )
            admin_btn.bind(on_press=self.show_admin_panel)
            header.add_widget(admin_btn)

        self.main_layout.add_widget(header)
        self.main_layout.add_widget(Label(size_hint_y=None, height=25))

        # ====== Category buttons ======
        cat_layout = BoxLayout(size_hint_y=None, height=70, spacing=20, padding=(15, 0))

        all_btn = Button(
            text='الكل',
            background_color=(0.9, 0, 0, 0.3),
            color=(1, 1, 1, 1),
            font_size='16sp',
            font_name=FONT_NAME
        )
        all_btn.bind(on_press=lambda x: self.show_products('all'))
        cat_layout.add_widget(all_btn)

        fakka_btn = Button(
            text='⚡ فكة',
            background_color=(0.9, 0, 0, 0.3),
            color=(1, 1, 1, 1),
            font_size='16sp',
            font_name=FONT_NAME
        )
        fakka_btn.bind(on_press=lambda x: self.show_products('fakka'))
        cat_layout.add_widget(fakka_btn)

        mared_btn = Button(
            text='🔥 مارد',
            background_color=(0.9, 0, 0, 0.3),
            color=(1, 1, 1, 1),
            font_size='16sp',
            font_name=FONT_NAME
        )
        mared_btn.bind(on_press=lambda x: self.show_products('mared'))
        cat_layout.add_widget(mared_btn)

        self.main_layout.add_widget(cat_layout)
        self.main_layout.add_widget(Label(size_hint_y=None, height=20))

        # ====== Products area ======
        self.products_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.products_layout)
        self.show_products('all')

    def show_products(self, category):
        self.products_layout.clear_widgets()

        if category == 'all':
            products = ALL_PRODUCTS
        elif category == 'fakka':
            products = FAKKA_PRODUCTS
        else:
            products = MARED_PRODUCTS

        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=20, padding=20, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for product in products:
            btn_text = f'[b]{product["name"]}[/b]\n{product["price"]} جنيه\n{product.get("units", 0)} {product.get("type", "وحدة")}'
            btn = Button(
                text=btn_text,
                markup=True,
                size_hint_y=None,
                height=170,
                background_color=(0.9, 0, 0, 0.2),
                color=(1, 1, 1, 1),
                font_size='16sp',
                font_name=FONT_NAME
            )
            btn.bind(on_press=lambda x, p=product: self.show_charge_dialog(p))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        self.products_layout.add_widget(scroll)

    def show_charge_dialog(self, product):
        content = BoxLayout(orientation='vertical', spacing=25, padding=30)

        info_text = f'[b]{product["name"]}[/b]\nالسعر: {product["price"]} جنيه\nسيتم خصم نقطة واحدة'
        info = Label(
            text=info_text,
            markup=True,
            font_size='18sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=120,
            font_name=FONT_NAME
        )
        content.add_widget(info)
        content.add_widget(Label(size_hint_y=None, height=15))

        target_input = TextInput(
            hint_text='رقم الهاتف للشحن',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=70,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            padding=(25, 20),
            font_size='18sp',
            font_name=FONT_NAME
        )
        content.add_widget(target_input)
        content.add_widget(Label(size_hint_y=None, height=15))

        pin_input = TextInput(
            hint_text='الرقم السري للمحفظة',
            multiline=False,
            password=True,
            size_hint_y=None,
            height=70,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            padding=(25, 20),
            font_size='18sp',
            font_name=FONT_NAME
        )
        content.add_widget(pin_input)
        content.add_widget(Label(size_hint_y=None, height=20))

        btn_layout = BoxLayout(size_hint_y=None, height=70, spacing=20)

        cancel_btn = Button(
            text='إلغاء',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            font_name=FONT_NAME
        )

        charge_btn = Button(
            text='تأكيد الشحن',
            background_color=(0.9, 0, 0, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size='16sp',
            font_name=FONT_NAME
        )

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(charge_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title=f'شحن {product["name"]}',
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False,
            title_font=FONT_NAME
        )

        cancel_btn.bind(on_press=popup.dismiss)

        def do_charge(instance):
            if self.points <= 0:
                self.show_popup('خطأ', 'لا توجد نقاط كافية\nاشحن نقاط أولاً')
                return

            target = target_input.text
            pin = pin_input.text

            if len(target) != 11 or not target.startswith('01'):
                self.show_popup('خطأ', 'رقم الهاتف غير صحيح')
                return

            if len(pin) < 4:
                self.show_popup('خطأ', 'الرقم السري قصير جداً')
                return

            popup.dismiss()
            self.charge_card(target, pin, product)

        charge_btn.bind(on_press=do_charge)
        popup.open()

    def charge_card(self, msisdn, pin, product):
        loading_content = BoxLayout(orientation='vertical', padding=40, spacing=20)
        loading_content.add_widget(Label(text='جاري الشحن...', font_size='20sp', font_name=FONT_NAME))
        progress = ProgressBar(max=100, value=50, size_hint_y=None, height=25)
        loading_content.add_widget(progress)

        loading_popup = Popup(
            title='الرجاء الانتظار',
            content=loading_content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False,
            title_font=FONT_NAME
        )
        loading_popup.open()

        def charge_thread():
            try:
                self.points -= 1
                self.update_points()

                result = self.call_vodafone_api(msisdn, pin, product['id'])

                Clock.schedule_once(lambda dt: loading_popup.dismiss(), 0)

                if result['success']:
                    Clock.schedule_once(lambda dt: self.show_popup('نجاح', result['message']), 0)
                    self.save_operation(product, msisdn, 'success')
                else:
                    self.points += 1
                    self.update_points()
                    Clock.schedule_once(lambda dt: self.show_popup('فشل', result['message']), 0)
                    self.save_operation(product, msisdn, 'failed')

                Clock.schedule_once(lambda dt: self.show_home(), 0)

            except Exception as e:
                Clock.schedule_once(lambda dt: loading_popup.dismiss(), 0)
                self.points += 1
                self.update_points()
                Clock.schedule_once(lambda dt: self.show_popup('خطأ', str(e)), 0)

        threading.Thread(target=charge_thread).start()

    def call_vodafone_api(self, msisdn, pin, product_id):
        session = requests.Session()

        headers_base = {
            'User-Agent': 'okhttp/4.12.0',
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ar',
            'x-agent-operatingsystem': '13',
            'x-agent-device': 'Android Device',
            'x-agent-version': '2026.4.1',
            'x-agent-build': '1139',
        }

        resp1 = session.get(
            'https://mobile.vodafone.com.eg/checkSeamless/realms/vf-realm/protocol/openid-connect/auth',
            params={'client_id': 'ana-vodafone-app-seamless'},
            headers=headers_base,
            timeout=30
        )

        if resp1.status_code != 200:
            return {'success': False, 'message': 'فشل الاتصال الأولي بفودافون\nتأكد من تشغيل داتا فودافون'}

        seamless_token = resp1.json().get('seamlessToken')

        headers_token = headers_base.copy()
        headers_token.update({
            'seamlessToken': seamless_token,
            'clientId': 'AnaVodafoneAndroid',
            'silentLogin': 'true',
            'firstTimeLogin': 'true',
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        token_data = {
            'grant_type': 'password',
            'client_secret': VODAFONE_CLIENT_SECRET,
            'client_id': VODAFONE_CLIENT_ID
        }

        resp2 = session.post(
            'https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token',
            data=token_data,
            headers=headers_token,
            timeout=30
        )

        if resp2.status_code != 200:
            return {'success': False, 'message': 'فشل تسجيل الدخول\nتأكد من فتح داتا فودافون'}

        access_token = resp2.json().get('access_token')

        headers_order = headers_token.copy()
        headers_order.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'api-host': 'ProductOrderingManagement',
            'useCase': 'CashFakkaAndMared',
            'api-version': 'v2',
            'msisdn': msisdn
        })

        order_body = {
            "channel": {"name": "MobileApp"},
            "orderItem": [{
                "action": "insert",
                "id": product_id,
                "product": {
                    "characteristic": [
                        {"name": "PaymentMethod", "value": "VFCash"},
                        {"name": "USE_EMONEY", "value": "False"},
                        {"name": "MerchantCode", "value": ""}
                    ],
                    "id": product_id,
                    "relatedParty": [
                        {"id": msisdn.replace("0", "", 1), "name": "MSISDN", "role": "Subscriber"},
                        {"id": msisdn, "name": "Receiver", "role": "Receiver"}
                    ]
                },
                "@type": product_id,
                "eCode": 0
            }],
            "relatedParty": [{"id": pin, "name": "pin", "role": "Requestor"}],
            "@type": "CashFakkaAndMared"
        }

        resp3 = session.post(
            'https://mobile.vodafone.com.eg/services/dxl/pom/productOrder',
            json=order_body,
            headers=headers_order,
            timeout=30
        )

        result = resp3.json()

        if resp3.status_code == 200:
            return {'success': True, 'message': 'تم الشحن بنجاح!'}
        elif result.get('code') == '6051':
            balance = next((item['value'] for item in result.get('characteristic', []) if item['name'] == 'RemainingBalance'), 'غير معروف')
            return {'success': False, 'message': f'لا يوجد رصيد كافي\nرصيدك: {balance} جنيه'}
        else:
            return {'success': False, 'message': result.get('reason', 'خطأ غير معروف')}

    def update_points(self):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }
            requests.patch(
                f'{SUPABASE_URL}/rest/v1/users?phone=eq.{self.user_phone}',
                headers=headers,
                json={'points': self.points},
                timeout=10
            )
        except:
            pass

    def save_operation(self, product, phone, status):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }
            requests.post(
                f'{SUPABASE_URL}/rest/v1/operations',
                headers=headers,
                json={
                    'user_phone': self.user_phone,
                    'product': product['name'],
                    'product_id': product['id'],
                    'price': product['price'],
                    'target_phone': phone,
                    'status': status,
                    'created_at': datetime.now().isoformat()
                },
                timeout=10
            )
        except:
            pass

    def show_history(self, instance=None):
        content = BoxLayout(orientation='vertical', spacing=15, padding=25)

        title = Label(
            text='[b]📋 سجل العمليات[/b]',
            markup=True,
            font_size='22sp',
            size_hint_y=None,
            height=60,
            font_name=FONT_NAME,
            color=(1, 1, 1, 1)
        )
        content.add_widget(title)

        history = self.get_user_history()

        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', spacing=15, padding=15, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        if not history:
            layout.add_widget(Label(
                text='لا توجد عمليات حتى الآن',
                font_size='16sp',
                color=(0.7, 0.7, 0.7, 1),
                font_name=FONT_NAME
            ))
        else:
            for item in history:
                status_text = '✅ نجاح' if item['status'] == 'success' else '❌ فشل'

                card = BoxLayout(orientation='vertical', spacing=8, padding=20, size_hint_y=None, height=150)

                info_text = f'[b]{item["product"]}[/b]\n📱 {item["target_phone"]}\n💰 {item["price"]} جنيه | {status_text}'
                info = Label(
                    text=info_text,
                    markup=True,
                    font_size='15sp',
                    color=(1, 1, 1, 1),
                    font_name=FONT_NAME
                )
                card.add_widget(info)
                layout.add_widget(card)

        scroll.add_widget(layout)
        content.add_widget(scroll)

        close_btn = Button(
            text='إغلاق',
            size_hint_y=None,
            height=65,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='16sp',
            font_name=FONT_NAME
        )

        popup = Popup(title='السجل', content=content, size_hint=(0.9, 0.85), title_font=FONT_NAME)
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def get_user_history(self):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/operations?user_phone=eq.{self.user_phone}&order=created_at.desc&limit=50',
                headers=headers,
                timeout=10
            )
            return response.json()
        except:
            return []

    def show_admin_panel(self, instance=None):
        self.main_layout.clear_widgets()

        title = Label(
            text='[b][color=E60000]⚙️ لوحة تحكم الأدمن[/color][/b]',
            markup=True,
            font_size='26sp',
            size_hint_y=None,
            height=70,
            font_name=FONT_NAME
        )
        self.main_layout.add_widget(title)

        stats = self.get_admin_stats()
        stats_text = f'📊 إجمالي اليوم: {stats["today_total"]} جنيه | ⭐ النقاط المباعة: {stats["points_sold"]}'
        stats_label = Label(
            text=stats_text,
            font_size='15sp',
            color=(0.97, 0.79, 0.28, 1),
            size_hint_y=None,
            height=50,
            font_name=FONT_NAME
        )
        self.main_layout.add_widget(stats_label)

        pending = self.get_pending_requests()

        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', spacing=20, padding=20, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        if not pending:
            layout.add_widget(Label(
                text='لا توجد طلبات قيد الانتظار',
                font_size='16sp',
                color=(0.7, 0.7, 0.7, 1),
                font_name=FONT_NAME
            ))
        else:
            for req in pending:
                card = BoxLayout(orientation='vertical', spacing=12, padding=25, size_hint_y=None, height=240)

                info_text = f'👤 [b]{req["user_phone"]}[/b]\n⭐ {req["points"]} نقطة - 💰 {req["price"]} جنيه\n⏳ في الانتظار'
                info = Label(
                    text=info_text,
                    markup=True,
                    font_size='16sp',
                    color=(1, 1, 1, 1),
                    font_name=FONT_NAME
                )
                card.add_widget(info)

                btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=15)

                approve_btn = Button(
                    text='✅ تأكيد',
                    background_color=(0, 0.7, 0, 1),
                    color=(1, 1, 1, 1),
                    font_size='16sp',
                    font_name=FONT_NAME
                )
                approve_btn.bind(on_press=lambda x, r=req: self.approve_recharge(r))

                reject_btn = Button(
                    text='❌ رفض',
                    background_color=(0.8, 0, 0, 1),
                    color=(1, 1, 1, 1),
                    font_size='16sp',
                    font_name=FONT_NAME
                )
                reject_btn.bind(on_press=lambda x, r=req: self.reject_recharge(r))

                btn_layout.add_widget(approve_btn)
                btn_layout.add_widget(reject_btn)
                card.add_widget(btn_layout)

                layout.add_widget(card)

        scroll.add_widget(layout)
        self.main_layout.add_widget(scroll)

        back_btn = Button(
            text='⬅️ رجوع للرئيسية',
            size_hint_y=None,
            height=65,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='16sp',
            font_name=FONT_NAME
        )
        back_btn.bind(on_press=lambda x: self.show_home())
        self.main_layout.add_widget(back_btn)

    def get_pending_requests(self):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/recharge_requests?status=eq.pending&order=created_at.desc',
                headers=headers,
                timeout=10
            )
            return response.json()
        except:
            return []

    def get_admin_stats(self):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
            today = datetime.now().strftime('%Y-%m-%d')

            resp1 = requests.get(
                f'{SUPABASE_URL}/rest/v1/recharge_requests?status=eq.approved&created_at=gte.{today}',
                headers=headers,
                timeout=10
            )
            today_data = resp1.json()
            today_total = sum(item['price'] for item in today_data)
            points_sold = sum(item['points'] for item in today_data)

            return {'today_total': today_total, 'points_sold': points_sold}
        except:
            return {'today_total': 0, 'points_sold': 0}

    def approve_recharge(self, request):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }

            requests.patch(
                f'{SUPABASE_URL}/rest/v1/recharge_requests?id=eq.{request["id"]}',
                headers=headers,
                json={'status': 'approved'},
                timeout=10
            )

            resp = requests.get(
                f'{SUPABASE_URL}/rest/v1/users?phone=eq.{request["user_phone"]}',
                headers=headers,
                timeout=10
            )
            user_data = resp.json()

            if user_data:
                new_points = user_data[0].get('points', 0) + request['points']
                requests.patch(
                    f'{SUPABASE_URL}/rest/v1/users?phone=eq.{request["user_phone"]}',
                    headers=headers,
                    json={'points': new_points},
                    timeout=10
                )

            self.show_popup('تم!', f'✅ تم تأكيد شحن {request["points"]} نقطة\nلـ {request["user_phone"]}')
            self.show_admin_panel()

        except Exception as e:
            self.show_popup('خطأ', str(e))

    def reject_recharge(self, request):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }

            requests.patch(
                f'{SUPABASE_URL}/rest/v1/recharge_requests?id=eq.{request["id"]}',
                headers=headers,
                json={'status': 'rejected'},
                timeout=10
            )

            self.show_popup('تم', f'❌ تم رفض الطلب\nلـ {request["user_phone"]}')
            self.show_admin_panel()

        except Exception as e:
            self.show_popup('خطأ', str(e))

    def show_recharge_dialog(self, instance=None):
        content = BoxLayout(orientation='vertical', spacing=15, padding=30)

        content.add_widget(Label(
            text='اختر الباقة:',
            font_size='20sp',
            color=(1, 1, 1, 1),
            font_name=FONT_NAME
        ))
        content.add_widget(Label(size_hint_y=None, height=15))

        for pkg in POINTS_PACKAGES:
            btn = Button(
                text=pkg['label'],
                size_hint_y=None,
                height=65,
                background_color=(0.97, 0.79, 0.28, 0.2),
                color=(0.97, 0.79, 0.28, 1),
                font_size='16sp',
                font_name=FONT_NAME
            )
            btn.bind(on_press=lambda x, p=pkg: self.send_recharge_request(p))
            content.add_widget(btn)

        content.add_widget(Label(size_hint_y=None, height=15))

        close_btn = Button(
            text='إلغاء',
            size_hint_y=None,
            height=65,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='16sp',
            font_name=FONT_NAME
        )

        popup = Popup(title='شحن نقاط', content=content, size_hint=(0.9, 0.8), title_font=FONT_NAME)
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def send_recharge_request(self, package):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }

            requests.post(
                f'{SUPABASE_URL}/rest/v1/recharge_requests',
                headers=headers,
                json={
                    'user_phone': self.user_phone,
                    'points': package['points'],
                    'price': package['price'],
                    'status': 'pending',
                    'admin_phone': ADMIN_PHONE,
                    'created_at': datetime.now().isoformat()
                },
                timeout=10
            )

            self.open_whatsapp(package)

            self.show_popup('تم إرسال الطلب', '✅ تم إرسال طلبك\nفي انتظار تأكيد الأدمن')

        except Exception as e:
            self.show_popup('خطأ', str(e))

    def open_whatsapp(self, package):
        try:
            import webbrowser
            import urllib.parse

            msg = (
                "🔔 طلب شحن نقاط جديد!" + "\n\n" +
                "👤 العميل: " + self.user_phone + "\n" +
                "⭐ النقاط: " + str(package['points']) + "\n" +
                "💰 المبلغ: " + str(package['price']) + " جنيه" + "\n\n" +
                "📱 افتح التطبيق للتأكيد"
            )

            url = "https://wa.me/2" + ADMIN_PHONE + "?text=" + urllib.parse.quote(msg)
            webbrowser.open(url)

        except Exception as e:
            print("WhatsApp error: " + str(e))

    def show_points_dialog(self, instance=None):
        content = BoxLayout(orientation='vertical', spacing=20, padding=30)
        content.add_widget(Label(
            text=f'[b][color=F7C948]⭐ {self.points} نقطة[/color][/b]',
            markup=True,
            font_size='32sp',
            font_name=FONT_NAME
        ))
        content.add_widget(Label(
            text='كل شحنة تخصم نقطة واحدة',
            font_size='16sp',
            color=(0.7, 0.7, 0.7, 1),
            font_name=FONT_NAME
        ))
        content.add_widget(Label(size_hint_y=None, height=20))

        close_btn = Button(
            text='إغلاق',
            size_hint_y=None,
            height=65,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='16sp',
            font_name=FONT_NAME
        )

        popup = Popup(title='رصيد النقاط', content=content, size_hint=(0.8, 0.5), title_font=FONT_NAME)
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=30, spacing=20)
        content.add_widget(Label(text=message, font_size='18sp', font_name=FONT_NAME))

        btn = Button(text='حسناً', size_hint_y=None, height=65, font_size='16sp', font_name=FONT_NAME)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5), title_font=FONT_NAME)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

if __name__ == '__main__':
    VodafoneApp().run()
