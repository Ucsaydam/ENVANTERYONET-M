import json
from datetime import datetime
import os
import shutil

class Product:
    def __init__(self, id, name, category, gender, size, color, purchase_price, price, image_path=None):
        self.id = id
        self.name = name
        self.category = category  # örn: "Pantolon", "Tişört", "Elbise"
        self.gender = gender      # "Kadın" veya "Erkek"
        self.size = size         # "XS", "S", "M", "L", "XL" vb.
        self.color = color
        self.purchase_price = purchase_price
        self.price = price  # Satış fiyatı
        self.stock_quantity = 0  # Başlangıçta 0
        self.image_path = image_path
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'gender': self.gender,
            'size': self.size,
            'color': self.color,
            'purchase_price': self.purchase_price,
            'price': self.price,
            'stock_quantity': self.stock_quantity,
            'image_path': self.image_path
        }

class StockMovement:
    def __init__(self, product_id, movement_type, quantity, date=None, description=""):
        self.product_id = product_id
        self.movement_type = movement_type  # "giriş" veya "çıkış"
        self.quantity = quantity
        self.date = date or datetime.now()
        self.description = description
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'date': self.date.isoformat(),
            'description': self.description
        }

class StockManager:
    def __init__(self, store=None):
        # Belgeler klasöründe uygulama klasörü oluştur
        self.app_folder = os.path.join(os.path.expanduser("~"), "Documents", "Stok Yönetim")
        if not os.path.exists(self.app_folder):
            os.makedirs(self.app_folder)
        
        # Dosya yolları
        self.products_file = os.path.join(self.app_folder, "products.json")
        self.movements_file = os.path.join(self.app_folder, "stock_movements.json")
        self.backup_folder = os.path.join(self.app_folder, "backups")
        
        # Mağaza bilgisi
        self.store = store
        
        # Yedekleme klasörünü oluştur
        if not os.path.exists(self.backup_folder):
            os.makedirs(self.backup_folder)
        
        self.products = {}
        self.stock_movements = []
        self.load_products()
        self.load_movements()

    def load_products(self):
        try:
            print(f"Ürünler yükleniyor... Dosya: {self.products_file}")
            with open(self.products_file, 'r', encoding='utf-8') as file:
                products_data = json.load(file)
                print(f"Yüklenecek ürün sayısı: {len(products_data)}")
                
                self.products = {}  # Ürün listesini temizle
                
                for product_data in products_data:
                    print(f"\nÜrün verisi: {product_data}")
                    try:
                        # Ürünü oluştur
                        product = Product(
                            id=str(product_data['id']),  # ID'yi string'e çevir
                            name=product_data['name'],
                            category=product_data['category'],
                            gender=product_data['gender'],
                            size=product_data['size'],
                            color=product_data['color'],
                            purchase_price=float(product_data['purchase_price']),
                            price=float(product_data['price']),
                            image_path=product_data.get('image_path')
                        )
                        
                        # Stok miktarını ayarla
                        product.stock_quantity = int(product_data.get('stock_quantity', 0))
                        
                        # Ürünü sözlüğe ekle
                        self.products[product.id] = product
                        print(f"Ürün başarıyla yüklendi: {product.name} (ID: {product.id})")
                        
                    except Exception as e:
                        print(f"Ürün yüklenirken hata: {e}")
                        print(f"Hatalı ürün verisi: {product_data}")
                        continue
                
                print(f"\nToplam {len(self.products)} ürün yüklendi")
                
        except FileNotFoundError:
            print(f"Ürün dosyası bulunamadı: {self.products_file}")
            self.products = {}
        except json.JSONDecodeError as e:
            print(f"JSON dosyası hatalı: {e}")
            self.products = {}
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")
            self.products = {}

    def save_products(self):
        try:
            products_data = []
            for product in self.products.values():
                product_dict = {
                    'id': product.id,
                    'name': product.name,
                    'category': product.category,
                    'gender': product.gender,
                    'size': product.size,
                    'color': product.color,
                    'purchase_price': product.purchase_price,
                    'price': product.price,
                    'stock_quantity': product.stock_quantity,
                    'image_path': product.image_path
                }
                products_data.append(product_dict)
            
            with open(self.products_file, 'w', encoding='utf-8') as file:
                json.dump(products_data, file, ensure_ascii=False, indent=4)
                print("Ürünler başarıyla kaydedildi.")
        except Exception as e:
            print(f"Ürünler kaydedilirken hata oluştu: {e}")

    def add_product(self, product):
        if product.id in self.products:
            print(f"HATA: {product.id} ID'li ürün zaten mevcut!")
            return False
        self.products[product.id] = product
        self.save_products()
        print(f"{product.name} ürünü başarıyla eklendi.")
        return True

    def update_stock(self, product_id, quantity):
        if product_id in self.products:
            self.products[product_id].stock_quantity = quantity
            self.save_products()
            print(f"Stok güncellendi. Yeni stok miktarı: {quantity}")
            return True
        print("Ürün bulunamadı!")
        return False

    def delete_product(self, product_id):
        if product_id in self.products:
            deleted_product = self.products.pop(product_id)
            self.save_products()
            print(f"{deleted_product.name} ürünü silindi.")
            return True
        print("Silinecek ürün bulunamadı!")
        return False

    def search_products(self, **kwargs):
        """
        Ürünleri arama fonksiyonu
        Örnek: search_products(category="Tişört", gender="Erkek")
        """
        results = []
        for product in self.products.values():
            match = True
            for key, value in kwargs.items():
                if hasattr(product, key) and getattr(product, key).lower() != value.lower():
                    match = False
                    break
            if match:
                results.append(product)
        return results

    def get_stock_level(self, product_id):
        if product_id in self.products:
            return self.products[product_id].stock_quantity
        return None

    def list_low_stock_products(self, threshold=5):
        low_stock = []
        for product in self.products.values():
            if product.stock_quantity <= threshold:
                low_stock.append(product)
        return low_stock

    def load_movements(self):
        try:
            with open(self.movements_file, 'r', encoding='utf-8') as file:
                movements_data = json.load(file)
                self.stock_movements = [
                    StockMovement(
                        product_id=m['product_id'],
                        movement_type=m['movement_type'],
                        quantity=m['quantity'],
                        date=datetime.fromisoformat(m['date']),
                        description=m['description']
                    ) for m in movements_data
                ]
        except FileNotFoundError:
            self.stock_movements = []

    def save_movements(self):
        movements_data = [movement.to_dict() for movement in self.stock_movements]
        with open(self.movements_file, 'w', encoding='utf-8') as file:
            json.dump(movements_data, file, ensure_ascii=False, indent=4)

    def add_stock_movement(self, product_id, movement_type, quantity, description=""):
        """Stok hareketi ekler"""
        try:
            # Ürünü kontrol et
            if str(product_id) not in self.products:
                raise ValueError(f"Ürün bulunamadı: {product_id}")
            
            # Yeni stok hareketi oluştur
            movement = StockMovement(
                product_id=str(product_id),
                movement_type=movement_type,
                quantity=quantity,
                description=description
            )
            
            # Stok miktarını güncelle
            product = self.products[str(product_id)]
            if movement_type == "giriş":
                product.stock_quantity += quantity
            elif movement_type == "çıkış":
                if product.stock_quantity < quantity:
                    raise ValueError("Yetersiz stok!")
                product.stock_quantity -= quantity
            
            # Hareketi listeye ekle ve kaydet
            self.stock_movements.append(movement)
            self.save_movements()
            self.save_products()
            
            return True
            
        except Exception as e:
            print(f"Stok hareketi eklenirken hata: {e}")
            raise e

    def get_product_movements(self, product_id):
        """Bir ürünün tüm stok hareketlerini getir"""
        return [m for m in self.stock_movements if m.product_id == product_id]

    def get_stock_report(self, start_date=None, end_date=None):
        """Belirli tarih aralığındaki stok hareketlerini raporla"""
        movements = self.stock_movements
        if start_date:
            movements = [m for m in movements if m.date >= start_date]
        if end_date:
            movements = [m for m in movements if m.date <= end_date]
        
        report = {}
        for movement in movements:
            product = self.products.get(movement.product_id)
            if product:
                if product.id not in report:
                    report[product.id] = {
                        'name': product.name,
                        'giriş': 0,
                        'çıkış': 0
                    }
                report[product.id][movement.movement_type] += movement.quantity
        
        return report

    def calculate_daily_profit(self):
        """Günlük kar hesaplama"""
        today = datetime.now().date()
        daily_profit = 0
        
        # Bugünkü satışları bul
        today_sales = [m for m in self.stock_movements 
                      if m.date.date() == today and 
                      m.movement_type == "çıkış"]
        
        # Her satış için kar hesapla
        for sale in today_sales:
            if sale.product_id in self.products:
                product = self.products[sale.product_id]
                # Kar = (Satış Fiyatı - Alış Fiyatı) × Satış Miktarı
                profit = (product.price - product.purchase_price) * sale.quantity
                daily_profit += profit
        
        return daily_profit

    def calculate_monthly_profit(self):
        """Aylık kar hesaplama"""
        today = datetime.now().date()
        monthly_profit = 0
        
        # Son 30 günlük satışları bul
        monthly_sales = [m for m in self.stock_movements 
                        if (today - m.date.date()).days <= 30 and 
                        m.movement_type == "çıkış"]
        
        # Her satış için kar hesapla
        for sale in monthly_sales:
            if sale.product_id in self.products:
                product = self.products[sale.product_id]
                profit = (product.price - product.purchase_price) * sale.quantity
                monthly_profit += profit
        
        return monthly_profit

    def calculate_product_profit(self, product_id):
        """Belirli bir ürünün toplam karını hesapla"""
        if product_id not in self.products:
            return 0
        
        total_profit = 0
        sales = [m for m in self.stock_movements 
                if m.product_id == product_id and 
                m.movement_type == "çıkış"]
        
        product = self.products[product_id]
        for sale in sales:
            profit = (product.price - product.purchase_price) * sale.quantity
            total_profit += profit
        
        return total_profit

    def auto_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # JSON dosyalarını yedekle
        for file_name in ["products.json", "stock_movements.json"]:
            source = os.path.join(self.app_folder, file_name)
            if os.path.exists(source):
                backup_file = os.path.join(self.backup_folder, f"{timestamp}_{file_name}")
                shutil.copy2(source, backup_file)

    def calculate_profit(self, start_date=None, end_date=None):
        """
        Belirli bir tarih aralığındaki karı hesaplar
        Args:
            start_date: Başlangıç tarihi (datetime)
            end_date: Bitiş tarihi (datetime)
        Returns:
            dict: Toplam kar, satış tutarı, maliyet ve detaylı satış bilgileri
        """
        if not start_date:
            start_date = datetime.min
        if not end_date:
            end_date = datetime.max
        
        profit_data = {
            'total_profit': 0,
            'total_revenue': 0,  # Toplam gelir (satış tutarı)
            'total_cost': 0,     # Toplam maliyet (alış fiyatı)
            'total_value': 0,    # Toplam değer (stok × alış fiyatı)
            'sales_details': []
        }
        
        # Mevcut stok değerini hesapla
        for product in self.products.values():
            product_value = product.stock_quantity * product.purchase_price
            profit_data['total_value'] += product_value
        
        # Satış hareketlerini filtrele
        sales = [
            movement for movement in self.stock_movements
            if movement.movement_type == "çıkış" 
            and start_date <= movement.date <= end_date
        ]
        
        # Her satış için kar hesapla
        for sale in sales:
            product = self.products.get(sale.product_id)
            if product:
                # Satış tutarı (gelir)
                revenue = product.price * sale.quantity
                # Maliyet (alış fiyatı)
                cost = product.purchase_price * sale.quantity
                # Kar = Gelir - Maliyet
                profit = revenue - cost
                
                # Toplam değerleri güncelle
                profit_data['total_revenue'] += revenue
                profit_data['total_cost'] += cost
                profit_data['total_profit'] += profit
                
                # Detaylı satış bilgisi ekle
                sale_detail = {
                    'date': sale.date,
                    'product_name': product.name,
                    'quantity': sale.quantity,
                    'revenue': revenue,
                    'cost': cost,
                    'profit': profit,
                    'profit_margin': (profit / revenue * 100) if revenue > 0 else 0,
                    'description': sale.description,
                    'purchase_price': product.purchase_price,
                    'selling_price': product.price
                }
                profit_data['sales_details'].append(sale_detail)
        
        # Kar marjı hesapla
        if profit_data['total_revenue'] > 0:
            profit_data['total_margin'] = (profit_data['total_profit'] / profit_data['total_revenue']) * 100
        else:
            profit_data['total_margin'] = 0
        
        return profit_data

class ProfitAnalysis:
    def __init__(self, stock_manager):
        self.stock_manager = stock_manager
        self.overhead_costs = {
            'kira': 0,
            'elektrik': 0,
            'personel': 0,
            'diğer': 0
        }
    
    def calculate_product_profitability(self, product_id):
        product = self.stock_manager.products.get(product_id)
        if not product:
            return None
            
        # Satış fiyatı ve alış fiyatı farkından kar hesapla
        gross_profit = product.price - product.purchase_price
        margin_percentage = (gross_profit / product.price) * 100
        
        # Son 30 günlük satışları bul
        monthly_sales = [m for m in self.stock_manager.stock_movements 
                        if m.product_id == product_id 
                        and m.movement_type == "çıkış"
                        and (datetime.now() - m.date).days <= 30]
        
        total_sales = sum(m.quantity for m in monthly_sales)
        total_revenue = total_sales * product.price
        total_cost = total_sales * product.purchase_price
        monthly_profit = total_revenue - total_cost
        
        return {
            'product_name': product.name,
            'purchase_price': product.purchase_price,
            'selling_price': product.price,
            'gross_profit': gross_profit,
            'margin_percentage': margin_percentage,
            'monthly_sales': total_sales,
            'monthly_revenue': total_revenue,
            'monthly_profit': monthly_profit
        }
    
    def get_most_profitable_products(self, limit=5):
        all_profits = []
        for product_id in self.stock_manager.products:
            profit_data = self.calculate_product_profitability(product_id)
            if profit_data:
                all_profits.append(profit_data)
        
        # Aylık kara göre sırala
        return sorted(all_profits, key=lambda x: x['monthly_profit'], reverse=True)[:limit]
    
    def get_profit_summary(self):
        total_inventory_value = sum(p.purchase_price * p.stock_quantity 
                                  for p in self.stock_manager.products.values())
        
        total_potential_revenue = sum(p.price * p.stock_quantity 
                                    for p in self.stock_manager.products.values())
        
        potential_profit = total_potential_revenue - total_inventory_value
        
        return {
            'inventory_value': total_inventory_value,
            'potential_revenue': total_potential_revenue,
            'potential_profit': potential_profit,
            'overhead_costs': sum(self.overhead_costs.values())
        }

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    print("\n=== STOK YÖNETİM SİSTEMİ ===")
    print("1. Yeni Ürün Ekle")
    print("2. Stok Girişi Yap")
    print("3. Stok Çıkışı Yap")
    print("4. Ürünleri Listele")
    print("5. Stok Hareketlerini Görüntüle")
    print("6. Düşük Stok Raporu")
    print("7. Ürün Ara")
    print("8. Ürün Sil")
    print("0. Çıkış")
    return input("\nSeçiminiz (0-8): ")

def get_product_info():
    print("\n=== Yeni Ürün Bilgileri ===")
    return Product(
        id=input("Ürün ID: "),
        name=input("Ürün Adı: "),
        category=input("Kategori: "),
        gender=input("Cinsiyet (Erkek/Kadın/Unisex): "),
        size=input("Beden: "),
        color=input("Renk: "),
        purchase_price=float(input("Alış Fiyatı: ")),
        price=float(input("Satış Fiyatı: ")),
        stock_quantity=0
    )

def main():
    stock_manager = StockManager()
    
    while True:
        clear_screen()
        choice = show_menu()
        
        if choice == "0":
            print("\nProgramdan çıkılıyor...")
            break
            
        elif choice == "1":
            try:
                urun = get_product_info()
                stock_manager.add_product(urun)
            except ValueError as e:
                print(f"\nHata: {e}")
            input("\nDevam etmek için Enter'a basın...")
            
        elif choice == "2":
            print("\n=== Stok Girişi ===")
            product_id = input("Ürün ID: ")
            try:
                quantity = int(input("Giriş Miktarı: "))
                description = input("Açıklama: ")
                stock_manager.add_stock_movement(product_id, "giriş", quantity, description)
            except ValueError:
                print("\nHata: Geçersiz miktar!")
            input("\nDevam etmek için Enter'a basın...")
            
        elif choice == "3":
            print("\n=== Stok Çıkışı ===")
            product_id = input("Ürün ID: ")
            try:
                quantity = int(input("Çıkış Miktarı: "))
                description = input("Açıklama: ")
                stock_manager.add_stock_movement(product_id, "çıkış", quantity, description)
            except ValueError:
                print("\nHata: Geçersiz miktar!")
            input("\nDevam etmek için Enter'a basın...")
            
        elif choice == "4":
            print("\n=== Ürün Listesi ===")
            for product in stock_manager.products.values():
                print(f"\nID: {product.id}")
                print(f"Ürün: {product.name}")
                print(f"Kategori: {product.category}")
                print(f"Cinsiyet: {product.gender}")
                print(f"Beden: {product.size}")
                print(f"Renk: {product.color}")
                print(f"Alış Fiyatı: {product.purchase_price} TL")
                print(f"Satış Fiyatı: {product.price} TL")
                print(f"Kar Marjı: %{((product.price - product.purchase_price) / product.purchase_price * 100):.1f}")
                print(f"Stok: {product.stock_quantity} adet")
            input("\nDevam etmek için Enter'a basın...")
            
        elif choice == "5":
            print("\n=== Stok Hareketleri ===")
            product_id = input("Ürün ID (tüm hareketler için boş bırakın): ")
            if product_id:
                movements = stock_manager.get_product_movements(product_id)
            else:
                movements = stock_manager.stock_movements
                
            for m in movements:
                product = stock_manager.products.get(m.product_id)
                if product:
                    print(f"\nÜrün: {product.name}")
                    print(f"Tarih: {m.date}")
                    print(f"İşlem: {m.movement_type}")
                    print(f"Miktar: {m.quantity}")
                    print(f"Açıklama: {m.description}")
            input("\nDevam etmek için Enter'a basın...")
            
        elif choice == "6":
            print("\n=== Düşük Stok Raporu ===")
            threshold = int(input("Eşik değeri (varsayılan:5): ") or "5")
            low_stock = stock_manager.list_low_stock_products(threshold)
            for product in low_stock:
                print(f"\n{product.name} - Stok: {product.stock_quantity} adet")
            input("\nDevam etmek için Enter'a basın...")
            
        elif choice == "7":
            print("\n=== Ürün Arama ===")
            print("(Boş bırakılan alanlar dikkate alınmayacak)")
            category = input("Kategori: ")
            gender = input("Cinsiyet: ")
            
            search_params = {}
            if category: search_params['category'] = category
            if gender: search_params['gender'] = gender
            
            results = stock_manager.search_products(**search_params)
            print("\nArama Sonuçları:")
            for product in results:
                print(f"\n{product.name} - {product.category} - {product.gender}")
                print(f"Stok: {product.stock_quantity} adet")
            input("\nDevam etmek için Enter'a basın...")
            
        elif choice == "8":
            print("\n=== Ürün Silme ===")
            product_id = input("Silinecek Ürün ID: ")
            stock_manager.delete_product(product_id)
            input("\nDevam etmek için Enter'a basın...")
        
        else:
            print("\nGeçersiz seçim!")
            input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main() 