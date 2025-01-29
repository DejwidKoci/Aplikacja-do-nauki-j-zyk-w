# Aplikacja do nauki języków

# Opis
Aplikacja, w której użytkownicy mogą dodawać słówka w obcym języku i uczyć się ich.

# Jak uruchomić?
Należy uruchomić aplikację `app.py`. Wymagane pakiety są zawarte w `requirements.txt`.  W terminalu pojawi się link, który należy uruchomić.
Zostaniemy przekierowani do strony gdzie należy utworzyć konto. W przypadku wprowadzenia niewłaściwego loginu lub hasła wyświetli się komunikat o nieprawidłowych danych. 
W przypadku pierwszego logowania zostaniemy poproszeni o dodaniu języka, którego będziemy się uczyć. Następnie pojawi się opcja dodania kolejnego języka albo kontynuacji. 
W przypadku wciśnięcia przycisku kontynuacji zostaniemy przeniesiemy do dashboardu.


# Dashboard
W dashboardzie mamy:
- wszelkie komunikaty dotyczące działań użytkownika (np. udane logowanie)
- informację o wybranym języku do nauki (Current Language)
- możliwość dodania nowego słowa (Add New Word)
- możliwość quizu ze słówek (Start a Word Test)
- możliwość zmiany języka (Change Language)
- możliwość wylogowania się (Logout)


W przypadku uruchomienia testu w momencie, kiedy do wybranego języka nie ma żadnych wcześniej utworzonych słów wyświetli się komunikat "You don't have any words to test in the selected language".
W przypadku uruchomienia testu w momencie, kiedy zostały słówka dodane do wybranego języka. Mamy następujący układ:
- słówko do przetłumaczenia
- pole do wpisania słowa
- odsetek wszystkich słówek, na które udzielono poprawną odpowiedź
- progres bar
- w przypadku udzielenia poprawnej odpowiedzi wyświetla się komunikat "correct"
- w przypadku udzielenia złej odpowiedzi wyświetla się komunikat o błędzie z właściwym tłumaczeniem słowa

Po ukończeniu testu dostaniemy informacje o jego zakończeniu, będzie również wtedy możliwość powrotu do dashboardu i wylogowaniu. 

