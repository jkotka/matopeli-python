import sys
import csv
import random as rnd
import datetime as dtm
from pathlib import Path

import pygame as pg

X = 800
Y = 600
RUUTU = pg.display.set_mode((X, Y))
BLOKKI = 20
HAKEMISTO = Path(__file__).parent.absolute()
FONTTI = Path(HAKEMISTO, "tiedostot/fontti/Schoolbell-Regular.ttf")
KUVAKE = pg.image.load(Path(HAKEMISTO, "tiedostot/kuvake.png"))


def teksti(teksti: str, koko: int, väri: str, x: int, y: int):
    """Piirretään teksti - keskitetään jos x tai y on -1"""
    teksti = pg.font.Font(FONTTI, koko).render(teksti, True, väri)
    if x == -1:
        x = X//2 - teksti.get_rect().centerx
    if y == -1:
        y = Y//2 - teksti.get_rect().centery
    RUUTU.blit(teksti, [x, y])


def efekti(tiedosto: str, volume: float):
    """Toistetaan ääniefekti"""
    tiedosto = Path(HAKEMISTO, "tiedostot/efektit", tiedosto)
    efekti = pg.mixer.Sound(tiedosto)
    efekti.set_volume(volume)
    efekti.play()


class Mato:
    def __init__(self):
        self.png = pg.image.load(Path(HAKEMISTO, "tiedostot/mato.png")).convert_alpha()
        self.pää = [X//2, Y//2]
        self.osat = [self.pää]
        self.suunta = [0, 0]
        self.muuta_suunta = self.suunta
        self.pituus = 1
        self.laskuri = 0
        self.viive = 100

    def piirrä(self):
        """Piirretään madon osat"""
        for osa in self.osat:
            RUUTU.blit(self.png, (osa[0], osa[1]))

    def liikuta(self, looppi_ms: int):
        """Liikutetaan matoa (sama nopeus riippumatta fps:stä)"""
        self.laskuri += looppi_ms
        while self.laskuri >= self.viive:
            self.laskuri -= self.viive

            # Toistetaan liikkumisefekti vain jos liikutaan
            if self.suunta != [0, 0]:
                efekti("mato.mp3", 0.15)

            # Estetään täyskäännös
            if (self.muuta_suunta[0] + self.suunta[0] != 0 or
                    self.muuta_suunta[1] + self.suunta[1] != 0):
                self.suunta = self.muuta_suunta

            # Liikutetaan matoa
            self.pää[0] += self.suunta[0]
            self.pää[1] += self.suunta[1]
            self.osat.insert(0, [self.pää[0], self.pää[1]])
            if len(self.osat) > self.pituus:
                del self.osat[-1]

    def reunaosuma(self):
        """Tarkistetaan onko törmätty reunaan"""
        if (self.pää[0] < 0 or self.pää[0] >= X
                or self.pää[1] < 0 or self.pää[1] >= Y):
            efekti("gameover1.mp3", 0.5)
            return True

    def häntäosuma(self):
        """Tarkistetaan onko törmätty omaan häntään"""
        for osa in self.osat[1:]:
            if self.pää == osa:
                efekti("gameover2.mp3", 0.2)
                return True


class Omena:
    def __init__(self):
        self.png = pg.image.load(Path(HAKEMISTO, "tiedostot/omena.png")).convert_alpha()
        self.sijainti = self.arvo_sijainti()

    def arvo_sijainti(self):
        """Arvotaan omenalle sijainti"""
        self.sijainti = [
            rnd.randrange(1, (X//BLOKKI))*BLOKKI,
            rnd.randrange(1, (Y//BLOKKI))*BLOKKI
        ]
        return self.sijainti

    def piirrä(self):
        """Piirretään omena"""
        RUUTU.blit(self.png, (self.sijainti[0], self.sijainti[1]))


class Peli:
    def __init__(self):
        self.clock = pg.time.Clock()
        self.fps = 60
        self.pistelista = Path(HAKEMISTO, "tiedostot/pistelista.csv")
        self.pistelista_otsikko = ["Nimikirjaimet", "Pisteet", "Aikaleima"]
        self.päävalikko()

    def päävalikko(self):
        """Näytetään pelin päävalikko"""
        lopeta = False
        valinnat = {
            "pelaa": pg.K_SPACE,
            "pistelista": pg.K_p,
            "lopeta": pg.K_ESCAPE
        }
        while not lopeta:
            RUUTU.fill("black")
            pg.display.set_caption("Matopeli")
            teksti("MATOPELI", 80, "green", -1, 160)
            teksti("Pelaa (SPACE)", 45, "white", -1, 255)
            teksti("Pistelista (P)", 45, "white", -1, 305)
            teksti("Lopeta (ESC)", 45, "red", -1, 355)

            # Näppäinkontrollit
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key in valinnat.values():
                        efekti("nappi.mp3", 0.7)
                    if event.key == valinnat["pelaa"]:
                        self.pelaa()
                    if event.key == valinnat["pistelista"]:
                        self.pistelista_näytä(None)
                    if event.key == valinnat["lopeta"]:
                        lopeta = True
                if event.type == pg.QUIT:
                    lopeta = True

            pg.display.flip()
            self.clock.tick(self.fps)
        pg.quit()
        sys.exit()

    def pelaa(self):
        """Pelilooppi"""
        mato = Mato()
        omena = Omena()
        looppi_ms = 0
        pause = False
        lopeta = False
        suunnat = {
            "ylös": pg.K_UP,
            "alas": pg.K_DOWN,
            "vasen": pg.K_LEFT,
            "oikea": pg.K_RIGHT
        }
        while not lopeta:
            RUUTU.fill("black")

            # Näppäinkontrollit
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key in suunnat.values():
                        efekti("mato.mp3", 0.6)
                    if event.key == suunnat["ylös"]:
                        mato.muuta_suunta = [0, -BLOKKI]
                    if event.key == suunnat["alas"]:
                        mato.muuta_suunta = [0, BLOKKI]
                    if event.key == suunnat["vasen"]:
                        mato.muuta_suunta = [-BLOKKI, 0]
                    if event.key == suunnat["oikea"]:
                        mato.muuta_suunta = [BLOKKI, 0]
                    if event.key == pg.K_SPACE:
                        efekti("nappi.mp3", 0.7)
                        pause = True
                if event.type == pg.QUIT:
                    lopeta = True

            mato.liikuta(looppi_ms)

            # Piirretään omena vasta kun mato liikkuu, muuten näytetään ohje
            if mato.suunta != [0, 0]:
                omena.piirrä()
            else:
                teksti("ALOITA VALITSEMALLA SUUNTA", 45, "green", -1, 10)
                teksti("(Suunta = Nuolinäppäimet)", 45, "white", -1, 60)
                teksti("(Pause = Space)", 45, "white", -1, 110)
                pause = False

            mato.piirrä()

            # Jos mato syö omenan
            if mato.pää == omena.sijainti:
                efekti("omena.mp3", 0.3)
                omena.arvo_sijainti()
                mato.pituus += 1
                mato.viive -= 1

            # Törmäystarkistus
            if mato.reunaosuma() or mato.häntäosuma():
                self.game_over(mato.pituus - 1)

            # Päivitetään pisteet, näyttö ja loopin nopeus
            pg.display.set_caption(f"Matopeli ~ Pisteet: {mato.pituus - 1}")
            pg.display.flip()
            looppi_ms = self.clock.tick(self.fps)

            # Pause
            while pause:
                pg.display.set_caption("Matopeli ~ Jatka peliä (SPACE)")
                teksti("||", 45, "white", 20, 10)

                # Näppäinkontrollit
                for event in pg.event.get():
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            efekti("nappi.mp3", 0.7)
                            pause = False
                    if event.type == pg.QUIT:
                        pause = False
                        lopeta = True
                        
                pg.display.flip()
                self.clock.tick(self.fps)
        pg.quit()
        sys.exit()

    def game_over(self, pisteet: int):
        "Game over - tarkistetaan päästäänkö pistelistalle"""
        pg.time.wait(500)
        RUUTU.fill("black")
        pg.display.set_caption("Matopeli ~ Game over!")
        teksti("GAME OVER!", 80, "red", -1, 210)
        teksti(f"Pisteet: {pisteet}", 45, "white", -1, 305)
        pg.display.flip()
        pg.time.wait(2000)

        # Tarkistetaan pisteet
        if pisteet > 0:
            try:
                with open(self.pistelista, "r") as tiedosto:
                    lista = list(csv.reader(tiedosto, delimiter=","))[1:]
                    for rivi in lista:
                        if pisteet > int(rivi[1]) or len(lista) < 10:
                            self.pistelista_tallenna(pisteet)
            except FileNotFoundError:
                self.pistelista_tallenna(pisteet)

        self.päävalikko()

    def pistelista_tallenna(self, pisteet: int):
        """Tallennetaan tulos pistelistalle"""
        efekti("pistelista.mp3", 0.3)
        lopeta = False
        nimikirjaimet = ""
        merkit = 3
        aikaleima = dtm.datetime.now()
        while not lopeta:
            RUUTU.fill("black")
            pg.display.set_caption("Matopeli ~ Anna nimikirjaimesi")

            # Kysytään nimikirjaimet
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.unicode.isalpha() or event.unicode == ".":
                        efekti("nappi.mp3", 0.7)
                        nimikirjaimet += event.unicode
                    if event.key == pg.K_BACKSPACE:
                        nimikirjaimet = nimikirjaimet[:-1]
                if event.type == pg.QUIT:
                    lopeta = True

            # Tallennetaan listaan
            if len(nimikirjaimet) == merkit:
                with open(self.pistelista, "a") as tiedosto:
                    lista = csv.writer(tiedosto, delimiter=",")
                    if not tiedosto.tell():
                        lista.writerow(self.pistelista_otsikko)
                    lista.writerow([nimikirjaimet.upper(), pisteet, aikaleima])
                self.pistelista_järjestä()
                self.pistelista_näytä(aikaleima)

            teksti("PÄÄSIT LISTALLE!", 80, "green", -1, 180)
            teksti(f"Nimikirjaimesi ({merkit - len(nimikirjaimet)} jäljellä):", 45, "white", -1, 275)
            teksti(f"> {nimikirjaimet.upper()}", 45, "white", 335, 325)
            pg.display.flip()
            self.clock.tick(self.fps)
        pg.quit()
        sys.exit()

    def pistelista_järjestä(self):
        """Järjestetään pistelista - 10 parasta tulosta"""
        try:
            with open(self.pistelista, "r") as tiedosto:
                lista = list(csv.reader(tiedosto, delimiter=","))[1:]
                top10 = sorted(lista, key=lambda p: int(p[1]), reverse=True)[:10]
            with open(self.pistelista, "w") as tiedosto:
                lista = csv.writer(tiedosto, delimiter=",")
                lista.writerow(self.pistelista_otsikko)
                lista.writerows(top10)
        except FileNotFoundError:
            print(f"Tiedostoa '{self.pistelista}' ei löytynyt.")

    def pistelista_näytä(self, aikaleima: dtm.datetime):
        """Näytetään pistelista"""
        lopeta = False
        while not lopeta:
            RUUTU.fill("black")
            pg.display.set_caption("Matopeli ~ Pistelista")
            teksti("PISTELISTA", 80, "green", -1, -10)

            # Näppäinkontrollit
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        efekti("nappi.mp3", 0.7)
                        self.päävalikko()
                if event.type == pg.QUIT:
                    lopeta = True

            # Luetaan lista - korostetaan tulos pelin jälkeen
            try:
                with open(self.pistelista, "r") as tiedosto:
                    lista = list(csv.reader(tiedosto, delimiter=","))[1:]
                    y = 85
                    for rivi in lista:
                        if rivi[2] == str(aikaleima):
                            väri = "green"
                        else:
                            väri = "white"
                        sija = lista.index(rivi) + 1
                        rivi = f"{sija}. {rivi[0]} {rivi[1]}"
                        teksti(rivi, 40, väri, 325, y)
                        y += 45
            except FileNotFoundError:
                teksti("Lista on tyhjä!", 45, "white", -1, -1)

            teksti("Valikko (ESC)", 45, "red", -1, 540)
            pg.display.flip()
            self.clock.tick(self.fps)
        pg.quit()
        sys.exit()


pg.init()
pg.display.set_icon(KUVAKE)

Peli()