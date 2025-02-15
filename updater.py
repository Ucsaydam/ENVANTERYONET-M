import requests
import os
import json
import sys
from tkinter import messagebox

# GitHub repo bilgileri
GITHUB_USER = "Ucsaydam"
REPO_NAME = "ENVANTERYONET-M"
BRANCH = "main"

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def check_for_updates():
    try:
        base_path = get_base_path()
        version_file = os.path.join(base_path, 'version.json')
        
        # GitHub'dan son sürümü kontrol et
        api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/releases/latest"
        response = requests.get(api_url)
        
        if response.status_code != 200:
            raise Exception("GitHub API'ye erişilemedi")
            
        latest_version = response.json()['tag_name']
        
        # Mevcut sürümü kontrol et
        with open(version_file, 'r') as f:
            current_version = json.load(f)['version']
        
        if latest_version > current_version:
            if messagebox.askyesno("Güncelleme Mevcut", 
                f"Yeni sürüm mevcut: {latest_version}\nŞu anki sürüm: {current_version}\n\nGüncellemek ister misiniz?"):
                
                # Güncellenecek dosyalar
                files_to_update = [
                    'stock_management.py',
                    'stock_management_gui.py',
                    'updater.py',
                    'version.json'
                ]
                
                # Dosyaları GitHub'dan indir
                for file in files_to_update:
                    file_path = os.path.join(base_path, file)
                    file_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{file}"
                    r = requests.get(file_url)
                    
                    if r.status_code == 200:
                        # Yedek oluştur
                        if os.path.exists(file_path):
                            backup_file = f"{file_path}.backup"
                            os.rename(file_path, backup_file)
                        
                        # Yeni dosyayı kaydet
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(r.text)
                    else:
                        raise Exception(f"{file} dosyası indirilemedi")
                
                messagebox.showinfo("Güncelleme Tamamlandı", 
                    "Program yeniden başlatılacak")
                
                # Programı yeniden başlat
                os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            messagebox.showinfo("Güncelleme Kontrolü", 
                "Program güncel! En son sürümü kullanıyorsunuz.")
            
    except Exception as e:
        messagebox.showerror("Hata", f"Güncelleme kontrol hatası: {e}") 