import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy  # 1. Importujemy narzędzie do bazy

app = Flask(__name__)

# 2. KONFIGURACJA BAZY DANYCH
# Mówimy: "Stwórz plik o nazwie 'uzytkownicy.db' i tam trzymaj dane"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'uzytkownicy.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Uruchamiamy bazę w naszej aplikacji
db = SQLAlchemy(app)

# 4. MODEL DANYCH (To jest projekt naszej tabeli w Excelu)
# Każda klasa to Tabela, każda zmienna to Kolumna
class Osoba(db.Model):
    id = db.Column(db.Integer, primary_key=True)      # Unikalny numer (1, 2, 3...)
    imie = db.Column(db.String(100), nullable=False)  # Imię (tekst)
    plec = db.Column(db.String(20), nullable=False)   # Płeć (tekst)

    def __repr__(self):
        return f'<Osoba {self.imie}>'

# 5. TWORZENIE BAZY (Tylko przy starcie)
with app.app_context():
    db.create_all()  # To polecenie fizycznie utworzy plik .db jeśli go nie ma

# --- TRASY (To już znasz) ---

@app.route('/')
def strona_glowna():
    return render_template('formularz.html')

@app.route('/powitanie', methods=['POST'])
def przetworz_dane():
    imie = request.form['imie']
    
    # Logika (ta sama co wcześniej)
    if imie.endswith('a'):
        zwrot = "Dzień dobry, Pani"
        plec_wynik = "Kobieta"
    else:
        zwrot = "Witam Pana"
        plec_wynik = "Mężczyzna"
    
    ladne_imie = imie.capitalize()
    
    # 6. ZAPISYWANIE DO BAZY (To jest nowość!)
    # Tworzymy nowy "wiersz" do naszej tabeli
    nowa_osoba = Osoba(imie=ladne_imie, plec=plec_wynik)
    
    # Dodajemy do "poczekalni"
    db.session.add(nowa_osoba)
    # Zatwierdzamy (jak przycisk "Save") - dopiero teraz dane lądują w pliku
    db.session.commit()
    
    return render_template('wynik.html', 
                           imie_html=ladne_imie, 
                           zwrot_html=zwrot, 
                           plec_html=plec_wynik)
# --- NOWA TRASA: PANEL ADMINISTRATORA (READ) ---
@app.route('/baza')
def pokaz_baze():
    # 1. Magiczne polecenie: "Pobierz WSZYSTKICH z tabeli Osoba"
    wszyscy_ludzie = Osoba.query.all()
    
    # 2. Wyświetl plik lista.html i przekaż mu tę listę
    return render_template('lista.html', ludzie=wszyscy_ludzie)
# --- TRASA: EDYCJA (UPDATE) ---
@app.route('/edytuj/<int:id>', methods=['GET', 'POST'])
def edytuj_osobe(id):
    # 1. Szukamy osoby
    osoba_do_edycji = Osoba.query.get_or_404(id)

    # 2. Jeśli przesłano formularz (POST) -> Zapisujemy zmiany
    if request.method == 'POST':
        # Pobieramy nowe imię z formularza
        nowe_imie = request.form['nowe_imie']
        
        # Aktualizujemy imię (i robimy ładne duże litery)
        osoba_do_edycji.imie = nowe_imie.capitalize()
        
        # WAŻNE: Musimy zaktualizować też płeć, bo imię mogło się zmienić!
        if osoba_do_edycji.imie.endswith('a'):
            osoba_do_edycji.plec = "Kobieta"
        else:
            osoba_do_edycji.plec = "Mężczyzna"
            
        # Zapisujemy zmiany w bazie
        db.session.commit()
        
        return redirect('/baza')

    # 3. Jeśli to tylko wejście na stronę (GET) -> Pokazujemy formularz
    return render_template('edycja.html', osoba=osoba_do_edycji)
# --- TRASA: USUWANIE (DELETE) ---
@app.route('/usun/<int:id>')
def usun_osobe(id):
    # 1. Szukamy osoby w bazie po numerze ID. 
    # Jeśli nie znajdzie, zwróci błąd 404 (get_or_404)
    osoba_do_usuniecia = Osoba.query.get_or_404(id)

    try:
        # 2. Usuwamy tę osobę
        db.session.delete(osoba_do_usuniecia)
        # 3. Zatwierdzamy zmianę w pliku
        db.session.commit()
        # 4. Wracamy (przekierowujemy) na stronę z tabelą
        return redirect('/baza')

    except:
        return "Wystąpił problem podczas usuwania."
if __name__ == '__main__':
    app.run(debug=True)