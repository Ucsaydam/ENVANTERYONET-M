import requests
import os
import json
import sys
import subprocess
from tkinter import messagebox

# GitHub repo bilgileri
GITHUB_USER = "Ucsaydam"
REPO_NAME = "ENVANTERYONET-M"
BRANCH = "main"

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def install_requirements():
    """Gerekli kütüphaneleri yükler"""
    try:
        # requirements.txt'yi oku
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # pip ile yükleme yap
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        return True
    except Exception as e:
        messagebox.showerror(
            "Hata",
            f"Kütüphaneler yüklenirken hata oluştu:\n{str(e)}"
        )
        return False

def check_for_updates(silent=False):
    """Güncellemeleri kontrol eder"""
    try:
        # GitHub'dan son sürümü kontrol et
        api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/releases/latest"
        response = requests.get(api_url)
        
        if response.status_code != 200:
            raise Exception("GitHub API'ye erişilemedi")
        
        # GitHub'dan en son sürümü al    
        latest_version = response.json()['tag_name']
        
        # Mevcut sürümü oku
        version_file = os.path.join(os.path.dirname(__file__), 'version.json')
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                current_version = json.load(f)['version']
        else:
            current_version = "1.0.2"
        
        if latest_version > current_version:
            if not silent:
                if messagebox.askyesno(
                    "Güncelleme Mevcut",
                    f"Yeni sürüm mevcut!\n\nMevcut sürüm: {current_version}\n"
                    f"Yeni sürüm: {latest_version}\n\nŞimdi güncellemek ister misiniz?"
                ):
                    # Önce gerekli kütüphaneleri yükle
                    if install_requirements():
                        get_updates()
            return False
        else:
            if not silent:
                messagebox.showinfo(
                    "Güncelleme Kontrolü",
                    "Program güncel! En son sürümü kullanıyorsunuz."
                )
            return True
            
    except Exception as e:
        if not silent:
            messagebox.showerror(
                "Hata",
                f"Güncelleme kontrolü yapılırken bir hata oluştu: {str(e)}"
            )
        return False

def get_updates():
    """Güncellemeleri indirir ve uygular"""
    try:
        base_path = get_base_path()
        
        # Güncellenecek dosyalar
        files_to_update = [
            'stock_management.py',
            'stock_management_gui.py',
            'updater.py',
            'version.json',
            'requirements.txt'
        ]
        
        # Dosyaları GitHub'dan indir
        for file in files_to_update:
            file_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{file}"
            response = requests.get(file_url)
            
            if response.status_code == 200:
                file_path = os.path.join(base_path, file)
                
                # Yedek oluştur
                if os.path.exists(file_path):
                    backup_path = f"{file_path}.backup"
                    os.rename(file_path, backup_path)
                
                # Yeni dosyayı kaydet
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                raise Exception(f"{file} dosyası indirilemedi (HTTP {response.status_code})")
        
        messagebox.showinfo(
            "Güncelleme Tamamlandı",
            "Güncelleme başarıyla tamamlandı. Program yeniden başlatılacak."
        )
        
        # Programı yeniden başlat
        python = sys.executable
        os.execl(python, python, *sys.argv)
        
    except Exception as e:
        messagebox.showerror(
            "Güncelleme Hatası",
            f"Güncelleme sırasında bir hata oluştu:\n{str(e)}"
        )
