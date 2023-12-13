import pandas as pd


class Gemi:
    Instances: dict = {}

    def __init__(self, gemi_adi, kapasite, gidecek_ulke):
        self.info = {
            "gemi_adi": gemi_adi,
            "kapasite": kapasite,
            "gidecek_ülke": gidecek_ulke
        }
        self.sira = gemi_adi
        self.guncel_kapasite = 0

    def yukle(self, yuk):
        self.guncel_kapasite += yuk

    def gitmeye_hazir_mi(self):
        return self.guncel_kapasite / self.info["kapasite"] >= 0.95

    @staticmethod
    def oku(path):
        df = pd.read_csv(path, encoding="cp1254")
        max_t = 0
        for i in range(len(df)):
            gemi = df.iloc[i]
            instanceGemi = Gemi(
                df.iloc[i]["gemi_adı"],
                df.iloc[i]["kapasite"],
                df.iloc[i]["gidecek_ülke"]
            )
            if Gemi.Instances.get(gemi["geliş_zamanı"]) is None:
                Gemi.Instances[gemi["geliş_zamanı"]] = [instanceGemi]
            else:
                Gemi.Instances[gemi["geliş_zamanı"]].append(instanceGemi)
            max_t = max(max_t, gemi["geliş_zamanı"])
        return max_t


class Tir:
    Instances: dict = {}

    def __init__(self, plaka: str, ulke: str, ton20: int, ton30: int, yuk_miktari: int, maliyet: int):
        self.info = {
            "plaka": plaka,
            "ülke": ulke,
            "20_ton_adet": ton20,
            "30_ton_adet": ton30,
            "yük_miktarı": yuk_miktari,
            "maliyet": maliyet
        }
        self.sira = plaka.split("_")[-1]

    @staticmethod
    def oku(path):
        df = pd.read_csv(path, encoding="cp1254")
        max_t = 0
        for i in range(len(df)):
            tir = df.iloc[i]
            instanceTir = Tir(
                df.iloc[i]["tır_plakası"],
                df.iloc[i]["ülke"],
                df.iloc[i]["20_ton_adet"],
                df.iloc[i]["30_ton_adet"],
                df.iloc[i]["yük_miktarı"],
                df.iloc[i]["maliyet"]
            )
            if Tir.Instances.get(tir["geliş_zamanı"]) is None:
                Tir.Instances[tir["geliş_zamanı"]] = [instanceTir]
            else:
                Tir.Instances[tir["geliş_zamanı"]].append(instanceTir)
            max_t = max(max_t, tir["geliş_zamanı"])
        return max_t


def istif_alani_yuku(istif_alani):
    return sum(map(lambda x: x[0], istif_alani))


if __name__ == "__main__":
    tir_max_t = Tir.oku("olaylar.csv")
    gemi_max_t = Gemi.oku("gemiler.csv")

    gemi_bekleme_alani = []
    tir_bekleme_alani = []
    istif_alani = [[], []]

    for t in range(1, max(tir_max_t, gemi_max_t) + 1):
        print(f"{t} tarihi için işlemler başladı")
        linc_kullanim_sayisi = 0
        # Tirlari beklet
        if Tir.Instances.get(t) is not None:
            for tir in Tir.Instances[t]:
                tir_bekleme_alani.append(tir)
                print(f"\t{t} tarihinde {tir.info['plaka']} plakalı tır bekletme alanına geldi")
            tir_bekleme_alani.sort(key=lambda tir: tir.sira)

        # Gemileri beklet
        if Gemi.Instances.get(t) is not None:
            for gemi in Gemi.Instances[t]:
                gemi_bekleme_alani.append(gemi)
                print(f"\t{t} tarihinde {gemi.info['gemi_adi']} gemisi bekletme alanına geldi")
            gemi_bekleme_alani.sort(key=lambda gemi: gemi.sira)

        # tirlari istif alanina bosalt
        while istif_alani_yuku(istif_alani[0]) < 750 and linc_kullanim_sayisi < 20:
            if len(tir_bekleme_alani) == 0:
                break
            tir = tir_bekleme_alani.pop(0)
            yuk = tir.info["20_ton_adet"] * 20 + tir.info["30_ton_adet"] * 30
            if istif_alani_yuku(istif_alani[0]) + yuk > 750:
                # tiri geri koy
                tir_bekleme_alani = [tir] + tir_bekleme_alani
                break
            else:
                istif_alani[0].append([yuk, tir.info["ülke"]])
                linc_kullanim_sayisi += 1
                print(
                    f"\t{t} tarihinde {tir.info['plaka']} plakalı tır istif alani 1'e {tir.info['ülke']}'ye gidecek kargo yukledi")

        if istif_alani_yuku(istif_alani[0]) == 750 and linc_kullanim_sayisi < 20:
            print(f"\t{t} tarihinde 750 tonluk istif alanı 1 doldu")

        while istif_alani_yuku(istif_alani[1]) < 750:
            if len(tir_bekleme_alani) == 0:
                break
            tir = tir_bekleme_alani.pop(0)
            yuk = tir.info["20_ton_adet"] * 20 + tir.info["30_ton_adet"] * 30
            if istif_alani_yuku(istif_alani[1]) + yuk > 750:
                # tiri geri koy
                tir_bekleme_alani = [tir] + tir_bekleme_alani
                break
            else:
                istif_alani[1].append(yuk)
                linc_kullanim_sayisi += 1
                print(
                    f"\t{t} tarihinde {tir.info['plaka']} plakalı tır istif alani 2'e {tir.info['ülke']}'ye gidecek kargo yukledi")

        if istif_alani_yuku(istif_alani[1]) == 750:
            print(f"\t{t} tarihinde 750 tonluk istif alanı 2 doldu")

        # gemileri istif alanina bosalt
        index = 0
        while istif_alani_yuku(istif_alani[0]) > 0 and index < len(gemi_bekleme_alani) and linc_kullanim_sayisi < 20:
            if len(gemi_bekleme_alani) == 0:
                break
            gemi = gemi_bekleme_alani[index]
            hedef_ulke = gemi.info["gidecek_ülke"]
            kargolar = list(filter(lambda x: x[1] == hedef_ulke, istif_alani[0]))
            for kargo in kargolar:
                gemi.yukle(kargo[0])
                linc_kullanim_sayisi += 1
                istif_alani[0].remove(kargo)
                print(
                    f"\t{t} tarihinde {kargo[0]} tonluk kargo istif alani 1'den gemi {gemi.info['gemi_adi']} yüklendi")
                if gemi.gitmeye_hazir_mi():
                    print(f"\t{t} tarihinde {gemi.info['gemi_adi']} gemisi {hedef_ulke} ülkesine yola çıktı")
                    gemi_bekleme_alani.pop(index)
                    index -= 1
                    break
            index += 1

        if istif_alani_yuku(istif_alani[0]) == 0:
            print(f"\t{t} tarihinde istif alanı 1 boşaldı")

        index = 0
        while istif_alani_yuku(istif_alani[1]) > 0 and index < len(gemi_bekleme_alani) and linc_kullanim_sayisi < 20:
            if len(gemi_bekleme_alani) == 0:
                break
            gemi = gemi_bekleme_alani[index]
            hedef_ulke = gemi.info["gidecek_ülke"]
            kargolar = list(filter(lambda x: x[1] == hedef_ulke, istif_alani[1]))
            for kargo in kargolar:
                gemi.yukle(kargo[0])
                istif_alani[1].remove(kargo)
                linc_kullanim_sayisi += 1
                print(
                    f"\t{t} tarihinde {gemi.info['gemi_adi']} gemisi istif alani 2'den {kargo[0]} tonluk kargo yükledi")
                if gemi.gitmeye_hazir_mi():
                    print(f"\t{t} tarihinde {gemi.info['gemi_adi']} gemisi {hedef_ulke} ülkesine yola çıktı")
                    gemi_bekleme_alani.pop(index)
                    index -= 1
                    break
            index += 1

        if istif_alani_yuku(istif_alani[1]) == 0:
            print(f"\t{t} tarihinde istif alanı 2 boşaldı")

        print(f"{t} tarihi için işlemler bitti")
