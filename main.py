#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mostafa - Vodafone Charge App
KivyMD version with full Arabic support
"""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.list import MDList, OneLineListItem
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.utils import platform
from kivy.metrics import dp
import requests
import json
import threading
import os
import time
from datetime import datetime
from collections import defaultdict

# ==================== ARABIC TEXT FIX ====================
def ar(text):
    """Arabic text handler - KivyMD handles RTL better"""
    return text

# ==================== COLORS ====================
COLOR_BG = (0.05, 0.05, 0.05, 1)
COLOR_CARD = (0.12, 0.12, 0.12, 1)
COLOR_RED = (0.9, 0.22, 0.27, 1)
COLOR_GOLD = (0.96, 0.64, 0.38, 1)
COLOR_TEXT = (1, 1, 1, 1)
COLOR_TEXT_GRAY = (0.6, 0.6, 0.6, 1)
COLOR_GREEN = (0.2, 0.8, 0.4, 1)

# ==================== CONFIG ====================
SUPABASE_URL = 'https://qippgvyupkeruvzkfdkz.supabase.co'
SUPABASE_KEY = 'sb_publishable_zUyj8k4QKYqognMAL6I1Qw_8cBGPFyf'
VODAFONE_CLIENT_SECRET = 'b86e30a8-ae29-467a-a71f-65c73f2ff5e3'
VODAFONE_CLIENT_ID = 'cash-app'
ADMIN_PHONE = '01019502983'

# ==================== PRODUCTS (All 22) ====================
FAKKA_PRODUCTS = [
    {"id": "Fakka_2.5_Unite", "name": "فكة 2.5", "price": 2.5, "units": 45, "validity": "1 يوم", "desc": "45 وحدة + 20 واتساب"},
    {"id": "Fakka_4.25_Unite", "name": "فكة 4.25", "price": 4.25, "units": 190, "validity": "1 يوم", "desc": "190 وحدة/صباحاً"},
    {"id": "Fakka_5_Unite", "name": "فكة 5", "price": 5, "units": 225, "validity": "1 يوم", "desc": "225 وحدة/صباحاً"},
    {"id": "Fakka_6_Unite", "name": "فكة 6", "price": 6, "units": 0, "validity": "1 يوم", "desc": ""},
    {"id": "Fakka_7_Unite", "name": "فكة 7", "price": 7, "units": 300, "validity": "3 أيام", "desc": "300 وحدة/صباحاً"},
    {"id": "Fakka_9_Unite", "name": "فكة 9", "price": 9, "units": 400, "validity": "4 أيام", "desc": "400 وحدة + 50 واتساب"},
    {"id": "Fakka_10_Unite", "name": "فكة 10", "price": 10, "units": 450, "validity": "7 أيام", "desc": "450 وحدة/صباحاً"},
    {"id": "Fakka_10.5_Unite", "name": "فكة 10.5", "price": 10.5, "units": 0, "validity": "7 أيام", "desc": ""},
    {"id": "Fakka_11.5_Unite", "name": "فكة 11.5", "price": 11.5, "units": 450, "validity": "7 أيام", "desc": "450 وحدة/صباحاً"},
    {"id": "Fakka_12_Unite", "name": "فكة 12", "price": 12, "units": 0, "validity": "7 أيام", "desc": ""},
    {"id": "Fakka_12.5_Unite", "name": "فكة 12.5", "price": 12.5, "units": 0, "validity": "7 أيام", "desc": ""},
    {"id": "Fakka_13_Unite", "name": "فكة 13", "price": 13, "units": 0, "validity": "7 أيام", "desc": ""},
    {"id": "Fakka_13.5_Unite", "name": "فكة 13.5", "price": 13.5, "units": 625, "validity": "7 أيام", "desc": "625 وحدة/صباحاً"},
    {"id": "Fakka_15_Unite", "name": "فكة 15", "price": 15, "units": 550, "validity": "7 أيام", "desc": "550 وحدة/صباحاً"},
    {"id": "Fakka_15.5_Unite", "name": "فكة 15.5", "price": 15.5, "units": 0, "validity": "7 أيام", "desc": ""},
    {"id": "Fakka_16.5_Unite", "name": "فكة 16.5", "price": 16.5, "units": 0, "validity": "7 أيام", "desc": ""},
    {"id": "Fakka_17.5_Unite", "name": "فكة 17.5", "price": 17.5, "units": 650, "validity": "10 أيام", "desc": "650 وحدة/صباحاً"},
    {"id": "Fakka_19.5_Unite", "name": "فكة 19.5", "price": 19.5, "units": 0, "validity": "10 أيام", "desc": ""},
    {"id": "Fakka_20_Unite", "name": "فكة 20", "price": 20, "units": 750, "validity": "10 أيام", "desc": "750 وحدة/صباحاً"},
    {"id": "Fakka_26_Unite", "name": "فكة 26", "price": 26, "units": 0, "validity": "شهر", "desc": ""},
]

MARED_PRODUCTS = [
    {"id": "Mared_10_Flexs", "name": "مارد 10 فليكس", "price": 10, "units": 10, "type": "فليكس", "validity": "24 ساعة", "desc": ""},
    {"id": "Mared_10_Minuts", "name": "مارد 10 دقائق", "price": 10, "units": 10, "type": "دقائق", "validity": "24 ساعة", "desc": ""},
    {"id": "Mared_10_Social", "name": "مارد 10 سوشيال", "price": 10, "units": 10, "type": "سوشيال", "validity": "24 ساعة", "desc": ""},
]

ALL_PRODUCTS = FAKKA_PRODUCTS + MARED_PRODUCTS

POINTS_PACKAGES = [
    {"points": 10, "price": 20, "label": "10 نقاط - 20 جنيه"},
    {"points": 25, "price": 50, "label": "25 نقطة - 50 جنيه"},
    {"points": 50, "price": 100, "label": "50 نقطة - 100 جنيه"},
    {"points": 100, "price": 200, "label": "100 نقطة - 200 جنيه"},
]

# ==================== SIM NUMBER ====================
def get_sim_number():
    if platform != 'android':
        return None
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        TelephonyManager = autoclass('android.telephony.TelephonyManager')
        activity = PythonActivity.mActivity
        tm = activity.getSystemService(Context.TELEPHONY_SERVICE)
        number = tm.getLine1Number()
        if number:
            number = number.replace('+20', '0').replace(' ', '').replace('-', '')
            if len(number) == 11 and number.startswith('01'):
                return number
    except Exception as e:
        print(f"SIM error: {e}")
    return None

# ==================== APP ====================
class VodafoneApp(MDApp):
    user_phone = StringProperty('')
    points = NumericProperty(0)
    is_admin = False
    dialog = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.accent_palette = "Orange"
        Window.clearcolor = COLOR_BG
        self.title = 'Mostafa - شحن فودافون'

        # Main screen
        self.screen = MDScreen()
        self.main_layout = MDBoxLayout(orientation='vertical', padding=0, spacing=0)
        self.screen.add_widget(self.main_layout)

        # Try auto-login
        auto_phone = get_sim_number()
        if auto_phone:
            self.user_phone = auto_phone
            self.is_admin = (auto_phone == ADMIN_PHONE)
            self.load_user_data()
            if self.is_admin:
                self.show_admin_panel()
            else:
                self.show_home()
        else:
            self.show_login()

        return self.screen

    # ==================== LOGIN ====================
    def show_login(self):
        self.main_layout.clear_widgets()

        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Logo
        logo = MDLabel(
            text='[b]MOSTAFA[/b]',
            markup=True,
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_RED,
            font_style='H3',
            size_hint_y=None,
            height=dp(80)
        )
        layout.add_widget(logo)

        subtitle = MDLabel(
            text='شحن كروت فودافون',
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT_GRAY,
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(subtitle)

        # Phone input
        self.phone_input = MDTextField(
            hint_text='رقم الهاتف (01XXXXXXXXX)',
            input_filter='int',
            size_hint_y=None,
            height=dp(60),
            mode='rectangle',
            helper_text='أدخل 11 رقم',
            helper_text_mode='on_focus'
        )
        layout.add_widget(self.phone_input)

        # Login button
        login_btn = MDRaisedButton(
            text='دخول',
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=COLOR_RED,
            text_color=COLOR_TEXT,
            font_style='H6'
        )
        login_btn.bind(on_press=self.do_login)
        layout.add_widget(login_btn)

        # Auto detect
        auto_btn = MDRoundFlatButton(
            text='الكشف التلقائي عن الرقم',
            size_hint=(1, None),
            height=dp(45),
            text_color=(0.2, 0.5, 0.9, 1)
        )
        auto_btn.bind(on_press=self.try_auto_login)
        layout.add_widget(auto_btn)

        self.main_layout.add_widget(layout)

    def try_auto_login(self, instance):
        auto_phone = get_sim_number()
        if auto_phone:
            self.user_phone = auto_phone
            self.is_admin = (auto_phone == ADMIN_PHONE)
            self.load_user_data()
            if self.is_admin:
                self.show_admin_panel()
            else:
                self.show_home()
        else:
            self.show_snackbar('لم يتم العثور على رقم الشريحة')

    def do_login(self, instance):
        phone = self.phone_input.text
        if len(phone) != 11 or not phone.startswith('01'):
            self.show_snackbar('رقم الهاتف غير صحيح')
            return
        self.user_phone = phone
        self.is_admin = (phone == ADMIN_PHONE)
        self.load_user_data()
        if self.is_admin:
            self.show_admin_panel()
        else:
            self.show_home()

    def load_user_data(self):
        try:
            headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/users?phone=eq.{self.user_phone}&select=*',
                headers=headers, timeout=10
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
            print(f'Error: {e}')
            self.points = 0

    # ==================== HOME ====================
    def show_home(self):
        self.main_layout.clear_widgets()

        scroll = MDScrollView()
        content = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # Top bar
        top_bar = MDTopAppBar(
            title='Mostafa',
            md_bg_color=COLOR_RED,
            specific_text_color=COLOR_TEXT,
            left_action_items=[['menu', lambda x: None]],
            right_action_items=[['refresh', lambda x: self.show_home()]]
        )
        content.add_widget(top_bar)

        # Points card - WIDER
        points_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(240),
            padding=dp(20),
            spacing=dp(10),
            md_bg_color=COLOR_CARD,
            radius=[dp(16), dp(16), dp(16), dp(16)]
        )

        welcome = MDLabel(
            text='مرحباً',
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_GREEN,
            font_style='H5',
            size_hint_y=None,
            height=dp(40)
        )
        points_card.add_widget(welcome)

        loading_text = MDLabel(
            text='انتظر حتى يتم تحميل رقمك...',
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT_GRAY,
            size_hint_y=None,
            height=dp(25)
        )
        points_card.add_widget(loading_text)

        points_num = MDLabel(
            text=str(self.points),
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_RED,
            font_style='H2',
            bold=True,
            size_hint_y=None,
            height=dp(70)
        )
        points_card.add_widget(points_num)

        points_label = MDLabel(
            text='نقاطك',
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT_GRAY,
            size_hint_y=None,
            height=dp(25)
        )
        points_card.add_widget(points_label)

        # Action buttons row
        btn_row = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        history_btn = MDRaisedButton(
            text='سجل العمليات',
            size_hint=(1, 1),
            md_bg_color=COLOR_RED,
            text_color=COLOR_TEXT
        )
        recharge_points_btn = MDRaisedButton(
            text='شحن نقاط',
            size_hint=(1, 1),
            md_bg_color=COLOR_RED,
            text_color=COLOR_TEXT
        )
        contact_btn = MDRaisedButton(
            text='تواصل معنا',
            size_hint=(1, 1),
            md_bg_color=COLOR_RED,
            text_color=COLOR_TEXT
        )

        recharge_points_btn.bind(on_press=self.show_recharge_dialog)
        contact_btn.bind(on_press=lambda x: self.show_snackbar(f'WhatsApp: {ADMIN_PHONE}'))

        btn_row.add_widget(history_btn)
        btn_row.add_widget(recharge_points_btn)
        btn_row.add_widget(contact_btn)
        points_card.add_widget(btn_row)

        content.add_widget(points_card)

        # Big recharge button - WIDER
        big_recharge = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=dp(15),
            md_bg_color=COLOR_CARD,
            radius=[dp(16), dp(16), dp(16), dp(16)],
            ripple_behavior=True
        )
        big_recharge.bind(on_press=self.show_recharge_balance_dialog)

        big_recharge.add_widget(MDLabel(
            text='[b]شحن الرصيد[/b]',
            markup=True,
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT,
            font_style='H5',
            size_hint_y=0.6
        ))
        big_recharge.add_widget(MDLabel(
            text='شحن رصيد فودافون',
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT_GRAY,
            size_hint_y=0.4
        ))
        content.add_widget(big_recharge)

        # Title
        content.add_widget(MDLabel(
            text='اختر الكارت',
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT,
            font_style='H5',
            size_hint_y=None,
            height=dp(40),
            bold=True
        ))

        # Products grid - 3 columns WIDER cards
        products_grid = MDGridLayout(
            cols=3,
            spacing=dp(12),
            padding=dp(5),
            size_hint_y=None,
            adaptive_height=True
        )

        for product in ALL_PRODUCTS:
            card = self.create_product_card(product)
            products_grid.add_widget(card)

        content.add_widget(products_grid)
        scroll.add_widget(content)
        self.main_layout.add_widget(scroll)

    def create_product_card(self, product):
        """Create wider product card"""
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            padding=dp(12),
            spacing=dp(5),
            md_bg_color=COLOR_CARD,
            radius=[dp(16), dp(16), dp(16), dp(16)],
            ripple_behavior=True,
            elevation=2
        )

        # Product name
        name = MDLabel(
            text=f'[b]{product["name"]}[/b]',
            markup=True,
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT,
            font_style='H6',
            size_hint_y=0.35
        )
        card.add_widget(name)

        # Description
        desc_text = product.get('desc', '') or f"{product.get('units', 0)} وحدة/صباحاً"
        desc = MDLabel(
            text=desc_text,
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT_GRAY,
            font_style='Caption',
            size_hint_y=0.35
        )
        card.add_widget(desc)

        # Validity
        validity = MDLabel(
            text=product['validity'],
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT_GRAY,
            font_style='Caption',
            size_hint_y=0.30
        )
        card.add_widget(validity)

        # Make clickable
        card.bind(on_press=lambda x, p=product: self.show_charge_dialog(p))

        return card

    def show_recharge_balance_dialog(self, instance):
        if not self.dialog:
            content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), size_hint_y=None, height=dp(350))

            content.add_widget(MDLabel(
                text='شحن رصيد فودافون',
                halign='center',
                theme_text_color='Custom',
                text_color=COLOR_TEXT,
                font_style='H5',
                size_hint_y=None,
                height=dp(40)
            ))

            amount_input = MDTextField(
                hint_text='المبلغ بالجنيه',
                input_filter='float',
                size_hint_y=None,
                height=dp(50),
                mode='rectangle'
            )
            content.add_widget(amount_input)

            phone_input = MDTextField(
                hint_text='رقم الهاتف للشحن',
                input_filter='int',
                size_hint_y=None,
                height=dp(50),
                mode='rectangle'
            )
            content.add_widget(phone_input)

            pin_input = MDTextField(
                hint_text='الرقم السري للمحفظة',
                password=True,
                size_hint_y=None,
                height=dp(50),
                mode='rectangle'
            )
            content.add_widget(pin_input)

            self.dialog = MDDialog(
                title='شحن الرصيد',
                type='custom',
                content_cls=content,
                buttons=[
                    MDFlatButton(text='إلغاء', theme_text_color='Custom', text_color=COLOR_TEXT_GRAY, on_press=lambda x: self.dialog.dismiss()),
                    MDRaisedButton(text='تأكيد', md_bg_color=COLOR_RED, text_color=COLOR_TEXT, on_press=lambda x: self.do_balance_recharge(amount_input.text, phone_input.text, pin_input.text))
                ]
            )
        self.dialog.open()

    def do_balance_recharge(self, amount, phone, pin):
        if not amount or not phone or not pin:
            self.show_snackbar('اكمل جميع البيانات')
            return
        self.dialog.dismiss()
        self.dialog = None
        self.show_snackbar('جاري تنفيذ طلب شحن الرصيد...')

    def show_charge_dialog(self, product):
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), size_hint_y=None, height=dp(300))

        content.add_widget(MDLabel(
            text=f'[b]{product["name"]}[/b]
سيتم خصم نقطة واحدة',
            markup=True,
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT,
            font_style='H6',
            size_hint_y=None,
            height=dp(60)
        ))

        target = MDTextField(
            hint_text='رقم الهاتف للشحن',
            input_filter='int',
            size_hint_y=None,
            height=dp(50),
            mode='rectangle'
        )
        content.add_widget(target)

        pin = MDTextField(
            hint_text='الرقم السري للمحفظة (4 أرقام)',
            password=True,
            input_filter='int',
            size_hint_y=None,
            height=dp(50),
            mode='rectangle'
        )
        content.add_widget(pin)

        dialog = MDDialog(
            title=f'شحن {product["name"]}',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(text='إلغاء', theme_text_color='Custom', text_color=COLOR_TEXT_GRAY, on_press=lambda x: dialog.dismiss()),
                MDRaisedButton(text='تأكيد الشحن', md_bg_color=COLOR_RED, text_color=COLOR_TEXT, on_press=lambda x: self.process_charge(target.text, pin.text, product, dialog))
            ]
        )
        dialog.open()

    def process_charge(self, target, pin, product, dialog):
        if self.points <= 0:
            self.show_snackbar('لا توجد نقاط كافية')
            return
        if len(target) != 11 or not target.startswith('01'):
            self.show_snackbar('رقم الهاتف غير صحيح')
            return
        if len(pin) != 4:
            self.show_snackbar('الرقم السري يجب أن يكون 4 أرقام')
            return
        dialog.dismiss()
        self.charge_card(target, pin, product)

    def charge_card(self, msisdn, pin, product):
        self.dialog = MDDialog(
            title='جاري الشحن...',
            type='custom',
            content_cls=MDBoxLayout(
                MDProgressBar(value=50, size_hint_y=None, height=dp(20)),
                padding=dp(30),
                size_hint_y=None,
                height=dp(100)
            )
        )
        self.dialog.open()

        def thread():
            try:
                self.points -= 1
                self.update_points()
                result = self.call_vodafone_api(msisdn, pin, product['id'])

                Clock.schedule_once(lambda dt: self.dialog.dismiss(), 0)
                self.dialog = None

                if result['success']:
                    Clock.schedule_once(lambda dt: self.show_snackbar('✅ ' + result['message']), 0)
                    self.save_operation(product, msisdn, 'success')
                else:
                    self.points += 1
                    self.update_points()
                    Clock.schedule_once(lambda dt: self.show_snackbar('❌ ' + result['message']), 0)
                    self.save_operation(product, msisdn, 'failed')

                Clock.schedule_once(lambda dt: self.show_home(), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.dialog.dismiss() if self.dialog else None, 0)
                self.dialog = None
                self.points += 1
                self.update_points()
                Clock.schedule_once(lambda dt: self.show_snackbar(f'خطأ: {str(e)}'), 0)

        threading.Thread(target=thread, daemon=True).start()

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
            headers=headers_base, timeout=30
        )
        if resp1.status_code != 200:
            return {'success': False, 'message': 'فشل الاتصال الأولي'}

        seamless_token = resp1.json().get('seamlessToken')

        headers_token = headers_base.copy()
        headers_token.update({
            'seamlessToken': seamless_token,
            'clientId': 'AnaVodafoneAndroid',
            'silentLogin': 'true',
            'firstTimeLogin': 'true',
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        resp2 = session.post(
            'https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token',
            data={'grant_type': 'password', 'client_secret': VODAFONE_CLIENT_SECRET,
                  'client_id': VODAFONE_CLIENT_ID},
            headers=headers_token, timeout=30
        )
        if resp2.status_code != 200:
            return {'success': False, 'message': 'فشل تسجيل الدخول
تأكد من فتح داتا فودافون'}

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

        api_msisdn = msisdn[1:] if msisdn.startswith('0') else msisdn

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
                        {"id": api_msisdn, "name": "MSISDN", "role": "Subscriber"},
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
            json=order_body, headers=headers_order, timeout=30
        )

        result = resp3.json()

        if resp3.status_code == 200:
            return {'success': True, 'message': 'تم الشحن بنجاح!'}
        elif result.get('code') == '6051':
            balance = next((item['value'] for item in result.get('characteristic', []) 
                          if item.get('name') == 'RemainingBalance'), 'غير معروف')
            return {'success': False, 'message': f'لا يوجد رصيد كافي
رصيدك: {balance} جنيه'}
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
                json={'points': self.points, 'updated_at': datetime.now().isoformat()},
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

    def show_recharge_dialog(self, instance=None):
        content = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20), size_hint_y=None, height=dp(350))

        content.add_widget(MDLabel(
            text='اختر باقة الشحن:',
            halign='center',
            theme_text_color='Custom',
            text_color=COLOR_TEXT,
            font_style='H6',
            size_hint_y=None,
            height=dp(40)
        ))

        for pkg in POINTS_PACKAGES:
            btn = MDRaisedButton(
                text=pkg['label'],
                size_hint=(1, None),
                height=dp(55),
                md_bg_color=(0.96, 0.64, 0.38, 0.2),
                text_color=COLOR_GOLD
            )
            btn.bind(on_press=lambda x, p=pkg: self.send_recharge_request(p))
            content.add_widget(btn)

        dialog = MDDialog(
            title='شحن نقاط',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(text='إلغاء', theme_text_color='Custom', text_color=COLOR_TEXT_GRAY, on_press=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()

    def send_recharge_request(self, package):
        try:
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }
            requests.post(
                f'{SUPABASE_URL}/rest/v1/charge_requests',
                headers=headers,
                json={
                    'user_phone': self.user_phone,
                    'points': package['points'],
                    'price': package['price'],
                    'status': 'pending',
                    'created_at': datetime.now().isoformat()
                },
                timeout=10
            )
        except:
            pass

        msg = f"🔔 طلب شحن نقاط!
👤 {self.user_phone}
⭐ {package['points']} نقطة
💰 {package['price']} جنيه"
        try:
            import urllib.parse, webbrowser
            webbrowser.open(f'https://wa.me/2{ADMIN_PHONE}?text={urllib.parse.quote(msg)}')
        except:
            pass

        self.show_snackbar('تم إرسال طلبك')

    # ==================== ADMIN PANEL ====================
    def show_admin_panel(self):
        self.main_layout.clear_widgets()

        top_bar = MDTopAppBar(
            title='لوحة التحكم',
            md_bg_color=COLOR_RED,
            specific_text_color=COLOR_TEXT,
            left_action_items=[['arrow-left', lambda x: self.show_login()]],
            right_action_items=[['refresh', lambda x: self.load_admin_requests()]]
        )
        self.main_layout.add_widget(top_bar)

        stats = MDBoxLayout(size_hint_y=None, height=dp(40), padding=dp(10))
        self.pending_label = MDLabel(
            text='جاري التحميل...',
            theme_text_color='Custom',
            text_color=COLOR_GOLD,
            font_style='H6'
        )
        stats.add_widget(self.pending_label)
        self.main_layout.add_widget(stats)

        self.requests_layout = MDBoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.requests_layout)

        self.load_admin_requests()
        Clock.schedule_interval(lambda dt: self.load_admin_requests(), 30)

    def load_admin_requests(self, instance=None):
        def fetch():
            try:
                headers = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}
                resp = requests.get(
                    f'{SUPABASE_URL}/rest/v1/charge_requests?status=eq.pending&order=created_at.desc',
                    headers=headers, timeout=10
                )
                requests_list = resp.json()

                users_resp = requests.get(
                    f'{SUPABASE_URL}/rest/v1/users?select=phone,points',
                    headers=headers, timeout=10
                )
                users = {u['phone']: u['points'] for u in users_resp.json()}

                Clock.schedule_once(lambda dt: self.display_requests(requests_list, users), 0)
            except:
                Clock.schedule_once(lambda dt: self.show_snackbar('فشل تحميل الطلبات'), 0)

        threading.Thread(target=fetch, daemon=True).start()

    def display_requests(self, requests_list, users):
        self.requests_layout.clear_widgets()
        self.pending_label.text = f'📋 طلبات قيد الانتظار: {len(requests_list)}'

        if not requests_list:
            self.requests_layout.add_widget(MDLabel(
                text='لا توجد طلبات',
                halign='center',
                theme_text_color='Custom',
                text_color=COLOR_TEXT_GRAY,
                font_style='H5'
            ))
            return

        scroll = MDScrollView()
        layout = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for req in requests_list:
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(180),
                padding=dp(15),
                spacing=dp(10),
                md_bg_color=COLOR_CARD,
                radius=[dp(16), dp(16), dp(16), dp(16)]
            )

            info = MDLabel(
                text=f'[b]{req["user_phone"]}[/b]
⭐ {req["points"]} نقطة | 💰 {req["price"]} جنيه',
                markup=True,
                theme_text_color='Custom',
                text_color=COLOR_TEXT,
                font_style='H6',
                size_hint_y=None,
                height=dp(80)
            )
            card.add_widget(info)

            btn_row = MDBoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
            reject = MDRaisedButton(
                text='❌ رفض',
                size_hint=(1, 1),
                md_bg_color=(0.8, 0, 0, 1),
                text_color=COLOR_TEXT
            )
            approve = MDRaisedButton(
                text='✅ موافقة',
                size_hint=(1, 1),
                md_bg_color=(0, 0.7, 0.3, 1),
                text_color=COLOR_TEXT
            )

            reject.bind(on_press=lambda x, rid=req['id']: self.handle_request(rid, 'rejected', req['user_phone'], 0))
            approve.bind(on_press=lambda x, rid=req['id'], p=req['user_phone'], pts=req['points']: 
                        self.handle_request(rid, 'approved', p, pts))

            btn_row.add_widget(reject)
            btn_row.add_widget(approve)
            card.add_widget(btn_row)
            layout.add_widget(card)

        scroll.add_widget(layout)
        self.requests_layout.add_widget(scroll)

    def handle_request(self, req_id, status, phone, points_to_add):
        def process():
            try:
                headers = {
                    'apikey': SUPABASE_KEY,
                    'Authorization': f'Bearer {SUPABASE_KEY}',
                    'Content-Type': 'application/json'
                }
                requests.patch(
                    f'{SUPABASE_URL}/rest/v1/charge_requests?id=eq.{req_id}',
                    headers=headers,
                    json={'status': status, 'updated_at': datetime.now().isoformat()},
                    timeout=10
                )

                if status == 'approved':
                    resp = requests.get(
                        f'{SUPABASE_URL}/rest/v1/users?phone=eq.{phone}&select=points',
                        headers=headers, timeout=10
                    )
                    data = resp.json()
                    if data:
                        new_points = data[0]['points'] + points_to_add
                        requests.patch(
                            f'{SUPABASE_URL}/rest/v1/users?phone=eq.{phone}',
                            headers=headers,
                            json={'points': new_points, 'updated_at': datetime.now().isoformat()},
                            timeout=10
                        )

                Clock.schedule_once(lambda dt: self.load_admin_requests(), 0)
                msg = 'تمت الموافقة' if status == 'approved' else 'تم الرفض'
                Clock.schedule_once(lambda dt: self.show_snackbar(msg), 0)
            except:
                Clock.schedule_once(lambda dt: self.show_snackbar('فشل المعالجة'), 0)

        threading.Thread(target=process, daemon=True).start()

    def show_snackbar(self, text):
        MDSnackbar(
            MDLabel(text=text),
            md_bg_color=COLOR_CARD,
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            size_hint_x=0.9
        ).open()

if __name__ == '__main__':
    VodafoneApp().run()
