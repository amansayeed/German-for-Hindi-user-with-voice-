# Fix a2.html: remove Pronunciation column, order German | English | Hindi
from pathlib import Path
from bs4 import BeautifulSoup

path = Path(__file__).resolve().parent.parent / "source" / "a2" / "a2.html"
soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

for table in soup.find_all("table"):
    thead = table.find("thead")
    if thead:
        ths = thead.find_all("th")
        for th in ths:
            if "Pronunciation" in (th.get_text() or ""):
                th.decompose()
                break
        ths = thead.find_all("th")
        if len(ths) == 4 and "Hindi" in (ths[2].get_text() or "") and "English" in (ths[3].get_text() or ""):
            ths[2].insert_before(ths[3])  # order: #, German, English, Hindi
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 5:
            # #, German, Pronunciation, Hindi, English -> keep #, German, English, Hindi
            pron_td = tr.find("td", class_=lambda c: c and "pronunciation" in c)
            if pron_td:
                pron_td.decompose()
            tds = tr.find_all("td")
            if len(tds) == 4:  # #, German, Hindi, English -> swap to #, German, English, Hindi
                hindi_td, english_td = tds[2], tds[3]
                hindi_td.insert_before(english_td)

path.write_text(str(soup), encoding="utf-8")
print("Updated a2.html: removed Pronunciation, order German | English | Hindi")
