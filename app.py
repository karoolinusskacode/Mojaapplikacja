from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
# NOWE IMPORTY:
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bardzo_tajny_i_trudny_kod_123'
# 2. KONFIGURACJA BAZY DANYCH
# Mówimy: "Stwórz plik o nazwie 'uzytkownicy.db' i tam trzymaj dane"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'uzytkownicy.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Uruchamiamy bazę w naszej aplikacji
db = SQLAlchemy(app)
# KONFIGURACJA SYSTEMU LOGOWANIA
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'strona_logowania' # Gdzie przekierować nie-zalogowanych?
# 4. MODEL DANYCH (To jest projekt naszej tabeli w Excelu)
# Każda klasa to Tabela, każda zmienna to Kolumna
class Osoba(db.Model):
    id = db.Column(db.Integer, primary_key=True)      # Unikalny numer (1, 2, 3...)
    imie = db.Column(db.String(100), nullable=False)  # Imię (tekst)
    plec = db.Column(db.String(20), nullable=False)   # Płeć (tekst)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f'<Osoba {self.imie}>'
# Tabela dla Użytkowników (Administratorów)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False) # Login
    password = db.Column(db.String(150), nullable=False) # Zahaszowane hasło

# Funkcja ładująca użytkownika (niezbędna dla Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# 5. TWORZENIE BAZY (Tylko przy starcie)
with app.app_context():
    db.create_all()  # To polecenie fizycznie utworzy plik .db jeśli go nie ma
# --- TRASA: REJESTRACJA ---
@app.route('/rejestracja', methods=['GET', 'POST'])
def rejestracja():
    # Jeśli użytkownik wysłał formularz (kliknął Zarejestruj)
    if request.method == 'POST':
        login = request.form['login']
        haslo = request.form['haslo']

        # 1. BEZPIECZEŃSTWO: Haszowanie hasła
        # Nigdy nie zapisujemy hasła wprost! Zamieniamy je na ciąg znaków.
        # Np. "tajne123" -> "pbkdf2:sha256:260000$..."
        zahaszowane_haslo = generate_password_hash(haslo, method='pbkdf2:sha256')

        # 2. Tworzymy nowego użytkownika
        nowy_user = User(username=login, password=zahaszowane_haslo)

        try:
            db.session.add(nowy_user)
            db.session.commit()
            return redirect('/logowanie') # Po sukcesie idziemy do logowania
        except:
            return "Błąd! Taki użytkownik już istnieje lub coś poszło nie tak."

    # Jeśli to tylko wejście na stronę (GET)
    return render_template('rejestracja.html')
# --- TRASA: LOGOWANIE ---
@app.route('/logowanie', methods=['GET', 'POST'])
def strona_logowania():
    # Jeśli przesłano formularz
    if request.method == 'POST':
        login = request.form['login']
        haslo = request.form['haslo']

        # 1. Szukamy użytkownika w bazie po loginie
        # .first() zwraca pierwszego znalezionego lub None (jeśli nie ma)
        user = User.query.filter_by(username=login).first()

        # 2. Sprawdzamy dwa warunki:
        # - Czy użytkownik istnieje?
        # - Czy hasło pasuje do hasha? (check_password_hash)
        if user and check_password_hash(user.password, haslo):
            # SUKCES: Logujemy użytkownika w systemie
            login_user(user)
            return redirect('/baza') # Przenosimy do panelu
        else:
            return "Błędny login lub hasło!"

    # Jeśli wejście na stronę (GET)
    return render_template('logowanie.html')

# --- TRASA: WYLOGOWANIE ---
@app.route('/wyloguj')
@login_required # Tylko zalogowany może się wylogować
def wyloguj():
    logout_user()
    return redirect('/logowanie')
# --- TRASY (To już znasz) ---

@app.route('/')
def strona_glowna():
    return render_template('formularz.html')

@app.route('/powitanie', methods=['POST'])
@login_required
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
    nowa_osoba = Osoba(imie=ladne_imie, plec=plec_wynik, user_id=current_user.id)
    
    db.session.add(nowa_osoba)
    db.session.commit()

    
    return render_template('wynik.html', 
                           imie_html=ladne_imie, 
                           zwrot_html=zwrot, 
                           plec_html=plec_wynik)
# --- NOWA TRASA: PANEL ADMINISTRATORA (READ) ---
# --- TRASA: PANEL ADMINISTRATORA ---
@app.route('/baza')
@login_required
def pokaz_baze():
    # DEBUGOWANIE: Wypisz w terminalu, kto pyta
    print(f"--- Logowanie do bazy ---")
    print(f"Kto pyta? {current_user.username} (ID: {current_user.id})")

    # Logika filtrująca
    moje_wpisy = Osoba.query.filter_by(user_id=current_user.id).all()
    
    # DEBUGOWANIE: Wypisz ile znaleziono
    print(f"Ile wpisów znaleziono? {len(moje_wpisy)}")

    return render_template('lista.html', ludzie=moje_wpisy, uzytkownik=current_user)
@app.route('/edytuj/<int:id>', methods=['GET', 'POST'])
@login_required
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
@login_required
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