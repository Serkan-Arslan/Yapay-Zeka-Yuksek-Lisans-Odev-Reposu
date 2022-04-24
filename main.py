import tkinter as tk
import sqlite3 as sql
from datetime import date
from tkinter import ttk, END
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import messagebox
from PIL import ImageTk, Image

anaekran = tk.Tk()
anaekran.geometry("1000x1000")
anaekran.title("Yatırım Portföyüm")

bugun = date.today().strftime("%d/%m/%Y")


# Ekranı ortalamak için yazdığım method
def ekran_ortala(ek, w=300, h=200):
    ws = ek.winfo_screenwidth()
    hs = ek.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    ek.geometry('%dx%d+%d+%d' % (w, h, x, y))


ekran_ortala(anaekran, 1000, 1000)

# Selenium ile WebScrapping Kodları
chrome_options=webdriver.ChromeOptions()
chrome_options.headless= True

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.binance.com/en/markets")
texts = [my_elem.text for my_elem in WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located(
    (By.XPATH, "//div[@id='tabContainer']//div[@direction='ltr']//div[@data-area='left']//div[@data-bn-type='text']")))]
coins = [texts[i] for i in range(len(texts)) if i % 3 == 1]
prices = [texts[i] for i in range(len(texts)) if i % 3 == 2]
print(coins)
print(prices)

# Ana Ekrandaki kripto para değerleri
kripto_degerler_ana = ttk.Treeview(anaekran, columns=("kripto_adi", "degeri"), show="headings", height=35)
kripto_degerler_ana.heading("kripto_adi", text="Kripto Adı", anchor="center")
kripto_degerler_ana.heading("degeri", text="Değeri", anchor="center")
kripto_degerler_ana.place(x=200, y=20)
degerler = []
for i in range(len(coins)):
    degerler.append([coins[i], prices[i]])

print(degerler)
for i in degerler:
    kripto_degerler_ana.insert("", END, values=i)

# SQL bağlantı kodları
varliklar_db = sql.connect("varliklar")
varliklar_im = varliklar_db.cursor()
varliklar_im.execute(
    "CREATE TABLE IF NOT EXISTS varliklarim (varlik_ad,miktar,tutar,ilk_alim,son_islem,ortalama_maliyet)")
varliklar_im.execute("CREATE TABLE IF NOT EXISTS islem_gecmisi(islem_id,arac,miktar,tutar)")
varliklar_db.commit()


# Yeni yatırım ekranı

def yeni_yatirim_ek_fun():
    yeni_yatirim_ek = tk.Toplevel(anaekran)
    yeni_yatirim_ek.geometry("1000x1000")
    ekran_ortala(yeni_yatirim_ek, 800, 800)
    yeni_yatirim_ek.title("Yeni Yatırım")

    varlik_adi_l = tk.Label(yeni_yatirim_ek, text="Varlık Adı:")
    varlik_adi_l.place(x=10, y=10)
    secilen_deger = tk.StringVar()
    varlik_adi_combo = ttk.Combobox(yeni_yatirim_ek, textvariable=secilen_deger)
    varlik_adi_combo["values"] = coins
    varlik_adi_combo.place(x=100, y=10)
    varlik_miktar_l = tk.Label(yeni_yatirim_ek, text="Miktar:")
    varlik_miktar_l.place(x=10, y=50)
    varlik_miktar_e = tk.Entry(yeni_yatirim_ek)
    varlik_miktar_e.place(x=100, y=50)
    varlik_alis_fiyat_l = tk.Label(yeni_yatirim_ek, text="Alış Fiyatı:")
    varlik_alis_fiyat_l.place(x=10, y=90)
    varlik_alis_fiyat_e = tk.Entry(yeni_yatirim_ek)
    varlik_alis_fiyat_e.place(x=100, y=90)

    # Yeni yatırım kaydetme fonksiyonu
    def varlik_kaydet_f():
        im = varliklar_db.cursor()
        im.execute("SELECT * FROM varliklarim")
        varliklar_anlik = im.fetchall()
        sahip_varlik_adlari_l = []
        for i in varliklar_anlik:
            sahip_varlik_adlari_l.append(i[0])
        if sahip_varlik_adlari_l.count(varlik_adi_combo.get()) == 0:
            varlik_list = (varlik_adi_combo.get(), varlik_miktar_e.get(),
                           str(int(varlik_alis_fiyat_e.get()) * int(varlik_miktar_e.get())), varlik_alis_fiyat_e.get(),
                           bugun, varlik_alis_fiyat_e.get())
            print(varlik_list)
            varliklar_im.execute("""INSERT INTO varliklarim VALUES (?,?,?,?,?,?)""", varlik_list)
        else:
            im.execute(f"""SELECT * FROM varliklarim WHERE varlik_ad="{varlik_adi_combo.get()}" """)
            v_l = im.fetchall()
            print("vl", v_l)
            varliklar_im.execute(
                f"""UPDATE varliklarim SET miktar={str(int(v_l[0][1]) + int(varlik_miktar_e.get()))} WHERE varlik_ad="{varlik_adi_combo.get()}" """)
            varliklar_im.execute(
                f"""UPDATE varliklarim SET tutar={str((int(v_l[0][1]) + int(varlik_miktar_e.get())) * int(varlik_alis_fiyat_e.get()))} WHERE varlik_ad="{varlik_adi_combo.get()}" """)
            varliklar_im.execute(
                f"""UPDATE varliklarim SET son_islem="{bugun}" WHERE varlik_ad="{varlik_adi_combo.get()}" """)
            ortalama_v = ((int(v_l[0][2])) + (int(varlik_alis_fiyat_e.get()) * int(varlik_miktar_e.get()))) / (
                        int(v_l[0][1]) + int(varlik_miktar_e.get()))
            varliklar_im.execute(
                f"""UPDATE varliklarim SET ortalama_maliyet={str(ortalama_v)} WHERE varlik_ad="{varlik_adi_combo.get()}" """)

        varliklar_db.commit()
        yeni_yatirim_ek.destroy()
        tk.messagebox.showinfo(title="Kaydedildi", message="Varlık alım işleminiz başarı ile kaydedildi")

    varlik_kaydet_b = tk.Button(yeni_yatirim_ek, text="Kaydet", command=varlik_kaydet_f)
    varlik_kaydet_b.place(x=80, y=150)


# Portföy Listem Ekranı
def portfoy_liste_fun():
    portfoy_listem_ek = tk.Toplevel(anaekran)
    ekran_ortala(portfoy_listem_ek, 1250 , 850)
    portfoy_listem_ek.title("Portföy Listesi")
    kripto_portfoy_liste = ttk.Treeview(portfoy_listem_ek, columns=(
    "varlik_ad", "miktar", "tutar", "ilk_alim", "son_islem", "ortalama_maliyet"), show="headings", height=35)
    kripto_portfoy_liste.heading("varlik_ad", text="Varlik Adı", anchor="center")
    kripto_portfoy_liste.heading("miktar", text="Miktar", anchor="center")
    kripto_portfoy_liste.heading("tutar", text="Tutar", anchor="center")
    kripto_portfoy_liste.heading("ilk_alim", text="İlk Alım", anchor="center")
    kripto_portfoy_liste.heading("son_islem", text="Son İşlem", anchor="center")
    kripto_portfoy_liste.heading("ortalama_maliyet", text="Ortalama Maliyet", anchor="center")

    kripto_portfoy_liste.place(x=10, y=10)
    im = varliklar_db.cursor()
    im.execute("""SELECT * FROM varliklarim """)
    v_l_1 = im.fetchall()
    for i in v_l_1:
        kripto_portfoy_liste.insert("", END, values=i)


# Ana Ekrandaki Butonlar
portfoylerim_button = tk.Button(anaekran, text="Portföy Listem", width=15, height=1, command=portfoy_liste_fun)
portfoylerim_button.place(x=10, y=10)
y_yatirim_button = tk.Button(anaekran, text="Yeni Yatırım", width=15, height=1, command=yeni_yatirim_ek_fun)
y_yatirim_button.place(x=10, y=50)


gedik_b_r = ImageTk.PhotoImage(Image.open("gedik.png"))

gedik_l = tk.Label(anaekran,image=gedik_b_r)
gedik_l.place(x=700, y=50)

ogrenci_l=tk.Label(anaekran,text="Serkan Arslan tarafından Gedik Üniversitesi\nYapay Zeka Mühendisliği Yüksek Lisans Programı\nPython Dersi Vizesi için Kodlanmıştır.\n Prof.Dr.Halit Hami Öz'e motive edici desteği için teşekkür ederim.")
ogrenci_l.place(x=650,y=300)
anaekran.mainloop()
