import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from stock_management import StockManager, Product
from datetime import datetime
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
    'table_header_text': '#845EC2' # Tablo başlık yazı rengi
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
    def __init__(self):
        super().__init__()
        
        # Uygulama klasörünü başlat
        self.app_folder = initialize_app()
        
        # Görünüm kalitesi ayarları
        self.tk.call('tk', 'scaling', 2.0)  # HiDPI desteği
        
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
        
        # Font tanımlamaları
        self.FONTS = {
            'header': ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),    # 20'den 18'e
            'subheader': ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), # 16'dan 15'e
            'normal': ctk.CTkFont(family="Segoe UI", size=12),                   # 13'ten 12'ye
            'small': ctk.CTkFont(family="Segoe UI", size=11),                    # 12'den 11'e
            'large': ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),     # 24'ten 22'ye
            'button': ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),    # 13'ten 12'ye
            'table': ('Segoe UI', 12),                                           # 13'ten 12'ye
            'table_header': ('Segoe UI', 12, 'bold')                             # 13'ten 12'ye
        }
        
        # Ana pencere ayarları
        self.title("Stok Yönetim Sistemi")
        self.geometry("1400x800")
        self.configure(fg_color=COLORS['background'])
        
        self.stock_manager = StockManager()
        
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

        # Güncelleme kontrolü
        self.after(1000, self.check_updates)  # Program başladıktan 1 saniye sonra kontrol et

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
            text="v1.0.0",
            font=self.FONTS['small'],
            text_color=COLORS['text_secondary']
        )
        version_label.pack()

    def show_dashboard(self):
        self.clear_content()
        
        # Üst bilgi kartları
        info_frame = ctk.CTkFrame(self.content_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        info_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        
        # Bugünün tarihi
        today = datetime.now().date()
        
        # Bugünkü ve aylık satış hesaplamaları
        today_movements = [m for m in self.stock_manager.stock_movements 
                          if m.date.date() == today]
        
        # Bugünkü satışlar
        today_sales = sum(
            self.stock_manager.products[m.product_id].price * m.quantity
            for m in today_movements
            if m.movement_type == "çıkış" 
            and m.product_id in self.stock_manager.products
        )
        
        # Aylık satışlar
        monthly_sales = sum(
            self.stock_manager.products[m.product_id].price * m.quantity
            for m in self.stock_manager.stock_movements
            if m.movement_type == "çıkış" 
            and (today - m.date.date()).days <= 30
            and m.product_id in self.stock_manager.products
        )
        
        # Bugünkü işlem sayıları
        today_inputs = [m for m in today_movements if m.movement_type == "giriş"]
        today_outputs = [m for m in today_movements if m.movement_type == "çıkış"]
        
        # Günlük ve aylık kar hesapla
        daily_profit = self.stock_manager.calculate_daily_profit()
        monthly_profit = self.stock_manager.calculate_monthly_profit()
        
        # İstatistik kartları
        self.create_stat_card(
            info_frame,
            "Toplam Ürün",
            f"{len(self.stock_manager.products)} adet",
            "📦",
            0
        )

        # Bugünkü işlemler kartını güncelle
        total_movements = len(today_inputs) + len(today_outputs)
        self.create_stat_card(
            info_frame,
            "Bugünkü İşlemler",
            f"{total_movements} hareket",
            "🔄",
            1
        )

        self.create_stat_card(
            info_frame,
            "Bugünkü Kar",
            f"{daily_profit:.2f} TL",
            "💰",
            2
        )

        self.create_stat_card(
            info_frame,
            "Aylık Kar",
            f"{monthly_profit:.2f} TL",
            "📈",
            3
        )

        self.create_stat_card(
            info_frame,
            "Toplam Değer",
            f"{sum(p.price * p.stock_quantity for p in self.stock_manager.products.values()):.2f} TL",
            "💵",
            4
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

    def create_stat_card(self, parent, title, value, icon, column):
        card = ctk.CTkFrame(parent, fg_color=COLORS['card'], corner_radius=15)
        card.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
        
        # İkon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=32),  # Eski haline döndü (24'ten 32'ye)
            text_color=COLORS['primary']
        )
        icon_label.pack(pady=(15, 5))
        
        # Değer
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),  # Eski haline döndü (18'den 24'e)
            text_color=COLORS['text']
        )
        value_label.pack(pady=5)
        
        # Başlık
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14),  # Eski haline döndü (12'den 14'e)
            text_color=COLORS['text_secondary']
        )
        title_label.pack(pady=(5, 15))

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
        
        # Ana container
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Başlık
        header_frame = ctk.CTkFrame(container, fg_color=COLORS['primary'], corner_radius=10)
        header_frame.pack(fill="x", padx=2, pady=2)
        
        ctk.CTkLabel(
            header_frame,
            text="➕ Yeni Ürün Ekle",
            font=self.FONTS['header'],
            text_color=COLORS['text']
        ).pack(pady=15)
        
        # Form container
        form_frame = ctk.CTkFrame(container, fg_color=COLORS['card'], corner_radius=10)
        form_frame.pack(fill="x", pady=10, padx=2)
        
        # Form alanları için grid yapılandırması
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Form alanları
        self.product_entries = {}
        self.selected_sizes = []  # Seçili bedenleri tutacak liste
        
        fields = [
            {'label': 'Ürün ID', 'key': 'id', 'icon': '🏷️', 'type': 'entry'},
            {'label': 'Ürün Adı', 'key': 'name', 'icon': '📝', 'type': 'entry'},
            {'label': 'Kategori', 'key': 'category', 'icon': '📁', 'type': 'combobox', 
             'values': ["Seçiniz...", "Pantolon", "Tişört", "Gömlek", "Elbise", "Ceket", "Ayakkabı"]},
            {'label': 'Cinsiyet', 'key': 'gender', 'icon': '👤', 'type': 'combobox', 
             'values': ["Seçiniz...", "Erkek", "Kadın", "Unisex"]},
            {'label': 'Beden', 'key': 'size', 'icon': '📏', 'type': 'size_buttons'},
            {'label': 'Renk', 'key': 'color', 'icon': '🎨', 'type': 'combobox', 
             'values': ["Seçiniz...", "Siyah", "Beyaz", "Kırmızı", "Mavi", "Yeşil", "Lacivert"]},
            {'label': 'Alış Fiyatı', 'key': 'purchase_price', 'icon': '💰', 'type': 'entry'},
            {'label': 'Satış Fiyatı', 'key': 'price', 'icon': '💵', 'type': 'entry'},
            {'label': 'Fotoğraf', 'key': 'image', 'icon': '📸', 'type': 'image'}  # Yeni alan
        ]
        
        def update_size_buttons(category):
            # Eski beden butonlarını temizle
            for widget in size_frame.winfo_children():
                widget.destroy()
            
            # Seçili bedenleri sıfırla
            self.selected_sizes.clear()
            
            if category == "Seçiniz...":
                # Kategori seçilmediğinde mesaj göster
                ctk.CTkLabel(
                    size_frame,
                    text="Lütfen önce kategori seçiniz",
                    font=self.FONTS['normal'],
                    text_color=COLORS['text_secondary']
                ).pack(pady=10)
                return
            
            # Kategoriye göre bedenleri al
            sizes = self.size_options[category]
            
            # Beden butonları için frame
            buttons_frame = ctk.CTkFrame(size_frame, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=10, pady=5)
            
            # Beden butonlarını oluştur
            for j, size in enumerate(sizes):
                btn = ctk.CTkButton(
                    buttons_frame,
                    text=size,
                    width=50,
                    height=30,
                    fg_color="transparent",
                    text_color=COLORS['text'],
                    hover_color=COLORS['secondary'],
                    border_width=1,
                    border_color=COLORS['border']
                )
                btn.grid(row=j//6, column=j%6, padx=2, pady=2)
                
                def toggle_size(s=size, b=btn):
                    if s in self.selected_sizes:
                        self.selected_sizes.remove(s)
                        b.configure(fg_color="transparent", text_color=COLORS['text'])
                    else:
                        self.selected_sizes.append(s)
                        b.configure(fg_color=COLORS['primary'], text_color=COLORS['text'])
                
                btn.configure(command=lambda s=size, b=btn: toggle_size(s, b))
            
            # Seçili bedenleri göstermek için etiket
            self.size_label = ctk.CTkLabel(
                size_frame,
                text="Seçili bedenler: ",
                font=self.FONTS['small'],
                text_color=COLORS['text_secondary']
            )
            self.size_label.pack(pady=10)
        
        # Form alanlarını oluştur
        for i, field in enumerate(fields):
            # Etiket
            ctk.CTkLabel(
                form_frame,
                text=f"{field['icon']} {field['label']}:",
                font=self.FONTS['normal'],
                text_color=COLORS['text_secondary']
            ).grid(row=i, column=0, padx=(20,10), pady=10, sticky="e")
            
            if field['type'] == 'size_buttons':
                # Beden butonları için frame
                size_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
                size_frame.grid(row=i, column=1, padx=(0,20), pady=10, sticky="ew")
                
                # Başlangıçta mesaj göster
                ctk.CTkLabel(
                    size_frame,
                    text="Lütfen önce kategori seçiniz",
                    font=self.FONTS['normal'],
                    text_color=COLORS['text_secondary']
                ).pack(pady=10)
                continue
            
            elif field['key'] == 'category':
                combo = ctk.CTkComboBox(
                    form_frame,
                    height=40,
                    font=self.FONTS['normal'],
                    values=field['values'],
                    state="readonly",
                    command=update_size_buttons  # Kategori değiştiğinde bedenleri güncelle
                )
                combo.grid(row=i, column=1, padx=(0,20), pady=10, sticky="ew")
                combo.set(field['values'][0])
                self.product_entries[field['key']] = combo
                continue
            
            # Giriş alanı veya combobox
            if field['type'] == 'entry':
                entry = ctk.CTkEntry(
                    form_frame,
                    height=40,
                    font=self.FONTS['normal'],
                    placeholder_text=f"{field['label']} giriniz..."
                )
                entry.grid(row=i, column=1, padx=(0,20), pady=10, sticky="ew")
                self.product_entries[field['key']] = entry
            elif field['type'] == 'combobox':
                combo = ctk.CTkComboBox(
                    form_frame,
                    height=40,
                    font=self.FONTS['normal'],
                    values=field['values'],
                    state="readonly"
                )
                combo.grid(row=i, column=1, padx=(0,20), pady=10, sticky="ew")
                combo.set(field['values'][0])
                self.product_entries[field['key']] = combo
            elif field['type'] == 'image':
                # Fotoğraf seçme alanı için frame
                image_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
                image_frame.grid(row=i, column=1, padx=(0,20), pady=10, sticky="ew")
                
                # Fotoğraf önizleme alanı
                preview_frame = ctk.CTkFrame(image_frame, width=150, height=150)
                preview_frame.grid(row=0, column=0, padx=5)
                preview_frame.grid_propagate(False)
                
                # Önizleme etiketi
                preview_label = ctk.CTkLabel(
                    preview_frame,
                    text="Önizleme",
                    font=self.FONTS['small']
                )
                preview_label.place(relx=0.5, rely=0.5, anchor="center")
                
                # Butonlar için frame
                button_frame = ctk.CTkFrame(image_frame, fg_color="transparent")
                button_frame.grid(row=0, column=1, padx=5)
                
                def select_image():
                    file_path = filedialog.askopenfilename(
                        title="Fotoğraf Seç",
                        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
                    )
                    if file_path:
                        try:
                            # Resmi yükle ve boyutlandır
                            image = Image.open(file_path)
                            image.thumbnail((140, 140))  # Önizleme boyutu
                            photo = ImageTk.PhotoImage(image)
                            
                            # Önizleme etiketini güncelle
                            preview_label.configure(image=photo, text="")
                            preview_label.image = photo  # Referansı koru
                            
                            # Dosya yolunu sakla
                            self.product_entries['image'] = file_path
                            
                        except Exception as e:
                            messagebox.showerror("Hata", f"Fotoğraf yüklenirken hata oluştu: {str(e)}")

                def remove_image():
                    preview_label.configure(image="", text="Önizleme")
                    self.product_entries['image'] = None
                
                # Fotoğraf seç butonu
                select_button = ctk.CTkButton(
                    button_frame,
                    text="Fotoğraf Seç",
                    font=self.FONTS['normal'],
                    height=35,
                    command=select_image
                )
                select_button.pack(pady=5)
                
                # Fotoğraf kaldır butonu
                remove_button = ctk.CTkButton(
                    button_frame,
                    text="Fotoğrafı Kaldır",
                    font=self.FONTS['normal'],
                    height=35,
                    fg_color="transparent",
                    border_width=1,
                    command=remove_image
                )
                remove_button.pack(pady=5)
                
                # Başlangıçta None olarak ayarla
                self.product_entries['image'] = None
        
        # Kaydet butonu
        save_button = ctk.CTkButton(
            form_frame,
            text="💾 Kaydet",
            font=self.FONTS['button'],
            height=40,
            command=self.save_product
        )
        save_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def save_product(self):
        try:
            # Form verilerini al
            product_data = {
                'id': self.product_entries['id'].get(),
                'name': self.product_entries['name'].get(),
                'category': self.product_entries['category'].get(),
                'gender': self.product_entries['gender'].get(),
                'size': ", ".join(self.selected_sizes),
                'color': self.product_entries['color'].get(),
                'purchase_price': float(self.product_entries['purchase_price'].get()),
                'price': float(self.product_entries['price'].get()),
                'image_path': self.product_entries['image']  # Fotoğraf yolu eklendi
            }
            
            # Boş alan kontrolü
            for key, value in product_data.items():
                if value == "" or value == "Seçiniz...":
                    messagebox.showerror("Hata", "Lütfen tüm alanları doldurunuz!")
                    return
            
            # Fiyat kontrolü
            if product_data['purchase_price'] <= 0 or product_data['price'] <= 0:
                messagebox.showerror("Hata", "Fiyatlar 0'dan büyük olmalıdır!")
                return
            
            # Ürünü oluştur ve kaydet
            new_product = Product(**product_data)
            if self.stock_manager.add_product(new_product):
                messagebox.showinfo("Başarılı", "Ürün başarıyla eklendi!")
                self.show_dashboard()
            
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli fiyat değerleri giriniz!")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def show_stock_movement(self):
        self.clear_content()
        
        # Ana container
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Grid yapılandırması
        container.grid_columnconfigure(0, weight=3)  # Form için
        container.grid_columnconfigure(1, weight=1)  # Bilgi kartı için
        container.grid_rowconfigure(0, weight=1)
        
        # Sol panel - Form
        form_frame = ctk.CTkFrame(container, corner_radius=15)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Başlık
        header_frame = ctk.CTkFrame(form_frame, fg_color=COLORS['primary'], corner_radius=10)
        header_frame.pack(fill="x", padx=2, pady=2)
        
        ctk.CTkLabel(
            header_frame,
            text="🔄 Stok Hareket İşlemi",
            font=self.FONTS['header'],
            text_color=COLORS['text']
        ).pack(pady=15)
        
        # Form içeriği
        content_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Grid yapılandırması
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Ürün seçimi
        ctk.CTkLabel(
            content_frame,
            text="📦 Ürün Seçimi",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=0, padx=(0, 10), pady=10, sticky="e")
        
        product_combobox = ctk.CTkComboBox(
            content_frame,
            values=[f"{p.id} - {p.name}" for p in self.stock_manager.products.values()],
            height=40,
            font=self.FONTS['normal']
        )
        product_combobox.grid(row=0, column=1, pady=10, sticky="ew")
        
        # Miktar
        ctk.CTkLabel(
            content_frame,
            text="🔢 Miktar",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).grid(row=1, column=0, padx=(0, 10), pady=10, sticky="e")
        
        quantity_entry = ctk.CTkEntry(
            content_frame,
            height=40,
            font=self.FONTS['normal'],
            placeholder_text="Miktar giriniz..."
        )
        quantity_entry.grid(row=1, column=1, pady=10, sticky="ew")
        
        # Hareket tipi seçimi
        ctk.CTkLabel(
            content_frame,
            text="🔄 İşlem Tipi",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).grid(row=2, column=0, padx=(0, 10), pady=10, sticky="e")
        
        # İşlem butonları için frame
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=1, pady=10, sticky="ew")
        
        # Grid yapılandırması - her sütuna eşit ağırlık ver
        buttons_frame.grid_columnconfigure(0, weight=1, uniform="button")
        buttons_frame.grid_columnconfigure(1, weight=1, uniform="button")
        buttons_frame.grid_columnconfigure(2, weight=1, uniform="button")
        
        # Satış yeri seçimi (frame)
        sales_place_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        sales_place_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        sales_place_frame.grid_remove()  # Başlangıçta gizli
        
        # Satış yeri seçimi
        ctk.CTkLabel(
            sales_place_frame,
            text="🏪 Satış Yeri",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=0, padx=(0, 10), pady=10, sticky="e")
        
        sales_place = ctk.CTkComboBox(
            sales_place_frame,
            values=["Seçiniz...", "Mağaza", "Instagram", "Trendyol", "Hepsiburada", "Diğer"],
            height=40,
            font=self.FONTS['normal']
        )
        sales_place.grid(row=0, column=1, pady=10, sticky="ew")
        sales_place.set("Seçiniz...")
        
        def handle_movement(move_type, is_sale=False):
            try:
                product_id = product_combobox.get().split(" - ")[0]
                qty = int(quantity_entry.get())
                desc = description_entry.get("1.0", "end-1c")
                
                # Satış işlemi için
                if is_sale:
                    sales_place_frame.grid()  # Satış yeri seçimini göster
                    if not sales_place.get() or sales_place.get() == "Seçiniz...":
                        messagebox.showerror("Hata", "Lütfen satış yerini seçiniz!")
                        return
                    desc = f"Satış Yeri: {sales_place.get()} | " + desc
                else:
                    sales_place_frame.grid_remove()  # Satış yeri seçimini gizle
                
                if self.stock_manager.add_stock_movement(product_id, move_type, qty, desc):
                    messagebox.showinfo("Başarılı", "Stok hareketi kaydedildi!")
                    self.show_dashboard()
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli bir miktar giriniz!")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
        
        # Giriş butonu
        entry_button = ctk.CTkButton(
            buttons_frame,
            text="📥 Giriş",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),  # 14'ten 16'ya çıkarıldı
            height=40,
            width=120,
            fg_color=COLORS['accent'],
            command=lambda: handle_movement("giriş")
        )
        entry_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        # Satış butonu
        sale_button = ctk.CTkButton(
            buttons_frame,
            text="💰 Satış",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),  # 14'ten 16'ya çıkarıldı
            height=40,
            width=120,
            fg_color="#2ecc71",  # Yeşil
            hover_color="#27ae60",  # Koyu yeşil
            command=lambda: handle_movement("çıkış", True)
        )
        sale_button.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Çıkış butonu
        exit_button = ctk.CTkButton(
            buttons_frame,
            text="📤 Çıkış",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),  # 14'ten 16'ya çıkarıldı
            height=40,
            width=120,
            fg_color="#e74c3c",  # Kırmızı
            hover_color="#c0392b",  # Koyu kırmızı
            command=lambda: handle_movement("çıkış", False)
        )
        exit_button.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Açıklama
        ctk.CTkLabel(
            content_frame,
            text="📝 Açıklama",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).grid(row=4, column=0, padx=(0, 10), pady=10, sticky="e")
        
        description_entry = ctk.CTkTextbox(
            content_frame,
            height=80,
            font=self.FONTS['normal']
        )
        description_entry.grid(row=4, column=1, pady=10, sticky="ew")

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
        
        # Ana container
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Başlık
        header_frame = ctk.CTkFrame(container, fg_color=COLORS['primary'], corner_radius=10)
        header_frame.pack(fill="x", padx=2, pady=2)
        
        ctk.CTkLabel(
            header_frame,
            text="📊 Raporlar ve Analizler",
            font=self.FONTS['header'],
            text_color=COLORS['text']
        ).pack(pady=15)
        
        # Filtre Frame
        filter_frame = ctk.CTkFrame(container, fg_color=COLORS['card'], corner_radius=10)
        filter_frame.pack(fill="x", pady=10)
        
        # Tarih aralığı seçimi
        date_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            date_frame,
            text="📅 Tarih Aralığı:",
            font=self.FONTS['normal']
        ).pack(side="left", padx=5)
        
        # Tarih seçiciler eklenecek...
        
        # Özet kartları
        stats_frame = ctk.CTkFrame(container)
        stats_frame.pack(fill="x", pady=10)
        stats_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # Grafik seçenekleri
        tabs = ctk.CTkTabview(
            container,
            fg_color=COLORS['card'],
            segmented_button_fg_color=COLORS['primary'],
            segmented_button_selected_color=COLORS['secondary'],
            segmented_button_selected_hover_color=COLORS['accent'],
            text_color=COLORS['text']
        )
        tabs.pack(fill="both", expand=True, pady=10)
        
        # Stok Durumu tab'ı
        stock_tab = tabs.add("📦 Stok Durumu")
        self.create_stock_chart(stock_tab)
        
        # Satış Trendi tab'ı
        sales_tab = tabs.add("💰 Satış Trendi")
        self.create_sales_chart(sales_tab)
        
        # Kategori Analizi tab'ı
        category_tab = tabs.add("📊 Kategori Analizi")
        self.create_category_chart(category_tab)
        
        # Kar Analizi tab'ı
        profit_tab = tabs.add("📈 Kar Analizi")
        self.create_profit_chart(profit_tab)
        
        # Alt butonlar
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        # Excel'e aktar butonu
        ctk.CTkButton(
            button_frame,
            text="📥 Excel'e Aktar",
            command=self.export_to_excel,
            width=200,
            fg_color=COLORS['accent'],
            hover_color=COLORS['secondary'],
            font=self.FONTS['button']
        ).pack(side="left", padx=5)
        
        # PDF Raporu oluştur butonu
        ctk.CTkButton(
            button_frame,
            text="📄 PDF Raporu",
            command=self.create_pdf_report,
            width=200,
            fg_color=COLORS['primary'],
            hover_color=COLORS['secondary'],
            font=self.FONTS['button']
        ).pack(side="left", padx=5)

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

    def check_updates(self):
        try:
            from updater import check_for_updates
            check_for_updates()
        except Exception as e:
            print(f"Güncelleme kontrolü yapılamadı: {e}")

    def show_settings(self):
        self.clear_content()
        
        # Başlık
        header_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['primary'], corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=2)
        
        ctk.CTkLabel(
            header_frame,
            text="⚙️ Ayarlar",
            font=self.FONTS['header'],
            text_color=COLORS['text']
        ).pack(pady=15)
        
        # Ayarlar içeriği
        settings_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS['card'])
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Güncelleme bölümü
        update_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        update_frame.pack(fill="x", padx=20, pady=20)
        
        # Başlık
        ctk.CTkLabel(
            update_frame,
            text="Program Güncellemesi",
            font=self.FONTS['subheader'],
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 10))
        
        # Mevcut sürüm
        try:
            with open('version.json', 'r') as f:
                current_version = json.load(f)['version']
        except:
            current_version = "1.0.0"
        
        version_frame = ctk.CTkFrame(update_frame, fg_color="transparent")
        version_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            version_frame,
            text="Mevcut Sürüm:",
            font=self.FONTS['normal'],
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            version_frame,
            text=current_version,
            font=self.FONTS['normal']
        ).pack(side="left", padx=5)
        
        # Güncelleme butonu
        def check_update():
            try:
                from updater import check_for_updates
                check_for_updates()
            except Exception as e:
                messagebox.showerror("Hata", f"Güncelleme kontrolü yapılamadı: {e}")
        
        ctk.CTkButton(
            update_frame,
            text="🔄 Güncellemeleri Kontrol Et",
            command=check_update,
            font=self.FONTS['normal'],
            height=40,
            fg_color=COLORS['primary'],
            hover_color=COLORS['secondary']
        ).pack(pady=20)
        
        # Otomatik güncelleme kontrolü
        auto_update_var = ctk.BooleanVar(value=True)
        
        auto_update_check = ctk.CTkCheckBox(
            update_frame,
            text="Program başladığında güncellemeleri otomatik kontrol et",
            variable=auto_update_var,
            font=self.FONTS['normal'],
            text_color=COLORS['text'],
            fg_color=COLORS['primary']
        )
        auto_update_check.pack(pady=10)

def main():
    app = ModernStockApp()
    app.mainloop()

if __name__ == "__main__":
    main() 