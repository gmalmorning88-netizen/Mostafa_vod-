#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mostafa - Vodafone Charge App
With built-in Arabic support (no external libraries needed)
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
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle
import requests
import json
import threading
import os
import time
from datetime import datetime
from collections import defaultdict

# ==================== BUILT-IN ARABIC SUPPORT ====================
ARABIC_LETTERS = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويىةئؤءاأإآ ')

def ar(text):
    """
    Built-in Arabic text handler
    Reverses text order for RTL display in Kivy
    """
    if not text:
        return text
    
    # Split into lines and reverse each line
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        chars = list(line)
        # Reverse the order of characters for RTL
        chars.reverse()
        result_lines.append(''.join(chars))
    
    return '\n'.join(result_lines)

# ==================== COLORS ====================
COLOR_BG = (0.05, 0.05, 0.05, 1)
COLOR_CARD = (0.1, 0.1, 0.1, 1)
COLOR_RED = (0.9, 0.22, 0.27, 1)
COLOR_RED_LIGHT = (0.9, 0.22, 0.27, 0.15)
COLOR_GOLD = (0.96, 0.64, 0.38, 1)
COLOR_GOLD_LIGHT = (0.96, 0.64, 0.38, 0.15)
COLOR_TEXT = (1, 1, 1, 1)
COLOR_TEXT_GRAY = (0.6, 0.6, 0.6, 1)
COLOR_GREEN = (0.2, 0.8, 0.4, 1)

# ==================== FONT SETUP ====================
FONT_NAME = 'Roboto'

def setup_font():
    global FONT_NAME
    if platform == 'android':
        android_fonts = [
            '/system/fonts/DroidSansArabic.ttf',
            '/system/fonts/NotoNaskhArabic-Regular.ttf',
            '/system/fonts/NotoSansArabic-Regular.ttf',
            '/system/fonts/NotoSansArabicUI-Regular.ttf',
        ]
        for font_path in android_fonts:
            if os.path.exists(font_path):
                try:
                    LabelBase.register(name='ArabicFont', fn_regular=font_path)
                    FONT_NAME = 'ArabicFont'
                    print(f"Font loaded: {font_path}")
                    return True
                except:
                    pass
    
    # Try bundled fonts
    app_fonts = [
        'Cairo-Regular.ttf',
        os.path.join(os.path.dirname(__file__), 'Cairo-Regular.ttf'),
    ]
    for font_path in app_fonts:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='ArabicFont', fn_regular=font_path)
                FONT_NAME = 'ArabicFont'
                print(f"Font loaded: {font_path}")
                return True
            except:
                pass
    return False

# ==================== CONFIG ====================
SUPABASE_URL = 'https://qippgvyupkeruvzkfdkz.supabase.co'
SUPABASE_KEY = 'sb_publishable_zUyj8k4QKYqognMAL6I1Qw_8cBGPFyf'
VODAFONE_CLIENT_SECRET = 'b86e30a8-ae29-467a-a71f-65c73f2ff5e3'
VODAFONE_CLIENT_ID = 'cash-app'
ADMIN_PHONE = '01019502983'

# ==================== PRODUCTS (All 22) ====================
# Using English IDs for API, Arabic names for display
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

# ==================== CUSTOM WIDGETS ====================
class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = 12
        self.spacing = 4
        with self.canvas.before:
            Color(*COLOR_CARD)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
            self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

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
class VodafoneApp(App):
    user_phone = StringProperty('')
    points = NumericProperty(0)
    is_admin = False

    def build(self):
        setup_font()
        Window.clearcolor = COLOR_BG
        self.title = 'Mostafa - شحن فودافون'
        self.main_layout = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
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
        
        return self.main_layout

    # ==================== LOGIN ====================
    def show_login(self):
        self.main_layout.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        logo_box = BoxLayout(size_hint_y=0.3, padding=20)
        logo = Label(
            text='[b][color=E63946]MOSTAFA[/color][/b]',
            markup=True, font_size='42sp', font_name=FONT_NAME
        )
        logo_box.add_widget(logo)
        layout.add_widget(logo_box)
        
        layout.add_widget(Label(
            text='شحن كروت فودافون',
            font_size='18sp', color=COLOR_TEXT_GRAY,
            font_name=FONT_NAME, size_hint_y=None, height=30
        ))
        layout.add_widget(Widget(size_hint_y=0.1))
        
        self.phone_input = TextInput(
            hint_text='رقم الهاتف (01XXXXXXXXX)',
            multiline=False, input_filter='int',
            size_hint_y=None, height=55,
            background_color=COLOR_CARD,
            foreground_color=COLOR_TEXT,
            hint_text_color=COLOR_TEXT_GRAY,
            padding=(15, 15), font_size='16sp', font_name=FONT_NAME
        )
        layout.add_widget(self.phone_input)
        layout.add_widget(Widget(size_hint_y=0.05))
        
        login_btn = Button(
            text='دخول', size_hint_y=None, height=55,
            background_color=COLOR_RED, color=COLOR_TEXT,
            font_size='18sp', bold=True, font_name=FONT_NAME
        )
        login_btn.bind(on_press=self.do_login)
        layout.add_widget(login_btn)
        
        auto_btn = Button(
            text='الكشف التلقائي عن الرقم',
            size_hint_y=None, height=45,
            background_color=(0.2, 0.5, 0.9, 1),
            color=COLOR_TEXT, font_size='13sp', font_name=FONT_NAME
        )
        auto_btn.bind(on_press=self.try_auto_login)
        layout.add_widget(auto_btn)
        layout.add_widget(Widget(size_hint_y=0.3))
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
            self.show_popup('تنبيه', 'لم يتم العثور على رقم الشريحة')

    def do_login(self, instance):
        phone = self.phone_input.text
        if len(phone) != 11 or not phone.startswith('01'):
            self.show_popup('خطأ', 'رقم الهاتف غير صحيح')
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
        scroll = ScrollView()
        main_content = BoxLayout(orientation='vertical', padding=15, spacing=15, size_hint_y=None)
        main_content.bind(minimum_height=main_content.setter('height'))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=50, padding=(10, 5))
        with top_bar.canvas.before:
            Color(*COLOR_RED)
            self.top_rect = RoundedRectangle(pos=top_bar.pos, size=(Window.width, 50), radius=[0])
            top_bar.bind(pos=self.update_top_bar)
        
        menu_btn = Button(text='☰', font_size='20sp', color=COLOR_TEXT,
                         background_color=(0,0,0,0), size_hint_x=0.15)
        title = Label(text='[b]Mostafa[/b]', markup=True, font_size='22sp',
                     color=COLOR_TEXT, font_name=FONT_NAME)
        refresh_btn = Button(text='↻', font_size='20sp', color=COLOR_TEXT,
                            background_color=(0,0,0,0), size_hint_x=0.15)
        refresh_btn.bind(on_press=lambda x: self.show_home())
        
        top_bar.add_widget(menu_btn)
        top_bar.add_widget(title)
        top_bar.add_widget(refresh_btn)
        main_content.add_widget(top_bar)
        
        # Points card
        points_card = Card(orientation='vertical', size_hint_y=None, height=220, spacing=8)
        points_card.add_widget(Label(
            text='مرحباً', font_size='18sp',
            color=COLOR_GREEN, font_name=FONT_NAME,
            size_hint_y=None, height=30
        ))
        points_card.add_widget(Label(
            text='انتظر حتى يتم تحميل رقمك...',
            font_size='14sp', color=COLOR_TEXT_GRAY,
            font_name=FONT_NAME, size_hint_y=None, height=25
        ))
        points_card.add_widget(Label(
            text=str(self.points), font_size='56sp',
            color=COLOR_RED, font_name=FONT_NAME,
            size_hint_y=None, height=70, bold=True
        ))
        points_card.add_widget(Label(
            text='نقاطك', font_size='14sp',
            color=COLOR_TEXT_GRAY, font_name=FONT_NAME,
            size_hint_y=None, height=25
        ))
        
        btn_row = BoxLayout(size_hint_y=None, height=45, spacing=8)
        history_btn = Button(text='سجل العمليات', background_color=COLOR_RED,
                            color=COLOR_TEXT, font_size='12sp', font_name=FONT_NAME)
        recharge_points_btn = Button(text='شحن نقاط', background_color=COLOR_RED,
                                    color=COLOR_TEXT, font_size='12sp', font_name=FONT_NAME)
        contact_btn = Button(text='تواصل معنا', background_color=COLOR_RED,
                            color=COLOR_TEXT, font_size='12sp', font_name=FONT_NAME)
        
        recharge_points_btn.bind(on_press=self.show_recharge_dialog)
        contact_btn.bind(on_press=lambda x: self.show_popup('تواصل', f'WhatsApp: {ADMIN_PHONE}'))
        
        btn_row.add_widget(history_btn)
        btn_row.add_widget(recharge_points_btn)
        btn_row.add_widget(contact_btn)
        points_card.add_widget(btn_row)
        main_content.add_widget(points_card)
        
        # Big recharge button
        big_recharge = Button(
            text='[b]شحن الرصيد[/b]\nشحن رصيد فودافون',
            markup=True, size_hint_y=None, height=80,
            background_color=COLOR_CARD, color=COLOR_TEXT,
            font_size='16sp', font_name=FONT_NAME
        )
        big_recharge.bind(on_press=self.show_recharge_balance_dialog)
        main_content.add_widget(big_recharge)
        
        # Title
        main_content.add_widget(Label(
            text='اختر الكارت', font_size='20sp',
            color=COLOR_TEXT, font_name=FONT_NAME,
            size_hint_y=None, height=40, bold=True
        ))
        
        # Products grid (3 columns)
        products_grid = GridLayout(cols=3, spacing=10, padding=5, size_hint_y=None)
        products_grid.bind(minimum_height=products_grid.setter('height'))
        
        for product in ALL_PRODUCTS:
            card = self.create_product_card(product)
            products_grid.add_widget(card)
        
        main_content.add_widget(products_grid)
        scroll.add_widget(main_content)
        self.main_layout.add_widget(scroll)

    def create_product_card(self, product):
        card = Card(orientation='vertical', size_hint_y=None, height=130)
        card.add_widget(Label(
            text=f'[b]{product["name"]}[/b]',
            markup=True, font_size='16sp',
            color=COLOR_TEXT, font_name=FONT_NAME,
            size_hint_y=0.4
        ))
        desc_text = product.get('desc', '') or f"{product.get('units', 0)} وحدة/صباحاً"
        card.add_widget(Label(
            text=desc_text, font_size='11sp',
            color=COLOR_TEXT_GRAY, font_name=FONT_NAME,
            size_hint_y=0.35
        ))
        card.add_widget(Label(
            text=product['validity'], font_size='10sp',
            color=COLOR_TEXT_GRAY, font_name=FONT_NAME,
            size_hint_y=0.25
        ))
        card.bind(on_touch_down=lambda touch, p=product: self.on_card_click(touch, p))
        return card

    def on_card_click(self, touch, product):
        if touch.button == 'left':
            self.show_charge_dialog(product)

    def update_top_bar(self, instance, value):
        if hasattr(self, 'top_rect'):
            self.top_rect.pos = (0, instance.y)
            self.top_rect.size = (Window.width, 50)

    def show_recharge_balance_dialog(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        content.add_widget(Label(
            text='شحن رصيد فودافون',
            font_size='18sp', color=COLOR_TEXT,
            font_name=FONT_NAME, bold=True
        ))
        
        amount_input = TextInput(
            hint_text='المبلغ بالجنيه', multiline=False, input_filter='float',
            size_hint_y=None, height=50, background_color=COLOR_CARD,
            foreground_color=COLOR_TEXT, hint_text_color=COLOR_TEXT_GRAY,
            font_size='16sp', font_name=FONT_NAME
        )
        content.add_widget(amount_input)
        
        phone_input = TextInput(
            hint_text='رقم الهاتف للشحن', multiline=False, input_filter='int',
            size_hint_y=None, height=50, background_color=COLOR_CARD,
            foreground_color=COLOR_TEXT, hint_text_color=COLOR_TEXT_GRAY,
            font_size='16sp', font_name=FONT_NAME
        )
        content.add_widget(phone_input)
        
        pin_input = TextInput(
            hint_text='الرقم السري للمحفظة', multiline=False, password=True,
            size_hint_y=None, height=50, background_color=COLOR_CARD,
            foreground_color=COLOR_TEXT, hint_text_color=COLOR_TEXT_GRAY,
            font_size='16sp', font_name=FONT_NAME
        )
        content.add_widget(pin_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=10)
        cancel = Button(text='إلغاء', background_color=(0.4,0.4,0.4,1),
                       color=COLOR_TEXT, font_size='14sp', font_name=FONT_NAME)
        confirm = Button(text='تأكيد', background_color=COLOR_RED,
                        color=COLOR_TEXT, font_size='14sp', font_name=FONT_NAME, bold=True)
        
        popup = Popup(title='شحن الرصيد', content=content,
                     size_hint=(0.9, 0.6), auto_dismiss=False,
                     title_font=FONT_NAME, title_color=COLOR_TEXT)
        
        cancel.bind(on_press=popup.dismiss)
        confirm.bind(on_press=lambda x: self.do_balance_recharge(
            amount_input.text, phone_input.text, pin_input.text, popup
        ))
        
        btn_layout.add_widget(cancel)
        btn_layout.add_widget(confirm)
        content.add_widget(btn_layout)
        popup.open()

    def do_balance_recharge(self, amount, phone, pin, popup):
        if not amount or not phone or not pin:
            self.show_popup('خطأ', 'اكمل جميع البيانات')
            return
        popup.dismiss()
        self.show_popup('معلومة', 'جاري تنفيذ طلب شحن الرصيد...')

    def show_charge_dialog(self, product):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        content.add_widget(Label(
            text=f'[b]{product["name"]}[/b]\nسيتم خصم نقطة واحدة',
            markup=True, font_size='16sp', color=COLOR_TEXT, font_name=FONT_NAME
        ))
        
        target = TextInput(
            hint_text='رقم الهاتف للشحن', multiline=False, input_filter='int',
            size_hint_y=None, height=50, background_color=COLOR_CARD,
            foreground_color=COLOR_TEXT, hint_text_color=COLOR_TEXT_GRAY,
            font_size='16sp', font_name=FONT_NAME
        )
        content.add_widget(target)
        
        pin = TextInput(
            hint_text='الرقم السري للمحفظة (4 أرقام)',
            multiline=False, password=True, input_filter='int',
            size_hint_y=None, height=50, background_color=COLOR_CARD,
            foreground_color=COLOR_TEXT, hint_text_color=COLOR_TEXT_GRAY,
            font_size='16sp', font_name=FONT_NAME
        )
        content.add_widget(pin)
        
        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=10)
        cancel = Button(text='إلغاء', background_color=(0.4,0.4,0.4,1),
                       color=COLOR_TEXT, font_size='14sp', font_name=FONT_NAME)
        confirm = Button(text='تأكيد الشحن', background_color=COLOR_RED,
                        color=COLOR_TEXT, font_size='14sp', font_name=FONT_NAME, bold=True)
        
        popup = Popup(title=f'شحن {product["name"]}', content=content,
                     size_hint=(0.9, 0.55), auto_dismiss=False,
                     title_font=FONT_NAME, title_color=COLOR_TEXT)
        
        cancel.bind(on_press=popup.dismiss)
        confirm.bind(on_press=lambda x: self.process_charge(target.text, pin.text, product, popup))
        
        btn_layout.add_widget(cancel)
        btn_layout.add_widget(confirm)
        content.add_widget(btn_layout)
        popup.open()

    def process_charge(self, target, pin, product, popup):
        if self.points <= 0:
            self.show_popup('خطأ', 'لا توجد نقاط كافية')
            return
        if len(target) != 11 or not target.startswith('01'):
            self.show_popup('خطأ', 'رقم الهاتف غير صحيح')
            return
        if len(pin) != 4:
            self.show_popup('خطأ', 'الرقم السري يجب أن يكون 4 أرقام')
            return
        popup.dismiss()
        self.charge_card(target, pin, product)

    def charge_card(self, msisdn, pin, product):
        loading = Popup(title='جاري الشحن...', auto_dismiss=False,
                       title_font=FONT_NAME, title_color=COLOR_TEXT,
                       content=BoxLayout(padding=20))
        loading.content.add_widget(ProgressBar(max=100, value=50))
        loading.open()
        
        def thread():
            try:
                self.points -= 1
                self.update_points()
                result = self.call_vodafone_api(msisdn, pin, product['id'])
                
                Clock.schedule_once(lambda dt: loading.dismiss(), 0)
                
                if result['success']:
                    Clock.schedule_once(lambda dt: self.show_popup('✅ نجاح', result['message']), 0)
                    self.save_operation(product, msisdn, 'success')
                else:
                    self.points += 1
                    self.update_points()
                    Clock.schedule_once(lambda dt: self.show_popup('❌ فشل', result['message']), 0)
                    self.save_operation(product, msisdn, 'failed')
                
                Clock.schedule_once(lambda dt: self.show_home(), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: loading.dismiss(), 0)
                self.points += 1
                self.update_points()
                Clock.schedule_once(lambda dt: self.show_popup('خطأ', str(e)), 0)
        
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
        content = BoxLayout(orientation='vertical', spacing=8, padding=20)
        content.add_widget(Label(
            text='اختر باقة الشحن:',
            font_size='18sp', color=COLOR_TEXT,
            font_name=FONT_NAME, size_hint_y=None, height=40
        ))
        
        for pkg in POINTS_PACKAGES:
            btn = Button(
                text=pkg['label'],
                size_hint_y=None, height=55,
                background_color=COLOR_GOLD_LIGHT,
                color=COLOR_GOLD, font_size='16sp',
                font_name=FONT_NAME
            )
            btn.bind(on_press=lambda x, p=pkg: self.send_recharge_request(p))
            content.add_widget(btn)
        
        close = Button(text='إلغاء', size_hint_y=None, height=55,
                      background_color=(0.4,0.4,0.4,1),
                      color=COLOR_TEXT, font_size='16sp', font_name=FONT_NAME)
        
        popup = Popup(title='شحن نقاط', content=content,
                     size_hint=(0.9, 0.7), title_font=FONT_NAME, title_color=COLOR_TEXT)
        close.bind(on_press=popup.dismiss)
        content.add_widget(close)
        popup.open()

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
        
        msg = f"🔔 طلب شحن نقاط!\n👤 {self.user_phone}\n⭐ {package['points']} نقطة\n💰 {package['price']} جنيه"
        try:
            import urllib.parse, webbrowser
            webbrowser.open(f'https://wa.me/2{ADMIN_PHONE}?text={urllib.parse.quote(msg)}')
        except:
            pass
        
        self.show_popup('تم', 'تم إرسال طلبك')

    # ==================== ADMIN PANEL ====================
    def show_admin_panel(self):
        self.main_layout.clear_widgets()
        
        header = BoxLayout(size_hint_y=None, height=60, spacing=5)
        header.add_widget(Label(
            text='[b][color=E63946]لوحة التحكم[/color][/b]',
            markup=True, font_size='20sp', font_name=FONT_NAME
        ))
        
        refresh = Button(text='🔄', size_hint_x=0.2,
                        background_color=(0.2, 0.6, 1, 1), font_size='20sp')
        refresh.bind(on_press=lambda x: self.load_admin_requests())
        header.add_widget(refresh)
        
        logout = Button(text='خروج', size_hint_x=0.2,
                       background_color=COLOR_RED, color=COLOR_TEXT,
                       font_size='12sp', font_name=FONT_NAME)
        logout.bind(on_press=lambda x: self.show_login())
        header.add_widget(logout)
        
        self.main_layout.add_widget(header)
        
        stats = BoxLayout(size_hint_y=None, height=40)
        self.pending_label = Label(
            text='جاري التحميل...',
            color=COLOR_GOLD, font_size='16sp', font_name=FONT_NAME
        )
        stats.add_widget(self.pending_label)
        self.main_layout.add_widget(stats)
        
        self.requests_layout = BoxLayout(orientation='vertical')
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
                Clock.schedule_once(lambda dt: self.show_popup('خطأ', 'فشل التحميل'), 0)
        
        threading.Thread(target=fetch, daemon=True).start()

    def display_requests(self, requests_list, users):
        self.requests_layout.clear_widgets()
        self.pending_label.text = f'📋 طلبات قيد الانتظار: {len(requests_list)}'
        
        if not requests_list:
            self.requests_layout.add_widget(Label(
                text='لا توجد طلبات', color=COLOR_TEXT_GRAY,
                font_size='18sp', font_name=FONT_NAME
            ))
            return
        
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', spacing=8, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        for req in requests_list:
            card = Card(orientation='vertical', size_hint_y=None, height=160, padding=10)
            
            info = Label(
                text=f'[b]{req["user_phone"]}[/b]\n⭐ {req["points"]} نقطة | 💰 {req["price"]} جنيه',
                markup=True, font_size='14sp', color=COLOR_TEXT,
                font_name=FONT_NAME, size_hint_y=None, height=80
            )
            card.add_widget(info)
            
            btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
            reject = Button(text='❌ رفض', background_color=(0.8,0,0,1),
                           color=COLOR_TEXT, font_size='13sp', font_name=FONT_NAME)
            approve = Button(text='✅ موافقة', background_color=(0,0.7,0.3,1),
                            color=COLOR_TEXT, font_size='13sp', font_name=FONT_NAME)
            
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
                Clock.schedule_once(lambda dt: self.show_popup('تم', msg), 0)
            except:
                Clock.schedule_once(lambda dt: self.show_popup('خطأ', 'فشل المعالجة'), 0)
        
        threading.Thread(target=process, daemon=True).start()

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        content.add_widget(Label(text=message, font_size='16sp', color=COLOR_TEXT, font_name=FONT_NAME))
        
        btn = Button(text='حسناً', size_hint_y=None, height=50,
                    background_color=COLOR_RED, color=COLOR_TEXT,
                    font_size='16sp', font_name=FONT_NAME)
        
        popup = Popup(title=title, content=content,
                     size_hint=(0.85, 0.35), title_font=FONT_NAME, title_color=COLOR_TEXT)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

if __name__ == '__main__':
    VodafoneApp().run()
