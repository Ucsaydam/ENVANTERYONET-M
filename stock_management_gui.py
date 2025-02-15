import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from stock_management import StockManager, Product
from datetime import datetime, timedelta
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import shutil
import os
from PIL import Image, ImageTk
import json

# Renk şeması
COLORS = {
    'primary': '#845EC2',          # Mor
    'secondary': '#4B4453',        # Koyu gri-mor
    'accent': '#00C9A7',           # Turkuaz
    'background': '#1A1A1A',       # Koyu arka plan
    'card': '#2D2D2D',             # Kart arka planı
    'text': '#FAFFFD',             # Beyaz
    'text_secondary': '#B8B8B8',   # Gri
    'border': '#363636',           # Kenarlık
    'table_header': '#2D2D2D',     # Tablo başlık
    'table_row_even': '#2D2D2D',   # Çift satırlar
    'table_row_odd': '#333333',    # Tek satırlar
    'table_text': '#B8B8B8',       # Tablo metin rengi
    'table_header_text': '#845EC2', # Tablo başlık yazı rengi
    'success': '#2ecc71',          # Yeşil
    'success_hover': '#27ae60',    # Koyu yeşil
    'danger': '#e74c3c',           # Kırmızı
    'danger_hover': '#c0392b',     # Koyu kırmızı
    'warning': '#f1c40f',          # Sarı
    'warning_hover': '#f39c12',    # Koyu sarı
    'info': '#3498db',             # Mavi
    'info_hover': '#2980b9',       # Koyu mavi
    'button_text': '#FFFFFF',      # Buton yazı rengi
}

def initialize_app():
    # Belgeler klasöründe uygulama klasörü oluştur
    app_folder = os.path.join(os.path.expanduser("~"), "Documents", "Stok Yönetim")
    if not os.path.exists(app_folder):
        os.makedirs(app_folder)
    
    # Gerekli dosyaları oluştur
    products_file = os.path.join(app_folder, "products.json")
    if not os.path.exists(products_file):
        with open(products_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
    
    return app_folder

class ModernStockApp(ctk.CTk):
    def __init__(self, user_data=None):  # user_data opsiyonel yapıldı
        super().__init__()
        
        # Font kalitesi için
        try:
            # Windows için font kalitesi
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        # MacOS için font kalitesi
        try:
            self.tk.call('tk', 'scaling', 2.0)
            self.tk.call('ns', 'window', '.', '-scale', '2.0')
        except:
            pass
        
        # Ana pencere ayarları
        self.title("Stok Yönetim Sistemi")
        self.geometry("1400x800")
        self.configure(fg_color=COLORS['background'])
        
        # Kullanıcı bilgileri
        self.user_data = user_data
        if user_data:
            self.title(f"Stok Yönetim Sistemi - {user_data['store']} - {user_data['username']}")
            
            # Eğer admin değilse bazı butonları gizle/devre dışı bırak
            if user_data['role'] != 'admin':
                # Sadece kendi mağazasının verilerini göster
                self.stock_manager = StockManager(store=user_data['store'])
            else:
                # Admin tüm verileri görebilir
                self.stock_manager = StockManager()
        else:
            self.stock_manager = StockManager()
        
        # Uygulama klasörünü başlat
        self.app_folder = initialize_app()
        
        # Görünüm kalitesi ayarları
        self.tk.call('tk', 'scaling', 2.0)  # HiDPI desteği
        
        # Font tanımlamaları
        self.FONTS = {
            'header': ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),     # 18'den 24'e
            'subheader': ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), # 15'ten 20'ye
            'normal': ctk.CTkFont(family="Segoe UI", size=16),                   # 12'den 16'ya
            'small': ctk.CTkFont(family="Segoe UI", size=14),                    # 11'den 14'e
            'large': ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),     # 22'den 28'e
            'button': ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),    # 12'den 16'ya
            'table': ('Segoe UI', 14),                                           # 12'den 14'e
            'table_header': ('Segoe UI', 14, 'bold')                             # 12'den 14'e
        }
        
        # Ana grid yapısı
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sol menü
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=250,
            fg_color=COLORS['card'],
            corner_radius=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)  # Sabit genişlik
        
        # Menü butonlarını oluştur
        self.create_sidebar_buttons()
        
        # Ana içerik alanı
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Tablo stilini ayarla
        self.configure_treeview_style()
        
        # Başlangıç sayfasını göster
        self.show_dashboard()
        
        # Beden seçenekleri
        self.size_options = {
            "Pantolon": ["26", "28", "30", "32", "34", "36", "38", "40", "42", "44"],
            "Tişört": ["XS", "S", "M", "L", "XL", "2XL"],
            "Gömlek": ["XS", "S", "M", "L", "XL", "2XL", 
                      "36", "38", "40", "42", "44"],
            "Elbise": ["XS", "S", "M", "L", "XL", "2XL",
                      "36", "38", "40", "42", "44"],
            "Ceket": ["XS", "S", "M", "L", "XL", "2XL",
                     "46", "48", "50", "52", "54"],
            "Ayakkabı": ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"],
            "Aksesuar": ["Standart", "S", "M", "L", "XL", "Tek Ebat"],
            "Şort": ["XS", "S", "M", "L", "XL", "2XL"],
            "Eşofman": ["XS", "S", "M", "L", "XL", "2XL"],
            "Sweatshirt": ["XS", "S", "M", "L", "XL", "2XL"],
            "Mont": ["XS", "S", "M", "L", "XL", "2XL"],
            "Hırka": ["XS", "S", "M", "L", "XL", "2XL"],
            "İç Giyim": ["XS", "S", "M", "L", "XL", "2XL"],
            "Çanta": ["Mini", "Küçük", "Orta", "Büyük", "Tek Ebat"],
            "Çorap": ["35-38", "39-42", "43-46", "Standart"]
        }
        
        # Kategoriler
        self.categories = ["Seçiniz..."] + list(self.size_options.keys())
        
        # Seçili bedenleri tutacak liste
        self.selected_sizes = []

    def create_sidebar_buttons(self):
        # Logo alanı için frame
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=15)
        
        # Modern logo container
        logo_container = ctk.CTkFrame(
            logo_frame, 
            fg_color=COLORS['primary'],
            corner_radius=12,
            height=60
        )
        logo_container.pack(fill="x", padx=5)
        logo_container.pack_propagate(False)
        
        # Logo yazısı için frame
        text_frame = ctk.CTkFrame(logo_container, fg_color="transparent")
        text_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Ana başlık
        ctk.CTkLabel(
            text_frame,
            text="STOK YÖNETİM",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS['text']
        ).pack()
        
        # Alt başlık
        ctk.CTkLabel(
            text_frame,
            text="SİSTEMİ",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),  # Boyut ve kalınlık artırıldı
            text_color=COLORS['text']  # Ana başlıkla aynı renk
        ).pack()
        
        # Menü butonları için frame
        menu_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        menu_frame.pack(fill="x", pady=10)
        
        buttons = [
            {
                "text": "Ana Sayfa",
                "icon": "🏠",
                "command": self.show_dashboard
            },
            {
                "text": "Ürün Ekle",
                "icon": "➕",
                "command": self.show_add_product
            },
            {
                "text": "Stok Hareket",
                "icon": "🔄",
                "command": self.show_stock_movement
            },
            {
                "text": "Ürün Listesi",
                "icon": "📋",
                "command": self.show_product_list
            },
            {
                "text": "Raporlar",
                "icon": "📊",
                "command": self.show_reports
            },
            {
                "text": "Ayarlar",
                "icon": "⚙️",
                "command": self.show_settings
            }
        ]
        
        for button in buttons:
            btn = ctk.CTkButton(
                menu_frame,
                text=f"{button['icon']} {button['text']}",
                command=button['command'],
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                height=50,
                anchor="w",
                fg_color="transparent",
                text_color=COLORS['text'],
                hover_color=COLORS['primary'],
                corner_radius=10
            )
            btn.pack(fill="x", padx=10, pady=5)
        
        # Alt bilgi
        footer_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom", pady=20)
        
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v1.0.2",
            font=self.FONTS['small'],
            text_color=COLORS['text_secondary']
        )
        version_label.pack()

    def show_dashboard(self):
        self.clear_content()
        
        # Başlık
        header_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['primary'])
        header_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="📊 Genel Durum",
            font=self.FONTS['header']
        ).pack(pady=10)
        
        # Özet kartları
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # Kar analizi yap
        profit_data = self.stock_manager.calculate_profit()
        
        # Toplam Stok Değeri (Alış Fiyatı Bazında)
        self.create_stat_card(
            stats_frame, 0,
            "💰 Toplam Stok Değeri",
            f"{profit_data['total_value']:,.2f} TL",
            "Alış fiyatları üzerinden",
            COLORS['primary']  # Mor renk
        )
        
        # Toplam Satış Geliri
        self.create_stat_card(
            stats_frame, 1,
            "📈 Toplam Satış Geliri",
            f"{profit_data['total_revenue']:,.2f} TL",
            "Son 30 gün",
            COLORS['accent']  # Turkuaz renk
        )
        
        # Toplam Kar
        self.create_stat_card(
            stats_frame, 2,
            "💎 Toplam Kar",
            f"{profit_data['total_profit']:,.2f} TL",
            f"Kar Marjı: %{profit_data['total_margin']:.1f}",
            COLORS['success']  # Yeşil renk
        )
        
        # Toplam Ürün Sayısı
        total_products = sum(product.stock_quantity for product in self.stock_manager.products.values())
        self.create_stat_card(
            stats_frame, 3,
            "📦 Toplam Ürün",
            str(total_products),
            f"{len(self.stock_manager.products)} farklı ürün",
            COLORS['secondary']  # Koyu gri-mor renk
        )
        
        # Alt bölüm için frame
        content_frame = ctk.CTkFrame(self.content_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Grid yapılandırması - her hücreye eşit ağırlık ver
        content_frame.grid_columnconfigure(0, weight=1, uniform="table")
        content_frame.grid_columnconfigure(1, weight=1, uniform="table")
        content_frame.grid_rowconfigure(0, weight=1, uniform="table")
        content_frame.grid_rowconfigure(1, weight=1, uniform="table")
        
        # Tablolar
        self.create_low_stock_table(content_frame, 0, 0)
        self.create_recent_movements_table(content_frame, 0, 1)
        self.create_inactive_products_table(content_frame, 1, 0)
        self.create_popular_products_table(content_frame, 1, 1)

    def create_low_stock_table(self, parent, row, column):
        frame = self.create_table_frame(parent, "Kritik Stok Seviyeleri", "⚠️", row, column)
        
        columns = ('Ürün', 'Stok', 'Minimum')
        tree = self.create_table(frame, columns)
        
        low_stock = self.stock_manager.list_low_stock_products()
        for product in low_stock:
            self.insert_with_tags(tree, (
                product.name,
                f"📦 {product.stock_quantity}",  # Emoji ekle
                f"⚠️ {5}"  # Minimum stok için emoji
            ))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def create_inactive_products_table(self, parent, row, column):
        frame = self.create_table_frame(parent, "Hareketsiz Ürünler (30+ gün)", "⏰", row, column)
        
        # Tablo
        columns = ('Ürün', 'Son Hareket', 'Stok')
        tree = self.create_table(frame, columns)
        
        # Son 30 gün içinde hareketi olmayan ürünler
        today = datetime.now()
        inactive_products = []
        
        for product in self.stock_manager.products.values():
            last_movement = None
            for movement in reversed(self.stock_manager.stock_movements):
                if movement.product_id == product.id:
                    last_movement = movement
                    break
            
            if last_movement is None or (today - last_movement.date).days > 30:
                inactive_products.append((
                    product,
                    last_movement.date if last_movement else "Hiç hareket yok"
                ))
        
        for product, last_date in inactive_products:
            self.insert_with_tags(tree, (product.name, last_date if isinstance(last_date, str) else last_date.strftime('%Y-%m-%d'), product.stock_quantity))
        
        tree.pack(fill="both", expand=True, padx=5, pady=5)

    def create_popular_products_table(self, parent, row, column):
        frame = self.create_table_frame(parent, "En Çok Satan Ürünler", "🔥", row, column)
        
        # Tablo
        columns = ('Ürün', 'Satış Adedi', 'Stok')
        tree = self.create_table(frame, columns)
        
        # Verileri ekle
        today = datetime.now()
        product_sales = {}
        
        for movement in self.stock_manager.stock_movements:
            if movement.movement_type == "çıkış" and (today - movement.date).days <= 30:
                if movement.product_id not in product_sales:
                    product_sales[movement.product_id] = 0
                product_sales[movement.product_id] += movement.quantity
        
        popular_products = sorted(
            product_sales.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for product_id, sales in popular_products:
            product = self.stock_manager.products.get(product_id)
            if product:
                self.insert_with_tags(tree, (product.name, sales, product.stock_quantity))
        
        tree.pack(fill="both", expand=True, padx=5, pady=5)

    def create_stat_card(self, parent, column, title, value, subtitle, color):
        """İstatistik kartı oluşturur"""
        card = ctk.CTkFrame(parent, fg_color=color)
        card.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
        
        # Başlık
        ctk.CTkLabel(
            card,
            text=title,
            font=self.FONTS['normal'],
            text_color="#FFFFFF"  # Her zaman beyaz
        ).pack(pady=(10, 0))
        
        # Değer
        ctk.CTkLabel(
            card,
            text=value,
            font=self.FONTS['large'],
            text_color="#FFFFFF"  # Her zaman beyaz
        ).pack(pady=(5, 0))
        
        # Alt başlık
        ctk.CTkLabel(
            card,
            text=subtitle,
            font=self.FONTS['small'],
            text_color="#FFFFFF"  # Her zaman beyaz
        ).pack(pady=(0, 10))

    def create_recent_movements_table(self, parent, row, column):
        # Tablo frame'i oluştur
        frame = self.create_table_frame(parent, "Son Hareketler", "🔄", row, column)
        
        # Tablo
        columns = ('Tarih', 'Ürün', 'İşlem', 'Miktar')
        tree = self.create_table(frame, columns)
        
        # Son 10 hareketi al ve sırala
        movements = sorted(
            self.stock_manager.stock_movements,
            key=lambda x: x.date,
            reverse=True
        )[:10]
        
        # Hareketleri tabloya ekle
        for movement in movements:
            product = self.stock_manager.products.get(movement.product_id)
            if product:
                # İşlem tipini ve satış yerini belirle
                if movement.movement_type == "giriş":
                    operation = "📥 Giriş"
                else:
                    # Açıklamadan satış yerini çıkar
                    if "Satış Yeri:" in movement.description:
                        sale_place = movement.description.split("|")[0].replace("Satış Yeri:", "").strip()
                        operation = f"📤 Çıkış ({sale_place})"
                    else:
                        operation = "📤 Çıkış"
                
                # Tabloyu doldur
                self.insert_with_tags(tree, (
                    movement.date.strftime("%d.%m.%Y %H:%M"),
                    product.name,
                    operation,
                    movement.quantity
                ))
        
        tree.pack(fill="both", expand=True, padx=5, pady=5)

    def show_add_product(self):
        self.clear_content()
        
        # Başlık
        header_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['primary'])
        header_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="➕ Yeni Ürün Ekle",
            font=self.FONTS['header']
        ).pack(pady=10)
        
        # Scroll container
        scroll_container = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS['card']
        )
        scroll_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # İç frame
        inner_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        inner_frame.pack(padx=40, pady=20, fill="both", expand=True)
        
        # Form alanları
        self.product_entries = {}
        
        # Entry'ler için ortak stil
        entry_style = {
            'height': 50,
            'width': 400,
            'font': self.FONTS['normal'],
            'border_color': COLORS['primary'],
            'border_width': 2,
            'corner_radius': 10,
            'fg_color': COLORS['background']
        }
        
        # Ürün ID
        self.product_entries['id'] = ctk.CTkEntry(
            inner_frame,
            placeholder_text="Ürün ID giriniz",
            **entry_style
        )
        self.product_entries['id'].pack(fill="x", pady=(0,20))
        
        # Ürün Adı
        self.product_entries['name'] = ctk.CTkEntry(
            inner_frame,
            placeholder_text="Ürün adı giriniz",
            **entry_style
        )
        self.product_entries['name'].pack(fill="x", pady=(0,20))
        
        # Kategori
        ctk.CTkLabel(
            inner_frame,
            text="📁 Kategori",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0,5))
        
        self.product_entries['category'] = ctk.CTkComboBox(
            inner_frame,
            values=self.categories,
            font=self.FONTS['normal'],
            height=50,
            width=400,
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
            border_color=COLORS['primary'],
            dropdown_fg_color=COLORS['card'],
            dropdown_hover_color=COLORS['primary'],
            dropdown_text_color=COLORS['text'],
            dropdown_font=self.FONTS['normal'],
            corner_radius=10,
            state="readonly"
        )
        self.product_entries['category'].pack(fill="x", pady=(0,20))
        
        # Beden seçimi
        ctk.CTkLabel(
            inner_frame,
            text="📏 Beden",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0,5))
        
        # Çoklu seçim için özel ComboBox sınıfı
        class MultiSelectComboBox(ctk.CTkComboBox):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.selected_items = set()
            
            def get_selected(self):
                return list(self.selected_items)
            
            def add_item(self, item):
                self.selected_items.add(item)
                self.set(", ".join(sorted(self.selected_items)))
            
            def remove_item(self, item):
                self.selected_items.discard(item)
                self.set(", ".join(sorted(self.selected_items)) or "Beden Seçiniz")
        
        # size_multiselect'i self'e ekle
        self.size_multiselect = MultiSelectComboBox(
            inner_frame,
            values=["Standart"],
            font=self.FONTS['normal'],
            height=50,
            width=400,
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
            border_color=COLORS['primary'],
            dropdown_fg_color=COLORS['card'],
            dropdown_hover_color=COLORS['primary'],
            dropdown_text_color=COLORS['text'],
            dropdown_font=self.FONTS['normal'],
            corner_radius=10,
            state="readonly"
        )
        self.size_multiselect.pack(fill="x", pady=(0,20))
        self.size_multiselect.set("Beden Seçiniz")
        
        # Kategori değiştiğinde bedenleri güncelle
        def update_sizes(choice):
            if choice in self.size_options:
                sizes = self.size_options[choice]
                self.size_multiselect.configure(values=sizes)
                self.size_multiselect.set("Beden Seçiniz")
            else:
                self.size_multiselect.configure(values=["Standart"])
                self.size_multiselect.set("Standart")
        
        # Kategori seçimini izle
        self.product_entries['category'].configure(command=update_sizes)
        
        # Beden seçim penceresi
        def show_size_selector(value=None):  # value parametresi eklendi
            selector_window = ctk.CTkToplevel(self)
            selector_window.title("Beden Seçimi")
            selector_window.geometry("300x400")
            selector_window.configure(fg_color=COLORS['background'])
            
            # Mevcut bedenleri göster
            sizes = self.size_options.get(self.product_entries['category'].get(), ["Standart"])
            
            # Checkbox'lar için frame
            checkbox_frame = ctk.CTkFrame(selector_window, fg_color=COLORS['card'])
            checkbox_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Checkbox değişkenlerini tut
            var_dict = {}
            
            for size in sizes:
                var = tk.BooleanVar(value=size in self.size_multiselect.selected_items)
                var_dict[size] = var
                
                ctk.CTkCheckBox(
                    checkbox_frame,
                    text=size,
                    variable=var,
                    font=self.FONTS['normal'],
                    text_color=COLORS['text'],
                    fg_color=COLORS['primary'],
                    hover_color=COLORS['secondary'],
                    command=lambda s=size, v=var: toggle_size(s, v)
                ).pack(pady=5, padx=20, anchor="w")
        
        def toggle_size(size, var):
            if var.get():
                self.size_multiselect.add_item(size)
            else:
                self.size_multiselect.remove_item(size)
        
        # Beden seçim butonunu ComboBox'a bağla
        self.size_multiselect.configure(command=show_size_selector)
        
        # Cinsiyet
        ctk.CTkLabel(
            inner_frame,
            text="👤 Cinsiyet",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0,5))
        
        self.product_entries['gender'] = ctk.CTkComboBox(
            inner_frame,
            values=["Seçiniz...", "Erkek", "Kadın", "Unisex"],
            font=self.FONTS['normal'],
            height=50,
            width=400,
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
            border_color=COLORS['primary'],
            dropdown_fg_color=COLORS['card'],
            dropdown_hover_color=COLORS['primary'],
            dropdown_text_color=COLORS['text'],
            dropdown_font=self.FONTS['normal'],
            corner_radius=10,
            state="readonly"
        )
        self.product_entries['gender'].pack(fill="x", pady=(0,20))
        
        # Renk
        ctk.CTkLabel(
            inner_frame,
            text="🎨 Renk",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0,5))
        
        self.product_entries['color'] = ctk.CTkComboBox(
            inner_frame,
            values=["Seçiniz...", "Siyah", "Beyaz", "Kırmızı", "Mavi", "Yeşil", "Sarı", "Pembe", "Mor", "Turuncu", "Gri", "Kahverengi"],
            font=self.FONTS['normal'],
            height=50,
            width=400,
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
            border_color=COLORS['primary'],
            dropdown_fg_color=COLORS['card'],
            dropdown_hover_color=COLORS['primary'],
            dropdown_text_color=COLORS['text'],
            dropdown_font=self.FONTS['normal'],
            corner_radius=10,
            state="readonly"
        )
        self.product_entries['color'].pack(fill="x", pady=(0,20))
        
        # Fiyat bilgileri frame
        price_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        price_frame.pack(fill="x", pady=(0,20))
        
        # Alış Fiyatı
        price_left = ctk.CTkFrame(price_frame, fg_color="transparent")
        price_left.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        ctk.CTkLabel(
            price_left,
            text="💰 Alış Fiyatı",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0,5))
        
        self.product_entries['purchase_price'] = ctk.CTkEntry(
            price_left,
            placeholder_text="Alış fiyatı giriniz",
            font=self.FONTS['normal'],
            height=50
        )
        self.product_entries['purchase_price'].pack(fill="x")
        
        # Satış Fiyatı
        price_right = ctk.CTkFrame(price_frame, fg_color="transparent")
        price_right.pack(side="left", fill="x", expand=True, padx=(10,0))
        
        ctk.CTkLabel(
            price_right,
            text="💵 Satış Fiyatı",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0,5))
        
        self.product_entries['price'] = ctk.CTkEntry(
            price_right,
            placeholder_text="Satış fiyatı giriniz",
            font=self.FONTS['normal'],
            height=50
        )
        self.product_entries['price'].pack(fill="x")
        
        # Fotoğraf yükleme bölümü
        photo_frame = ctk.CTkFrame(inner_frame, fg_color=COLORS['card'])
        photo_frame.pack(fill="x", pady=(0,20))
        
        photo_label = ctk.CTkLabel(
            photo_frame,
            text="📸 Ürün Fotoğrafı",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        )
        photo_label.pack(anchor="w", pady=(10,5), padx=20)
        
        # Fotoğraf önizleme alanı
        self.photo_preview = ctk.CTkLabel(
            photo_frame,
            text="Fotoğraf seçilmedi",
            font=self.FONTS['small'],
            text_color=COLORS['text_secondary']
        )
        self.photo_preview.pack(pady=5)
        
        # Fotoğraf butonları için frame
        photo_buttons = ctk.CTkFrame(photo_frame, fg_color="transparent")
        photo_buttons.pack(fill="x", padx=20, pady=(5,10))
        
        def select_photo():
            file_path = filedialog.askopenfilename(
                title="Fotoğraf Seç",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_path:
                # Fotoğrafı kaydet ve önizleme göster
                try:
                    # Fotoğrafı kopyala
                    photo_dir = os.path.join(self.app_folder, "photos")
                    if not os.path.exists(photo_dir):
                        os.makedirs(photo_dir)
                    
                    # Yeni dosya adı oluştur
                    file_ext = os.path.splitext(file_path)[1]
                    new_filename = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
                    new_path = os.path.join(photo_dir, new_filename)
                    
                    # Fotoğrafı kopyala
                    shutil.copy2(file_path, new_path)
                    
                    # Önizleme göster
                    img = Image.open(new_path)
                    img.thumbnail((100, 100))  # Önizleme boyutu
                    photo = ImageTk.PhotoImage(img)
                    
                    self.photo_preview.configure(image=photo, text="")
                    self.photo_preview.image = photo  # Referansı sakla
                    
                    # Fotoğraf yolunu kaydet
                    self.product_entries['image'] = new_path
                    
                except Exception as e:
                    messagebox.showerror("Hata", f"Fotoğraf yüklenirken hata oluştu: {e}")
        
        def remove_photo():
            self.photo_preview.configure(image=None, text="Fotoğraf seçilmedi")
            if hasattr(self.photo_preview, 'image'):
                del self.photo_preview.image
            self.product_entries['image'] = ""
        
        ctk.CTkButton(
            photo_buttons,
            text="Fotoğraf Seç",
            command=select_photo,
            font=self.FONTS['normal'],
            height=40,
            fg_color=COLORS['info'],
            hover_color=COLORS['info_hover']
        ).pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(
            photo_buttons,
            text="Fotoğrafı Kaldır",
            command=remove_photo,
            font=self.FONTS['normal'],
            height=40,
            fg_color=COLORS['danger'],
            hover_color=COLORS['danger_hover']
        ).pack(side="left", expand=True, padx=5)
        
        # Kaydet butonu için ayrı frame
        button_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['card'])
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Kaydet butonu
        ctk.CTkButton(
            button_frame,
            text="💾 Kaydet",
            command=self.save_product,
            font=self.FONTS['button'],
            height=50,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover']
        ).pack(fill="x", padx=40, pady=10)

    def save_product(self):
        try:
            # Form verilerini al
            product_data = {
                'id': self.product_entries['id'].get().strip(),
                'name': self.product_entries['name'].get().strip(),
                'category': self.product_entries['category'].get(),
                'gender': self.product_entries['gender'].get(),
                'size': self.size_multiselect.get_selected(),  # self. eklendi
                'color': self.product_entries['color'].get(),
                'purchase_price': self.product_entries['purchase_price'].get().strip(),
                'price': self.product_entries['price'].get().strip(),
                'image_path': self.product_entries.get('image', '')
            }
            
            # Boş alan kontrolü
            required_fields = {
                'id': 'Ürün ID',
                'name': 'Ürün Adı',
                'category': 'Kategori',
                'gender': 'Cinsiyet',
                'size': 'Beden',
                'color': 'Renk',
                'purchase_price': 'Alış Fiyatı',
                'price': 'Satış Fiyatı'
            }
            
            empty_fields = []
            for key, label in required_fields.items():
                value = product_data[key]
                if not value or value == "Seçiniz...":
                    empty_fields.append(label)
            
            if empty_fields:
                messagebox.showerror("Hata", f"Lütfen aşağıdaki alanları doldurunuz:\n\n" + "\n".join(empty_fields))
                return
            
            # Fiyat kontrolü
            try:
                purchase_price = float(product_data['purchase_price'])
                price = float(product_data['price'])
                if purchase_price <= 0 or price <= 0:
                    messagebox.showerror("Hata", "Fiyatlar 0'dan büyük olmalıdır!")
                    return
                product_data['purchase_price'] = purchase_price
                product_data['price'] = price
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli fiyat değerleri giriniz!")
                return
            
            # Ürünü oluştur ve kaydet
            new_product = Product(**product_data)
            if self.stock_manager.add_product(new_product):
                messagebox.showinfo("Başarılı", "Ürün başarıyla eklendi!")
                self.show_dashboard()
            
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def show_stock_movement(self):
        self.clear_content()
        
        # Başlık
        header_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['primary'])
        header_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="🔄 Stok Hareket İşlemi",
            font=self.FONTS['header']
        ).pack(pady=10)
        
        # Ana form frame
        form_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['card'])
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # İç frame
        inner_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        inner_frame.pack(padx=40, pady=20, fill="both", expand=True)
        
        # Ürün seçimi
        ctk.CTkLabel(
            inner_frame,
            text="📦 Ürün Seçimi",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0,5))
        
        product_combobox = ctk.CTkComboBox(
            inner_frame,
            values=[f"{p.id} - {p.name}" for p in self.stock_manager.products.values()],
            font=self.FONTS['normal'],
            height=50,  # Yüksekliği artırdık
            width=400,
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
            border_color=COLORS['primary'],  # Kenarlık rengini değiştirdik
            dropdown_fg_color=COLORS['card'],
            dropdown_hover_color=COLORS['primary'],
            dropdown_text_color=COLORS['text'],
            dropdown_font=self.FONTS['normal'],  # Dropdown yazı boyutunu artırdık
            corner_radius=10,  # Köşe yuvarlaklığını artırdık
            state="readonly"  # Sadece seçim yapılabilir
        )
        product_combobox.pack(fill="x", pady=(0,20))
        product_combobox.set("Ürün Seçiniz...")
        
        # Satış yeri seçimi
        ctk.CTkLabel(
            inner_frame,
            text="🏪 Satış Yeri",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0,5))
        
        sales_place = ctk.CTkComboBox(
            inner_frame,
            values=["Mağaza", "Instagram", "Trendyol", "Hepsiburada", "Diğer"],
            font=self.FONTS['normal'],
            height=50,  # Yüksekliği artırdık
            width=400,
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
            border_color=COLORS['primary'],  # Kenarlık rengini değiştirdik
            dropdown_fg_color=COLORS['card'],
            dropdown_hover_color=COLORS['primary'],
            dropdown_text_color=COLORS['text'],
            dropdown_font=self.FONTS['normal'],  # Dropdown yazı boyutunu artırdık
            corner_radius=10,  # Köşe yuvarlaklığını artırdık
            state="readonly"  # Sadece seçim yapılabilir
        )
        sales_place.pack(fill="x", pady=(0,20))
        sales_place.set("Satış Yeri Seçiniz...")
        
        # Miktar
        ctk.CTkLabel(
            inner_frame,
            text="🔢 Miktar",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0,5))
        
        quantity_entry = ctk.CTkEntry(
            inner_frame,
            placeholder_text="Miktar giriniz",
            font=self.FONTS['normal'],
            height=40,
            width=400
        )
        quantity_entry.pack(fill="x", pady=(0,20))
        
        # Butonlar için frame
        buttons_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20,0))
        
        def add_movement(movement_type):
            try:
                product_id = product_combobox.get().split(" - ")[0]
                qty = int(quantity_entry.get())
                
                # Çıkış hareketi için satış yeri bilgisini ekle
                desc = f"Satış Yeri: {sales_place.get()}" if movement_type == "çıkış" else ""
                
                self.stock_manager.add_stock_movement(
                    product_id=product_id,
                    movement_type=movement_type,
                    quantity=qty,
                    description=desc
                )
                
                messagebox.showinfo("Başarılı", "Stok hareketi kaydedildi!")
                self.show_dashboard()
                
            except ValueError as e:
                messagebox.showerror("Hata", str(e))
            except Exception as e:
                messagebox.showerror("Hata", f"Bir hata oluştu: {e}")
        
        # İşlem butonları
        ctk.CTkButton(
            buttons_frame,
            text="📥 Giriş",
            command=lambda: add_movement("giriş"),
            font=self.FONTS['button'],
            height=45,
            width=180,
            fg_color=COLORS['info'],
            hover_color=COLORS['info_hover']
        ).pack(side="left", padx=5, expand=True)
        
        ctk.CTkButton(
            buttons_frame,
            text="💰 Satış",
            command=lambda: add_movement("çıkış"),
            font=self.FONTS['button'],
            height=45,
            width=180,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover']
        ).pack(side="left", padx=5, expand=True)
        
        ctk.CTkButton(
            buttons_frame,
            text="📤 Çıkış",
            command=lambda: add_movement("çıkış"),
            font=self.FONTS['button'],
            height=45,
            width=180,
            fg_color=COLORS['danger'],
            hover_color=COLORS['danger_hover']
        ).pack(side="left", padx=5, expand=True)

    def show_product_list(self):
        self.clear_content()
        
        # Ana container
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Başlık
        header_frame = ctk.CTkFrame(container, fg_color=COLORS['primary'], corner_radius=10)
        header_frame.pack(fill="x", padx=2, pady=2)
        
        ctk.CTkLabel(
            header_frame,
            text="📋 Ürün Listesi",
            font=self.FONTS['header'],
            text_color=COLORS['text']
        ).pack(pady=15)
        
        # Filtre Frame
        filter_frame = ctk.CTkFrame(container, fg_color=COLORS['card'], corner_radius=10)
        filter_frame.pack(fill="x", pady=10)
        
        # Grid yapılandırması
        filter_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1)
        
        # Kategori filtresi
        ctk.CTkLabel(
            filter_frame,
            text="📁 Kategori:",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=0, padx=10, pady=10)
        
        category_cb = ctk.CTkComboBox(
            filter_frame,
            values=self.categories,
            height=35,
            width=150
        )
        category_cb.grid(row=0, column=1, padx=10, pady=10)
        category_cb.set("Tümü")
        
        # Cinsiyet filtresi
        ctk.CTkLabel(
            filter_frame,
            text="👤 Cinsiyet:",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=2, padx=10, pady=10)
        
        gender_cb = ctk.CTkComboBox(
            filter_frame,
            values=["Tümü", "Erkek", "Kadın", "Unisex"],
            height=35,
            width=150
        )
        gender_cb.grid(row=0, column=3, padx=10, pady=10)
        gender_cb.set("Tümü")
        
        # Tablo Frame
        table_frame = ctk.CTkFrame(container, fg_color=COLORS['card'], corner_radius=10)
        table_frame.pack(fill="both", expand=True, pady=10)
        
        # Tablo
        columns = ('ID', 'Ürün', 'Kategori', 'Cinsiyet', 'Beden', 'Renk', 'Alış Fiyatı', 'Satış Fiyatı', 'Stok', 'İşlem')
        tree = self.create_table(table_frame, columns)
        
        def show_product_details(product_id):
            # ID'yi string'e çevir
            product_id = str(product_id)
            
            # Ürünü al
            product = self.stock_manager.products.get(product_id)
            if not product:
                print(f"Ürün bulunamadı: {product_id}")
                return
            
            print(f"Ürün detayları açılıyor: {product.name} (ID: {product_id})")
            
            # Detay penceresi
            detail_window = ctk.CTkToplevel(self)
            detail_window.title(f"Ürün Detayları - {product.name}")
            detail_window.geometry("1000x700")
            detail_window.grab_set()
            
            # Tab view
            tabs = ctk.CTkTabview(
                detail_window,
                fg_color=COLORS['card'],
                segmented_button_fg_color=COLORS['primary'],
                segmented_button_selected_color=COLORS['secondary']
            )
            tabs.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Ürün Bilgileri tab'ı
            info_tab = tabs.add("📋 Ürün Bilgileri")
            
            # Ana frame
            main_frame = ctk.CTkFrame(info_tab, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Sol panel - Fotoğraf ve özet istatistikler
            left_frame = ctk.CTkFrame(main_frame, width=300)
            left_frame.pack(side="left", fill="y", padx=10)
            
            # Fotoğraf alanı
            photo_frame = ctk.CTkFrame(left_frame, width=250, height=250)
            photo_frame.pack(pady=20)
            photo_frame.pack_propagate(False)
            
            photo_label = ctk.CTkLabel(photo_frame, text="Fotoğraf Yok")
            photo_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Fotoğrafı göster
            if product.image_path and os.path.exists(product.image_path):
                try:
                    print(f"Fotoğraf yükleniyor: {product.image_path}")  # Debug için
                    image = Image.open(product.image_path)
                    image.thumbnail((240, 240))
                    photo = ImageTk.PhotoImage(image)
                    photo_label.configure(image=photo, text="")
                    photo_label.image = photo
                except Exception as e:
                    print(f"Fotoğraf yükleme hatası: {e}")
            
            # Sağ panel - Detaylı bilgiler
            right_frame = ctk.CTkFrame(main_frame)
            right_frame.pack(side="left", fill="both", expand=True, padx=10)
            
            # Ürün bilgileri
            fields = [
                ('Ürün ID:', product.id),
                ('Ürün Adı:', product.name),
                ('Kategori:', product.category),
                ('Cinsiyet:', product.gender),
                ('Bedenler:', product.size),
                ('Renk:', product.color),
                ('Alış Fiyatı:', f"{product.purchase_price:.2f} TL"),
                ('Satış Fiyatı:', f"{product.price:.2f} TL"),
                ('Stok:', str(product.stock_quantity))
            ]
            
            for i, (label, value) in enumerate(fields):
                ctk.CTkLabel(
                    right_frame,
                    text=label,
                    font=self.FONTS['normal'],
                    text_color=COLORS['text_secondary']
                ).grid(row=i, column=0, padx=10, pady=5, sticky="e")
                
                ctk.CTkLabel(
                    right_frame,
                    text=value,
                    font=self.FONTS['normal']
                ).grid(row=i, column=1, padx=10, pady=5, sticky="w")
            
            # Stok Geçmişi tab'ı
            history_tab = tabs.add("🔄 Stok Geçmişi")
            
            # Tablo
            columns = ('Tarih', 'İşlem', 'Miktar', 'Açıklama')
            history_tree = self.create_table(history_tab, columns)
            
            # Stok hareketlerini getir
            movements = self.stock_manager.get_product_movements(product_id)
            for movement in movements:
                self.insert_with_tags(history_tree, (
                    movement.date.strftime("%d.%m.%Y %H:%M"),
                    "📥 Giriş" if movement.movement_type == "giriş" else "📤 Çıkış",
                    movement.quantity,
                    movement.description
                ))
        
        def filter_products(category, gender):
            # Tabloyu temizle
            for item in tree.get_children():
                tree.delete(item)
            
            # Tıklama olayını ekle
            def on_click(event):
                item = tree.selection()
                if item:  # Seçili öğe varsa
                    item = item[0]
                    product_id = tree.item(item)['values'][0]  # ID ilk sütunda
                    print(f"Ürüne tıklandı: {product_id}")  # Debug için
                    show_product_details(product_id)
            
            tree.bind('<Double-1>', on_click)  # Çift tıklama olayı
            
            # Filtreleme
            for product in self.stock_manager.products.values():
                if (category == "Tümü" or product.category == category) and \
                   (gender == "Tümü" or product.gender == gender):
                    
                    # Ürün bilgilerini tabloya ekle
                    item = tree.insert('', 'end', values=(
                        str(product.id),  # ID'yi string olarak ekle
                        product.name,
                        product.category,
                        product.gender,
                        product.size,
                        product.color,
                        f"{product.purchase_price:.2f} TL",
                        f"{product.price:.2f} TL",
                        product.stock_quantity,
                        "👁️ Detay"
                    ))
        
        # Filtrele butonu
        ctk.CTkButton(
            filter_frame,
            text="🔍 Filtrele",
            font=self.FONTS['button'],
            height=35,
            width=120,
            command=lambda: filter_products(category_cb.get(), gender_cb.get())
        ).grid(row=0, column=4, padx=10, pady=10)
        
        # Başlangıçta tüm ürünleri göster
        filter_products("Tümü", "Tümü")
        
        # Tabloyu yerleştir
        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def show_reports(self):
        self.clear_content()
        
        # Başlık
        header_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['primary'], corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=2)
        
        ctk.CTkLabel(
            header_frame,
            text="📊 Raporlar ve Analizler",
            font=self.FONTS['header'],
            text_color=COLORS['text']
        ).pack(pady=15)
        
        # Tab view oluştur
        tabs = ctk.CTkTabview(self.content_frame, fg_color=COLORS['card'])
        tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Stok Durumu tab'ı
        stock_tab = tabs.add("📦 Stok Durumu")
        stock_frame = ctk.CTkFrame(stock_tab, fg_color="transparent")
        stock_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_stock_chart(stock_frame)
        
        # Satış Analizi tab'ı
        sales_tab = tabs.add("💰 Satış Analizi")
        sales_frame = ctk.CTkFrame(sales_tab, fg_color="transparent")
        sales_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_store_analysis_chart(sales_frame)
        
        # Kar Analizi tab'ı
        profit_tab = tabs.add("📈 Kar Analizi")
        profit_frame = ctk.CTkFrame(profit_tab, fg_color="transparent")
        profit_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_profit_chart(profit_frame)
        
        # Alt butonlar
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="📊 Excel'e Aktar",
            command=self.export_to_excel,
            height=40,
            fg_color=COLORS['accent'],
            hover_color=COLORS['secondary']
        ).pack(side="left", padx=5)

    def create_store_analysis_chart(self, parent):
        # Satış yeri bazlı analiz
        sales_data = {
            'Hepsiburada': {'total': 0, 'count': 0},
            'Trendyol': {'total': 0, 'count': 0},
            'Amazon': {'total': 0, 'count': 0},
            'Mağaza': {'total': 0, 'count': 0}
        }
        total_sales = 0
        
        # Son 30 günlük satışları al
        today = datetime.now()
        for movement in self.stock_manager.stock_movements:
            if movement.movement_type == "çıkış" and (today - movement.date).days <= 30:
                # Satış yerini al (description'dan)
                if "Satış Yeri:" in movement.description:
                    place = movement.description.split("Satış Yeri:")[1].split("|")[0].strip()
                    product = self.stock_manager.products.get(movement.product_id)
                    if product:
                        sale_amount = movement.quantity * product.price
                        if place in sales_data:
                            sales_data[place]['total'] += sale_amount
                            sales_data[place]['count'] += movement.quantity
                            total_sales += sale_amount
        
        # Grafik oluştur
        fig = Figure(figsize=(14, 6), facecolor=COLORS['card'])  # Genişliği artırdık
        
        # Pasta grafik için subplot
        ax1 = fig.add_subplot(121)
        ax1.set_position([0.05, 0.1, 0.4, 0.8])  # Sol grafik pozisyonu
        
        # Satış tutarı olmayan yerleri çıkar
        active_places = {k: v for k, v in sales_data.items() if v['total'] > 0}
        
        if active_places:
            places = list(active_places.keys())
            amounts = [v['total'] for v in active_places.values()]
            percentages = [amount/total_sales*100 for amount in amounts]
            
            wedges, texts, autotexts = ax1.pie(
                percentages,
                labels=places,
                autopct='%1.1f%%',
                colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], '#2ecc71'],
                textprops={'color': COLORS['text']}
            )
            ax1.set_title('Satış Yeri Dağılımı (Tutar)', color=COLORS['text'], pad=20)
        
        # Adet bazlı grafik için subplot
        ax2 = fig.add_subplot(122)
        ax2.set_position([0.55, 0.1, 0.4, 0.8])  # Sağ grafik pozisyonu
        
        if active_places:
            counts = [v['count'] for v in active_places.values()]
            total_count = sum(counts)
            count_percentages = [count/total_count*100 for count in counts]
            
            wedges, texts, autotexts = ax2.pie(
                count_percentages,
                labels=places,
                autopct='%1.1f%%',
                colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], '#2ecc71'],
                textprops={'color': COLORS['text']}
            )
            ax2.set_title('Satış Yeri Dağılımı (Adet)', color=COLORS['text'], pad=20)
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tablo için frame
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="x", pady=(30, 10), padx=20)  # Üst boşluğu artırdık
        
        # Tablo başlığı
        ctk.CTkLabel(
            table_frame,
            text="Satış Yeri Detayları",
            font=self.FONTS['subheader'],
            text_color=COLORS['text']
        ).pack(pady=(0, 10))

    def export_to_excel(self):
        # Ürün verilerini DataFrame'e dönüştür
        products_data = []
        for product in self.stock_manager.products.values():
            products_data.append({
                'ID': product.id,
                'Ürün': product.name,
                'Kategori': product.category,
                'Cinsiyet': product.gender,
                'Beden': product.size,
                'Renk': product.color,
                'Fiyat': product.price,
                'Stok': product.stock_quantity
            })
        
        df = pd.DataFrame(products_data)
        
        # Excel dosyasına kaydet
        filename = f"stok_raporu_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(filename, index=False)
        messagebox.showinfo("Başarılı", f"Rapor kaydedildi: {filename}")

    def auto_backup(self):
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # JSON dosyalarını yedekle
        for file in ["products.json", "stock_movements.json"]:
            if os.path.exists(file):
                backup_file = f"{backup_dir}/{timestamp}_{file}"
                shutil.copy2(file, backup_file)

    def clear_content(self):
        # İçerik alanını temizle
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def configure_treeview_style(self):
        style = ttk.Style()
        
        # Anti-aliasing için
        self.option_add('*Font', self.FONTS['normal'])
        
        # Treeview'in tüm beyaz alanlarını kaldır
        style.layout("Custom.Treeview", [
            ('Custom.Treeview.treearea', {'sticky': 'nswe'})
        ])
        
        # Ana tablo stili
        style.configure(
            "Custom.Treeview",
            background=COLORS['card'],
            foreground=COLORS['table_text'],
            fieldbackground=COLORS['card'],
            borderwidth=0,
            font=self.FONTS['table'],
            rowheight=40,
            relief='flat'
        )
        
        # Başlık stili
        style.configure(
            "Custom.Treeview.Heading",
            background=COLORS['table_header'],
            foreground=COLORS['table_header_text'],
            relief="flat",
            font=self.FONTS['table_header'],
            padding=12,
            borderwidth=0
        )
        
        # Başlıklara hover efekti
        style.map(
            "Custom.Treeview.Heading",
            background=[('active', COLORS['secondary'])],
            foreground=[('active', COLORS['text'])]
        )
        
        # Seçili satır stili
        style.map(
            "Custom.Treeview",
            background=[('selected', COLORS['primary'])],
            foreground=[('selected', COLORS['text'])],
            fieldbackground=[('selected', COLORS['card'])]  # Seçili satır arka planı
        )

    def create_table(self, parent, columns, height=5):
        # Tablo oluştur
        tree = ttk.Treeview(
            parent,
            columns=columns,
            show='headings',
            height=height,
            style="Custom.Treeview"
        )
        
        # Sütunları ayarla
        for col in columns:
            tree.heading(col, text=col.upper())
            tree.column(col, width=150, anchor="center")
        
        # Tek/çift satır renkleri için tag'ler
        tree.tag_configure('oddrow', background=COLORS['table_row_odd'], foreground=COLORS['table_text'])
        tree.tag_configure('evenrow', background=COLORS['table_row_even'], foreground=COLORS['table_text'])
        
        # Font boyutunu küçült
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            font=('Segoe UI', 10),  # 12'den 10'a
            rowheight=35  # 40'tan 35'e
        )
        style.configure(
            "Custom.Treeview.Heading",
            font=('Segoe UI', 10, 'bold'),  # 12'den 10'a
            padding=10  # 12'den 10'a
        )
        
        # Scrollbar ekle
        scrollbar = ctk.CTkScrollbar(parent, command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
        return tree

    def create_table_frame(self, parent, title, icon, row, column):
        # Sabit boyutlu frame
        frame = ctk.CTkFrame(parent, fg_color=COLORS['card'], corner_radius=10, height=300)  # Sabit yükseklik
        frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
        frame.grid_propagate(False)  # Boyutu sabitle
        
        # Başlık frame
        header = ctk.CTkFrame(frame, fg_color=COLORS['primary'], corner_radius=10)
        header.pack(fill="x", padx=2, pady=2)
        
        # Başlık
        ctk.CTkLabel(
            header,
            text=f"{icon} {title}",
            font=self.FONTS['subheader'],
            text_color=COLORS['text']
        ).pack(pady=10)
        
        return frame

    def insert_with_tags(self, tree, values):
        """Tek/çift satır renklerini uygula"""
        idx = len(tree.get_children()) + 1
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        tree.insert('', 'end', values=values, tags=(tag,))

    def create_stock_chart(self, parent):
        fig = Figure(figsize=(8, 4), facecolor=COLORS['card'])
        ax = fig.add_subplot(111)
        
        products = list(self.stock_manager.products.values())
        names = [p.name for p in products]
        stocks = [p.stock_quantity for p in products]
        
        bars = ax.bar(names, stocks)
        ax.set_facecolor(COLORS['card'])
        ax.set_title('Ürün Stok Durumu', color=COLORS['text'], pad=20)
        ax.tick_params(axis='x', colors=COLORS['text'], rotation=45)
        ax.tick_params(axis='y', colors=COLORS['text'])
        ax.spines['bottom'].set_color(COLORS['border'])
        ax.spines['top'].set_color(COLORS['border'])
        ax.spines['left'].set_color(COLORS['border'])
        ax.spines['right'].set_color(COLORS['border'])
        
        # Renklendirme ve stil
        for bar in bars:
            bar.set_color(COLORS['primary'])
            bar.set_alpha(0.8)  # Biraz transparanlık
        
        # Izgara çizgileri
        ax.grid(True, color=COLORS['border'], linestyle='--', alpha=0.3)
        
        fig.tight_layout()  # Otomatik düzenleme
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_profit_chart(self, parent):
        # Son 30 günlük kar analizi
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        profit_data = self.stock_manager.calculate_profit(thirty_days_ago, today)
        
        # Grafik oluştur
        fig = Figure(figsize=(14, 6), facecolor=COLORS['card'])
        
        # Kar grafiği
        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(COLORS['card'])
        
        # Satış ve kar verilerini hazırla
        dates = [detail['date'].date() for detail in profit_data['sales_details']]
        revenues = [detail['revenue'] for detail in profit_data['sales_details']]
        profits = [detail['profit'] for detail in profit_data['sales_details']]
        
        # Çizgi grafikleri
        ax1.plot(dates, revenues, label='Satış Geliri', color=COLORS['primary'], marker='o')
        ax1.plot(dates, profits, label='Kar', color=COLORS['accent'], marker='o')
        
        ax1.set_title('Günlük Satış ve Kar Analizi', color=COLORS['text'], pad=20)
        ax1.set_xlabel('Tarih', color=COLORS['text'])
        ax1.set_ylabel('TL', color=COLORS['text'])
        ax1.legend()
        ax1.grid(True, color=COLORS['border'], linestyle='--', alpha=0.3)
        
        # Kar marjı grafiği
        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(COLORS['card'])
        
        margins = [detail['profit_margin'] for detail in profit_data['sales_details']]
        ax2.plot(dates, margins, color=COLORS['secondary'], marker='o')
        
        ax2.set_title('Günlük Kar Marjı (%)', color=COLORS['text'], pad=20)
        ax2.set_xlabel('Tarih', color=COLORS['text'])
        ax2.set_ylabel('Kar Marjı (%)', color=COLORS['text'])
        ax2.grid(True, color=COLORS['border'], linestyle='--', alpha=0.3)
        
        # Eksenleri düzenle
        for ax in [ax1, ax2]:
            ax.tick_params(axis='x', colors=COLORS['text'], rotation=45)
            ax.tick_params(axis='y', colors=COLORS['text'])
            for spine in ax.spines.values():
                spine.set_color(COLORS['border'])
        
        fig.tight_layout()
        
        # Özet bilgiler
        summary_frame = ctk.CTkFrame(parent, fg_color="transparent")
        summary_frame.pack(fill="x", pady=20, padx=20)
        
        # Toplam satış
        sales_frame = ctk.CTkFrame(summary_frame, fg_color=COLORS['primary'])
        sales_frame.pack(side="left", expand=True, padx=5, fill="x")
        
        ctk.CTkLabel(
            sales_frame,
            text="Toplam Satış",
            font=self.FONTS['normal']
        ).pack(pady=(10,0))
        
        ctk.CTkLabel(
            sales_frame,
            text=f"{profit_data['total_revenue']:,.2f} TL",
            font=self.FONTS['large']
        ).pack(pady=(0,10))
        
        # Toplam kar
        profit_frame = ctk.CTkFrame(summary_frame, fg_color=COLORS['accent'])
        profit_frame.pack(side="left", expand=True, padx=5, fill="x")
        
        ctk.CTkLabel(
            profit_frame,
            text="Toplam Kar",
            font=self.FONTS['normal']
        ).pack(pady=(10,0))
        
        ctk.CTkLabel(
            profit_frame,
            text=f"{profit_data['total_profit']:,.2f} TL",
            font=self.FONTS['large']
        ).pack(pady=(0,10))
        
        # Ortalama kar marjı
        margin_frame = ctk.CTkFrame(summary_frame, fg_color=COLORS['secondary'])
        margin_frame.pack(side="left", expand=True, padx=5, fill="x")
        
        ctk.CTkLabel(
            margin_frame,
            text="Ortalama Kar Marjı",
            font=self.FONTS['normal']
        ).pack(pady=(10,0))
        
        ctk.CTkLabel(
            margin_frame,
            text=f"%{profit_data['total_margin']:.1f}",
            font=self.FONTS['large']
        ).pack(pady=(0,10))
        
        # Grafiği yerleştir
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def show_settings(self):
        self.clear_content()
        
        # Başlık
        header_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['primary'])
        header_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="⚙️ Ayarlar",
            font=self.FONTS['header']
        ).pack(pady=10)
        
        # Ana içerik frame
        main_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['card'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # İç frame
        inner_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        inner_frame.pack(padx=40, pady=20, fill="both", expand=True)
        
        # Program Güncellemesi Bölümü
        update_section = self.create_settings_section(
            inner_frame,
            "🔄 Program Güncellemesi",
            "Programın en son sürümünü kullandığınızdan emin olun"
        )
        
        # Versiyon bilgisi
        try:
            with open('version.json', 'r') as f:
                version = json.load(f)['version']
        except:
            version = "1.0.0"
        
        version_frame = ctk.CTkFrame(update_section, fg_color="transparent")
        version_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            version_frame,
            text="Mevcut Sürüm:",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            version_frame,
            text=version,
            font=self.FONTS['normal'],
            text_color=COLORS['text']
        ).pack(side="left", padx=5)
        
        # Güncelleme butonu
        ctk.CTkButton(
            update_section,
            text="Güncellemeleri Kontrol Et",
            command=lambda: self.check_updates(show_message=True),
            font=self.FONTS['normal'],
            height=40,
            fg_color=COLORS['primary'],
            hover_color=COLORS['secondary']
        ).pack(pady=10, fill="x")
        
        # Veri Yedekleme Bölümü
        backup_section = self.create_settings_section(
            inner_frame,
            "💾 Veri Yedekleme",
            "Verilerinizi güvende tutmak için düzenli yedekleme yapın",
            pady=(30, 0)
        )
        
        # Son yedekleme bilgisi
        backup_info_frame = ctk.CTkFrame(backup_section, fg_color="transparent")
        backup_info_frame.pack(fill="x", pady=5)
        
        last_backup = self.get_last_backup_date()
        
        ctk.CTkLabel(
            backup_info_frame,
            text="Son Yedekleme:",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            backup_info_frame,
            text=last_backup,
            font=self.FONTS['normal'],
            text_color=COLORS['text']
        ).pack(side="left", padx=5)
        
        # Yedekleme butonları
        backup_buttons_frame = ctk.CTkFrame(backup_section, fg_color="transparent")
        backup_buttons_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            backup_buttons_frame,
            text="Yedekleme Oluştur",
            command=self.create_backup,
            font=self.FONTS['normal'],
            height=40,
            fg_color=COLORS['success'],
            hover_color=COLORS['success_hover']
        ).pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(
            backup_buttons_frame,
            text="Yedekleme Klasörünü Aç",
            command=lambda: os.startfile(self.stock_manager.backup_folder),
            font=self.FONTS['normal'],
            height=40,
            fg_color=COLORS['accent'],
            hover_color=COLORS['secondary']
        ).pack(side="left", expand=True, padx=5)

    def create_settings_section(self, parent, title, description="", **kwargs):
        """Ayarlar bölümü oluşturur"""
        section = ctk.CTkFrame(parent, fg_color=COLORS['card'])
        section.pack(fill="x", **kwargs)
        
        # Başlık
        ctk.CTkLabel(
            section,
            text=title,
            font=self.FONTS['subheader'],
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(10, 0))
        
        # Açıklama
        if description:
            ctk.CTkLabel(
                section,
                text=description,
                font=self.FONTS['small'],
                text_color=COLORS['text_secondary']
            ).pack(anchor="w", pady=(0, 10))
        
        return section

    def get_last_backup_date(self):
        """Son yedekleme tarihini döndürür"""
        try:
            backup_files = os.listdir(self.stock_manager.backup_folder)
            if not backup_files:
                return "Henüz yedekleme yapılmadı"
            
            # En son yedeklenen dosyanın tarihini al
            latest_backup = max(
                backup_files,
                key=lambda x: os.path.getctime(os.path.join(self.stock_manager.backup_folder, x))
            )
            
            # Dosya oluşturma tarihini al
            timestamp = os.path.getctime(os.path.join(self.stock_manager.backup_folder, latest_backup))
            date = datetime.fromtimestamp(timestamp)
            
            return date.strftime("%d.%m.%Y %H:%M")
        except:
            return "Bilinmiyor"

    def show_product_detail(self, product_id):
        # Ana pencere
        details_window = ctk.CTkToplevel(self)
        details_window.title("Ürün Detayları")
        details_window.geometry("600x800")
        details_window.configure(fg_color=COLORS['background'])
        
        # Ürün bilgilerini al
        product = self.stock_manager.products[str(product_id)]
        
        # Ürün bilgileri frame
        info_frame = ctk.CTkFrame(details_window, fg_color=COLORS['card'])
        info_frame.pack(fill="x", padx=20, pady=10)
        
        # Ürün adı
        ctk.CTkLabel(
            info_frame,
            text=product.name,
            font=self.FONTS['header']
        ).pack(pady=10)
        
        # Ürün detayları
        details = [
            ("Kategori:", product.category),
            ("Cinsiyet:", product.gender),
            ("Beden:", product.size),
            ("Renk:", product.color),
            ("Alış Fiyatı:", f"{product.purchase_price:.2f} TL"),
            ("Satış Fiyatı:", f"{product.price:.2f} TL"),
            ("Stok:", str(product.stock_quantity))
        ]
        
        for label, value in details:
            detail_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            detail_frame.pack(fill="x", padx=20, pady=2)
            
            ctk.CTkLabel(
                detail_frame,
                text=label,
                font=self.FONTS['normal'],
                text_color=COLORS['text_secondary']
            ).pack(side="left")
            
            ctk.CTkLabel(
                detail_frame,
                text=value,
                font=self.FONTS['normal']
            ).pack(side="right")
        
        # Stok hareketi formu
        form_frame = ctk.CTkFrame(details_window, fg_color=COLORS['card'])
        form_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            form_frame,
            text="Stok Hareketi Ekle",
            font=self.FONTS['subheader']
        ).pack(pady=10)
        
        # Hareket tipi
        ctk.CTkLabel(
            form_frame,
            text="Hareket Tipi",
            font=self.FONTS['normal']
        ).pack(pady=(10,0))
        
        sales_place = ctk.CTkComboBox(
            form_frame,
            values=["giriş", "çıkış"],
            font=self.FONTS['normal'],
            width=200
        )
        sales_place.pack(pady=5)
        
        # Miktar
        ctk.CTkLabel(
            form_frame,
            text="Miktar",
            font=self.FONTS['normal']
        ).pack(pady=(10,0))
        
        quantity_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Miktar giriniz",
            width=200
        )
        quantity_entry.pack(pady=5)
        
        # Açıklama
        ctk.CTkLabel(
            form_frame,
            text="Açıklama",
            font=self.FONTS['normal']
        ).pack(pady=(10,0))
        
        description_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Açıklama giriniz",
            width=200
        )
        description_entry.pack(pady=5)
        
        def add_movement():
            try:
                qty = int(quantity_entry.get())
                desc = description_entry.get()
                
                self.stock_manager.add_stock_movement(
                    product_id=product_id,
                    movement_type=sales_place.get(),
                    quantity=qty,
                    description=desc
                )
                
                # Tabloyu güncelle
                self.refresh_tables()
                # Detay penceresini kapat
                details_window.destroy()
                messagebox.showinfo("Başarılı", "Stok hareketi eklendi!")
                
            except ValueError as e:
                messagebox.showerror("Hata", str(e))
            except Exception as e:
                messagebox.showerror("Hata", f"Bir hata oluştu: {e}")
        
        # Kaydet butonu
        ctk.CTkButton(
            form_frame,
            text="Kaydet",
            command=add_movement,
            font=self.FONTS['normal'],
            fg_color=COLORS['primary'],
            hover_color=COLORS['secondary']
        ).pack(pady=10)

    def check_updates(self, show_message=False):
        """
        Güncellemeleri kontrol eder
        Args:
            show_message: True ise güncelleme mesajını gösterir
        """
        try:
            from updater import check_for_updates
            is_updated = check_for_updates(silent=not show_message)
            return is_updated
        except Exception as e:
            if show_message:
                messagebox.showerror("Hata", f"Güncelleme kontrolü yapılamadı: {e}")
            return False

def main():
    app = ModernStockApp()
    app.mainloop()

if __name__ == "__main__":
    main() 