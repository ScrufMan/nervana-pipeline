import os
import unittest

from file_processor import File
from lingua import Language


class TestFileProcessor(unittest.TestCase):
    def test_object_creates_full_path(self):
        cwd = os.getcwd()
        full_path = os.path.join(cwd, "sample_files", "sample.pdf")

        file = File(full_path)

        self.assertIsNotNone(file)
        self.assertEqual(file.path, full_path)

    def test_object_creates_relative_path(self):
        relative_path = "sample_files/sample.pdf"

        file = File(relative_path)

        self.assertIsNotNone(file)
        self.assertEqual(file.path, relative_path)

    def test_file_data_valid(self):
        file = File("sample_files/sample.pdf")

        self.assertEqual(file.filename, "sample")
        self.assertEqual(file.extension, "pdf")

    def test_plaintext_extraction_without_filter_pdf(self):
        file = File("sample_files/sample.pdf")

        expected_value = """
































 A Simple PDF File 
 This is a small demonstration .pdf file - 

 just for use in the Virtual Mechanics tutorials. More text. And more 
 text. And more text. And more text. And more text. 

 And more text. And more text. And more text. And more text. And more 
 text. And more text. Boring, zzzzz. And more text. And more text. And 
 more text. And more text. And more text. And more text. And more text. 
 And more text. And more text. 

 And more text. And more text. And more text. And more text. And more 
 text. And more text. And more text. Even more. Continued on page 2 ...



 Simple PDF File 2 
 ...continued from page 1. Yet more text. And more text. And more text. 
 And more text. And more text. And more text. And more text. And more 
 text. Oh, how boring typing this stuff. But not as boring as watching 
 paint dry. And more text. And more text. And more text. And more text. 
 Boring.  More, a little more text. The end, and just as well. 


"""

        file.extract_plaintext(do_filter=False)

        self.assertEqual(file.plaintext, expected_value)

    def test_plaintext_extraction_with_filter_pdf(self):
        file = File("sample_files/sample.pdf")

        expected_value = """A Simple PDF File 
 This is a small demonstration .pdf file - 

 just for use in the Virtual Mechanics tutorials. More text. And more 
 text. And more text. And more text. And more text. 

 And more text. And more text. And more text. And more text. And more 
 text. And more text. Boring, zzzzz. And more text. And more text. And 
 more text. And more text. And more text. And more text. And more text. 
 And more text. And more text. 

 And more text. And more text. And more text. And more text. And more 
 text. And more text. And more text. Even more. Continued on page 2 ...
 Simple PDF File 2 
 ...continued from page 1. Yet more text. And more text. And more text. 
 And more text. And more text. And more text. And more text. And more 
 text. Oh, how boring typing this stuff. But not as boring as watching 
 paint dry. And more text. And more text. And more text. And more text. 
 Boring.  More, a little more text. The end, and just as well."""

        file.extract_plaintext()  # filter implicitly on

        self.assertEqual(file.plaintext, expected_value)

    def test_plaintext_extraction_without_filter_pptx(self):
        file = File("sample_files/sample.pptx")

        expected_value = """














































Využitie grafovej databázy NEO4j



Využitie grafovej databázy NEO4j
PV177
Team 1













12/21/2022
Annual Review
‹#›

1





	indexácia
dotaz/odpoveď

(HTTP)
(HTTP)
preprocessing
Metacloud
klient






12/21/2022
Annual Review
‹#›
Python v úlohe log4j?



12/21/2022
Annual Review
‹#›

Ad-hoc riešenie, ktoré funguje


Podpora regulárnych výrazov


Schopnosť rýchlo parsovať rôzne formáty vstupu


A ďalej ich upravovať 


HTTP klient






12/21/2022
Annual Review
‹#›
Uzly
hashované heslá a heslá v plaintexte
emaily
Vzťahy
našli sme to v nejakom súbore
k emailu sa viaže heslo/hash
Čo sme ukladali



12/21/2022
Annual Review
‹#›
Asi najznámejšia “grafovka”
Server ale aj desktopový klient
Jazyk cypher
HTTP backend







12/21/2022
Annual Review
‹#›









12/21/2022
Annual Review
‹#›
Vypísať heslá pre daný email
Pridať k hashu plaintext
Vypísať hashe pre daný email


Nájsť všetky dvojice (mail, heslo/hash) zo súboru
Klient



12/21/2022
Annual Review
‹#›

Demo






12/21/2022
Annual Review
‹#›
"""

        file.extract_plaintext(do_filter=False)

        self.assertEqual(file.plaintext, expected_value)

    def test_plaintext_extraction_with_filter_pptx(self):
        file = File("sample_files/sample.pptx")

        expected_value = """Využitie grafovej databázy NEO4j
Využitie grafovej databázy NEO4j
PV177
Team 1
1
	indexácia
dotaz/odpoveď

(HTTP)
(HTTP)
preprocessing
Metacloud
klient
Python v úlohe log4j?
Ad-hoc riešenie, ktoré funguje
Podpora regulárnych výrazov
Schopnosť rýchlo parsovať rôzne formáty vstupu
A ďalej ich upravovať 
HTTP klient
Uzly
hashované heslá a heslá v plaintexte
emaily
Vzťahy
našli sme to v nejakom súbore
k emailu sa viaže heslo/hash
Čo sme ukladali
Asi najznámejšia “grafovka”
Server ale aj desktopový klient
Jazyk cypher
HTTP backend
Vypísať heslá pre daný email
Pridať k hashu plaintext
Vypísať hashe pre daný email
Nájsť všetky dvojice (mail, heslo/hash) zo súboru
Klient
Demo"""

        file.extract_plaintext()  # filter implicitly on

        self.assertEqual(file.plaintext, expected_value)

    def test_plaintext_extraction_without_filter_docx(self):
        file = File("sample_files/sample.docx")

        expected_value = """
























































Oznámení podle § 16 odst. 8 zákona č. 21/1992 Sb., o bankách
o předpokládaném převodu části obchodního závodu MOPET CZ a.s. na společnost Česká spořitelna, a.s.

Informace o transakci a zúčastněných společnostech
Společnost MOPET CZ a.s., se sídlem Budějovická 1912/64b, 140 00 Praha 4, IČ 247 59 023 („MOPET“) jako prodávající a společnost Česká spořitelna, a.s., se sídlem Praha 4, Olbrachtova 1929/62, PSČ 140 00, IČ 45244782 („Česká spořitelna“) jako kupující uzavřely dne 8.11.2021 Smlouvu o koupi obchodního závodu MOPET. Česká spořitelna tak k 15.12.2021 nabude vlastnické právo k části obchodního závodu MOPET. 
V rámci transakce bude do České spořitelny převedena veškerá evidence bývalých účtů elektronických peněz klientů, včetně kompletní dokumentace a povinností s těmito účty spojenými. Česká spořitelna bude nadále tuto evidenci u sebe spravovat. 
Česká národní banka s převodem části obchodního závodu udělila předchozí souhlas. 

Informace o plnění pravidel obezřetného podnikání 
Vybrané údaje o plnění pravidel obezřetného podnikání Českou spořitelnou jsou dostupné na: 
https://www.csas.cz/cs/dokumenty-ke-stazeni#/7/Povinne-informace-v-souladu-s-Vyhlaskou-CNB

Vybrané údaje o plnění pravidel obezřetného podnikání společnosti MOPET jsou dostupné na: 
https://www.mopetcz.cz/

Informace o vlivu postupu na smluvní vztahy s klienty MOPET a s klienty České spořitelny
Vzhledem k tomu, že společnost MOPET ukončila smluvní vztahy se všemi svými klienty, nedochází v rámci převodu části obchodního závodu k žádnému převodu smluvních vztahů s klienty na Českou spořitelnu. Česká spořitelna přebírá veškerou evidenci a dokumentaci spojenou s bývalými účty elektronických peněz. Bývalí klienti MOPETu tak budou mít možnost se ve věcech týkajících se účtů elektronických peněz obracet na Českou spořitelnu.
Na stávající klienty České spořitelny nebude mít výše uvedený postup žádný dopad.
V případě jakýchkoli dotazů se prosím obracejte:
na MOPET: email: info@mopetcz.cz, telefon: +420 731 633 487, korespondenční adresa: MOPET CZ a.s., Budějovická 1912/64b, 140 00 Praha 4
na Českou spořitelnu: email: csas@csas.cz, telefon: +420 800 468 378, korespondenční adresa: Česká spořitelna, a.s., Olbrachtova 1929/62, 140 00 Praha 4 

Informace o orgánu dohledu 
Po uskutečnění převodu části obchodního závodu MOPET do České spořitelny bude příslušným orgánem dohledu Česká národní banka.
Toto oznámení je činěno podle § 16 odst. 8 zákona o bankách. Oznámení bylo v souladu s § 16 odst. 10 zákona o bankách zasláno České národní bance a byly splněny podmínky tohoto ustanovení pro jeho uveřejnění.
"""

        file.extract_plaintext(do_filter=False)

        self.assertEqual(file.plaintext, expected_value)

    def test_plaintext_extraction_witho_filter_docx(self):
        file = File("sample_files/sample.docx")

        expected_value = """Oznámení podle § 16 odst. 8 zákona č. 21/1992 Sb., o bankách
o předpokládaném převodu části obchodního závodu MOPET CZ a.s. na společnost Česká spořitelna, a.s.

Informace o transakci a zúčastněných společnostech
Společnost MOPET CZ a.s., se sídlem Budějovická 1912/64b, 140 00 Praha 4, IČ 247 59 023 („MOPET“) jako prodávající a společnost Česká spořitelna, a.s., se sídlem Praha 4, Olbrachtova 1929/62, PSČ 140 00, IČ 45244782 („Česká spořitelna“) jako kupující uzavřely dne 8.11.2021 Smlouvu o koupi obchodního závodu MOPET. Česká spořitelna tak k 15.12.2021 nabude vlastnické právo k části obchodního závodu MOPET. 
V rámci transakce bude do České spořitelny převedena veškerá evidence bývalých účtů elektronických peněz klientů, včetně kompletní dokumentace a povinností s těmito účty spojenými. Česká spořitelna bude nadále tuto evidenci u sebe spravovat. 
Česká národní banka s převodem části obchodního závodu udělila předchozí souhlas. 

Informace o plnění pravidel obezřetného podnikání 
Vybrané údaje o plnění pravidel obezřetného podnikání Českou spořitelnou jsou dostupné na: 
https://www.csas.cz/cs/dokumenty-ke-stazeni#/7/Povinne-informace-v-souladu-s-Vyhlaskou-CNB

Vybrané údaje o plnění pravidel obezřetného podnikání společnosti MOPET jsou dostupné na: 
https://www.mopetcz.cz/

Informace o vlivu postupu na smluvní vztahy s klienty MOPET a s klienty České spořitelny
Vzhledem k tomu, že společnost MOPET ukončila smluvní vztahy se všemi svými klienty, nedochází v rámci převodu části obchodního závodu k žádnému převodu smluvních vztahů s klienty na Českou spořitelnu. Česká spořitelna přebírá veškerou evidenci a dokumentaci spojenou s bývalými účty elektronických peněz. Bývalí klienti MOPETu tak budou mít možnost se ve věcech týkajících se účtů elektronických peněz obracet na Českou spořitelnu.
Na stávající klienty České spořitelny nebude mít výše uvedený postup žádný dopad.
V případě jakýchkoli dotazů se prosím obracejte:
na MOPET: email: info@mopetcz.cz, telefon: +420 731 633 487, korespondenční adresa: MOPET CZ a.s., Budějovická 1912/64b, 140 00 Praha 4
na Českou spořitelnu: email: csas@csas.cz, telefon: +420 800 468 378, korespondenční adresa: Česká spořitelna, a.s., Olbrachtova 1929/62, 140 00 Praha 4 

Informace o orgánu dohledu 
Po uskutečnění převodu části obchodního závodu MOPET do České spořitelny bude příslušným orgánem dohledu Česká národní banka.
Toto oznámení je činěno podle § 16 odst. 8 zákona o bankách. Oznámení bylo v souladu s § 16 odst. 10 zákona o bankách zasláno České národní bance a byly splněny podmínky tohoto ustanovení pro jeho uveřejnění."""

        file.extract_plaintext()  # filter implicitly on

        self.assertEqual(file.plaintext, expected_value)

    def test_language_detection_english(self):
        file = File("sample_files/sample.pdf")

        file.extract_plaintext()
        file.detect_language()

        self.assertEqual(file.lang, Language.ENGLISH)
