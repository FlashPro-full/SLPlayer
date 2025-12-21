from typing import Dict
from config.settings import settings

_LANG: str = settings.get("language", "en")

_STRINGS: Dict[str, Dict[str, str]] = {
    "app.title": {
        "en": "SLPlayer",
        "it": "SLPlayer",
        "pl": "SLPlayer",
    },
    "content.video": {"en": "Video", "it": "Video", "pl": "Wideo"},
    "content.photo": {"en": "Photo", "it": "Foto", "pl": "Zdjęcie"},
    "content.text": {"en": "Text", "it": "Testo", "pl": "Tekst"},
    "content.singleline_text": {"en": "Single Line Text", "it": "Testo su singola riga", "pl": "Tekst jednoliniowy"},
    "content.animation": {"en": "Animation", "it": "Animazione", "pl": "Animacja"},
    "content.clock": {"en": "Clock", "it": "Orologio", "pl": "Zegar"},
    "content.timing": {"en": "Timing", "it": "Timing", "pl": "Czasowanie"},
    "content.weather": {"en": "Weather", "it": "Meteo", "pl": "Pogoda"},
    "content.sensor": {"en": "Sensor", "it": "Sensore", "pl": "Czujnik"},
    "content.html": {"en": "HTML", "it": "HTML", "pl": "HTML"},
    "content.hdmi": {"en": "HDMI", "it": "HDMI", "pl": "HDMI"},
    # Menus
    "menu.file": {"en": "File", "it": "File", "pl": "Plik"},
    "menu.setting": {"en": "Setting", "it": "Impostazioni", "pl": "Ustawienia"},
    "menu.control": {"en": "Control", "it": "Controllo", "pl": "Sterowanie"},
    "menu.language": {"en": "Language", "it": "Lingua", "pl": "Język"},
    "menu.help": {"en": "Help", "it": "Aiuto", "pl": "Pomoc"},
    # File actions
    "action.new": {"en": "🖥 New", "it": "🖥 Nuovo", "pl": "🖥 Nowy"},
    "action.open": {"en": "📂 Open", "it": "📂 Apri", "pl": "📂 Otwórz"},
    "action.save": {"en": "💾 Save", "it": "💾 Salva", "pl": "💾 Zapisz"},
    "action.exit": {"en": "🚪 Exit", "it": "🚪 Esci", "pl": "🚪 Wyjście"},
    # Setting actions
    "action.screen_setting": {"en": "🖥 Screen Setting", "it": "🖥 Impostazioni Schermo", "pl": "🖥 Ustawienia ekranu"},
    "action.sync_setting": {"en": "🔄 Sync Setting", "it": "🔄 Impostazioni Sync", "pl": "🔄 Ustawienia synchronizacji"},
    "action.license": {"en": "🔐 License", "it": "🔐 Licenza", "pl": "🔐 Licencja"},
    # Control actions
    "action.device_info": {"en": "🧾 Controller Information", "it": "🧾 Informazioni Controller", "pl": "🧾 Informacje o kontrolerze"},
    "action.clear_program": {"en": "🧹 Clear program", "it": "🧹 Pulisci programma", "pl": "🧹 Wyczyść program"},
    "action.send": {"en": "⬆️ Send", "it": "⬆️ Invia", "pl": "⬆️ Wyślij"},
    # Help actions
    "action.about": {"en": "About", "it": "Informazioni", "pl": "O programie"},
    # Toolbar groups
    "toolbar.program": {"en": "Program", "it": "Programma", "pl": "Program"},
    "toolbar.visible_content": {"en": "Visible Content", "it": "Contenuti Visibili", "pl": "Widoczna zawartość"},
    "toolbar.control": {"en": "Control", "it": "Controllo", "pl": "Sterowanie"},
    "toolbar.playback": {"en": "Playback", "it": "Riproduzione", "pl": "Odtwarzanie"},
    "toolbar.send": {"en": "Send program to controller via network", "it": "Invia programma al controller via rete", "pl": "Wyślij program do kontrolera przez sieć"},
    "toolbar.insert": {"en": "Insert U-Disk into controller (after export)", "it": "Inserisci U-Disk nel controller (dopo esportazione)", "pl": "Wstaw U-Disk do kontrolera (po eksporcie)"},
    "toolbar.clear": {"en": "Clear program", "it": "Wyczyść program", "pl": "Wyczyść program"},
    "toolbar.clear_tooltip": {"en": "Clear Program", "it": "Pulisci Programma", "pl": "Wyczyść Program"},
    "message.no_controller_connected": {"en": "No controller connected. Please connect to a controller first.", "it": "Nessun controller connesso. Connetti prima un controller.", "pl": "Brak połączenia z kontrolerem. Najpierw połącz się z kontrolerem."},
    "message.no_program_selected": {"en": "No program selected. Please select or create a program first.", "it": "Nessun programma selezionato. Seleziona o crea prima un programma.", "pl": "Nie wybrano programu. Najpierw wybierz lub utwórz program."},
    "message.program_sent_success": {"en": "Program '{name}' sent successfully to controller.", "it": "Programma '{name}' inviato con successo al controller.", "pl": "Program '{name}' został pomyślnie wysłany do kontrolera."},
    "message.program_send_failed": {"en": "Failed to send program to controller.", "it": "Invio del programma al controller fallito.", "pl": "Nie udało się wysłać programu do kontrolera."},
    "message.program_send_error": {"en": "Error sending program: {error}", "it": "Errore durante l'invio del programma: {error}", "pl": "Błąd podczas wysyłania programu: {error}"},
    "message.confirm_clear_program": {"en": "Are you sure you want to clear program '{name}'?", "it": "Sei sicuro di voler cancellare il programma '{name}'?", "pl": "Czy na pewno chcesz wyczyścić program '{name}'?"},
    # Short labels for toolbar button texts
    "label.program": {"en": "Program", "it": "Programma", "pl": "Program"},
    "label.send": {"en": "Send", "it": "Invia", "pl": "Wyślij"},
    "label.insert": {"en": "Insert", "it": "Inserisci", "pl": "Wstaw"},
    "label.clear": {"en": "Clear", "it": "Pulisci", "pl": "Wyczyść"},
    "label.first": {"en": "First", "it": "Pierwszy", "pl": "Pierwszy"},
    "label.prev": {"en": "Previous", "it": "Poprzedni", "pl": "Poprzedni"},
    "label.next": {"en": "Next", "it": "Następny", "pl": "Następny"},
    "label.last": {"en": "Last", "it": "Ostatni", "pl": "Ostatni"},
    "label.play": {"en": "Play", "it": "Odtwórz", "pl": "Odtwórz"},
    "label.pause": {"en": "Pause", "it": "Wstrzymaj", "pl": "Wstrzymaj"},
    "label.stop": {"en": "Stop", "it": "Zatrzymaj", "pl": "Zatrzymaj"},
    "toolbar.nav_first": {"en": "Go to first program", "it": "Idź do pierwszego", "pl": "Idź do pierwszego"},
    "toolbar.nav_prev": {"en": "Previous program", "it": "Poprzedni program", "pl": "Poprzedni program"},
    "toolbar.nav_next": {"en": "Next program", "it": "Następny program", "pl": "Następny program"},
    "toolbar.nav_last": {"en": "Go to last program", "it": "Idź do ostatniego", "pl": "Idź do ostatniego"},
    "toolbar.play": {"en": "Play program", "it": "Odtwórz", "pl": "Odtwórz"},
    "toolbar.pause": {"en": "Pause playback", "it": "Wstrzymaj", "pl": "Wstrzymaj"},
    "toolbar.stop": {"en": "Stop playback", "it": "Zatrzymaj", "pl": "Zatrzymaj"},
    # Program list panel
    "program_list.new": {"en": "New", "it": "Nuovo", "pl": "Nowy"},
    "program_list.duplicate": {"en": "Duplicate", "it": "Duplica", "pl": "Duplikuj"},
    "program_list.move_up": {"en": "Move Up", "it": "Przenieś w górę", "pl": "Przenieś w górę"},
    "program_list.move_down": {"en": "Move Down", "it": "Przenieś w dół", "pl": "Przenieś w dół"},
    "program_list.delete": {"en": "Delete", "it": "Elimina", "pl": "Usuń"},
    # Properties panel
    "prop.program_properties": {"en": "Program properties", "it": "Proprietà programma", "pl": "Właściwości programu"},
    "prop.frame": {"en": "Frame", "it": "Rama", "pl": "Ramka"},
    "prop.background_music": {"en": "Background Music", "it": "Musica di sottofondo", "pl": "Muzyka w tle"},
    "prop.select_file": {"en": "Select File...", "it": "Seleziona file...", "pl": "Wybierz plik..."},
    "prop.play_mode": {"en": "Play mode", "it": "Modalità di riproduzione", "pl": "Tryb odtwarzania"},
    "prop.play_times": {"en": "Play times", "it": "Czas odtwarzania", "pl": "Liczba odtworzeń"},
    "prop.fixed_length": {"en": "Fixed length", "it": "Długość stała", "pl": "Stała długość"},
    "prop.play_control": {"en": "Play control", "it": "Sterowanie odtwarzaniem", "pl": "Sterowanie odtwarzaniem"},
    "prop.specified_time": {"en": "specified time", "it": "określony czas", "pl": "określony czas"},
    "prop.specify_week": {"en": "Specify the week", "it": "Wybierz dni tygodnia", "pl": "Wybierz dni tygodnia"},
    "prop.specify_date": {"en": "Specify the date", "it": "Wybierz datę", "pl": "Wybierz datę"},
    "prop.select_date": {"en": "Select Date...", "it": "Seleziona data...", "pl": "Wybierz datę..."},
    "prop.select_date_title": {"en": "Select Date", "it": "Seleziona data", "pl": "Wybierz datę"},
    "weekday.mon": {"en": "Monday", "it": "Lunedì", "pl": "Poniedziałek"},
    "weekday.tue": {"en": "Tuesday", "it": "Martedì", "pl": "Wtorek"},
    "weekday.wed": {"en": "Wednesday", "it": "Mercoledì", "pl": "Środa"},
    "weekday.thu": {"en": "Thursday", "it": "Giovedì", "pl": "Czwartek"},
    "weekday.fri": {"en": "Friday", "it": "Venerdì", "pl": "Piątek"},
    "weekday.sat": {"en": "Saturday", "it": "Sabato", "pl": "Sobota"},
    "weekday.sun": {"en": "Sunday", "it": "Domenica", "pl": "Niedziela"},
    # Screen settings dialog
    "screen.device_list": {"en": "Device list", "it": "Elenco dispositivi", "pl": "Lista urządzeń"},
    "screen.use_device_setting": {"en": "Use Device Setting", "it": "Usa impostazioni dispositivo", "pl": "Użyj ustawień urządzenia"},
    "screen.device_type": {"en": "Device Type", "it": "Tipo dispositivo", "pl": "Typ urządzenia"},
    "screen.rotate": {"en": "Rotate", "it": "Obróć", "pl": "Obrót"},
    "screen.suggested_range": {"en": "Suggested range", "it": "Intervallo suggerito", "pl": "Sugerowany zakres"},
    "screen.max_width": {"en": "Maximum width", "it": "Larghezza massima", "pl": "Maksymalna szerokość"},
    "screen.max_height": {"en": "Maximum height", "it": "Altezza massima", "pl": "Maksymalna wysokość"},
    "screen.storage_capacity": {"en": "Storage capacity", "it": "Capacità di archiviazione", "pl": "Pojemność pamięci"},
    "screen.gray_scale": {"en": "Gray scale", "it": "Skala szarości", "pl": "Skala szarości"},
    "screen.comm_interface": {"en": "Communication Interface", "it": "Interfaccia di comunicazione", "pl": "Interfejs komunikacyjny"},
    "screen.other": {"en": "Other", "it": "Altro", "pl": "Inne"},
    "screen.controller_list": {"en": "Controller list", "it": "Elenco controller", "pl": "Lista kontrolerów"},
    "screen.use_controller_setting": {"en": "Use Controller Setting", "it": "Usa impostazioni controller", "pl": "Użyj ustawień kontrolera"},
    "screen.width": {"en": "Width", "it": "Larghezza", "pl": "Szerokość"},
    "screen.height": {"en": "Height", "it": "Altezza", "pl": "Wysokość"},
    # Status bar
    "status.no_device": {"en": "No Device Detected", "it": "Nessun dispositivo rilevato", "pl": "Nie wykryto urządzenia"},
    "status.connecting": {"en": "Connecting...", "it": "Connessione...", "pl": "Łączenie..."},
    "status.connected": {"en": "Device Connected", "it": "Dispositivo connesso", "pl": "Urządzenie połączone"},
    "status.connection_error": {"en": "Connection Error", "it": "Errore di connessione", "pl": "Błąd połączenia"},
    "status.program": {"en": "Program", "it": "Programma", "pl": "Program"},
    # Menu actions
    "action.discover": {"en": "🔍 Discover Controllers", "it": "🔍 Scopri controller", "pl": "🔍 Odkryj kontrolery"},
    "action.dashboard": {"en": "📊 Dashboard", "it": "📊 Dashboard", "pl": "📊 Panel"},
    "action.time_power": {"en": "⏰ Time / Power / Brightness", "it": "⏰ Ora / Alimentazione / Luminosità", "pl": "⏰ Czas / Zasilanie / Jasność"},
    "action.network_config": {"en": "🌐 Network Configuration", "it": "🌐 Configurazione di rete", "pl": "🌐 Konfiguracja sieci"},
    "action.diagnostics": {"en": "🔧 Diagnostics & Logs", "it": "🔧 Diagnostica e log", "pl": "🔧 Diagnostyka i logi"},
    "action.import_controller": {"en": "📥 Import from Controller", "it": "📥 Importa dal controller", "pl": "📥 Importuj z kontrolera"},
    "action.export": {"en": "📤 Export / Publish", "it": "📤 Esporta / Pubblica", "pl": "📤 Eksportuj / Publikuj"},
    "action.open_program": {"en": "Open Program", "it": "Apri programma", "pl": "Otwórz program"},
    "action.program_files": {"en": "Program Files (*.soo);;All Files (*)", "it": "File programma (*.soo);;Tutti i file (*)", "pl": "Pliki programu (*.soo);;Wszystkie pliki (*)"},
    # Screen settings
    "screen.title": {"en": "Screen Parameters Setting", "it": "Impostazioni parametri schermo", "pl": "Ustawienia parametrów ekranu"},
    "screen.controller_name": {"en": "Controller Name", "it": "Nome controller", "pl": "Nazwa kontrolera"},
    "screen.controller_type": {"en": "Controller type", "it": "Tipo controller", "pl": "Typ kontrolera"},
    "screen.width_tooltip": {"en": "Screen width (pixels)", "it": "Larghezza schermo (pixel)", "pl": "Szerokość ekranu (piksele)"},
    "screen.height_tooltip": {"en": "Screen height (pixels)", "it": "Altezza schermo (pixel)", "pl": "Wysokość ekranu (piksele)"},
    "screen.rotate_tooltip": {"en": "Rotate output orientation", "it": "Ruota orientamento output", "pl": "Obróć orientację wyjścia"},
    "screen.rotate_combo_tooltip": {"en": "Rotation in degrees", "it": "Rotazione in gradi", "pl": "Obrót w stopniach"},
    "screen.controller_tooltip": {"en": "Choose a connected controller from the local database", "it": "Scegli un controller connesso dal database locale", "pl": "Wybierz podłączony kontroler z lokalnej bazy danych"},
    "screen.controller_list_tooltip": {"en": "Controllers previously connected and stored locally", "it": "Controller precedentemente connessi e memorizzati localmente", "pl": "Kontrolery wcześniej podłączone i przechowywane lokalnie"},
    "screen.use_controller_tooltip": {"en": "When enabled, parameters are derived from the selected controller", "it": "Quando abilitato, i parametri sono derivati dal controller selezionato", "pl": "Gdy włączone, parametry są pobierane z wybranego kontrolera"},
    "screen.series_tooltip": {"en": "Controller brand / series", "it": "Marca / serie controller", "pl": "Marka / seria kontrolera"},
    "screen.model_tooltip": {"en": "Controller model", "it": "Modello controller", "pl": "Model kontrolera"},
    # Program list
    "program_list.select_all_tooltip": {"en": "Select/Deselect active program or all programs in active screen", "it": "Seleziona/Deseleziona programma attivo o tutti i programmi nello schermo attivo", "pl": "Zaznacz/odznacz aktywny program lub wszystkie programy na aktywnym ekranie"},
    "program_list.copy": {"en": "Copy", "it": "Copia", "pl": "Kopiuj"},
    "program_list.paste": {"en": "Paste", "it": "Incolla", "pl": "Wklej"},
    "program_list.rename": {"en": "📝 Rename", "it": "📝 Rinomina", "pl": "📝 Zmień nazwę"},
    "program_list.delete": {"en": "❌ Delete", "it": "❌ Elimina", "pl": "❌ Usuń"},
    "program_list.new_screen": {"en": "🖥 New Screen", "it": "🖥 Nuovo schermo", "pl": "🖥 Nowy ekran"},
    "program_list.add_program": {"en": "💽 Add program", "it": "💽 Aggiungi programma", "pl": "💽 Dodaj program"},
    "program_list.insert": {"en": "📲 Insert", "it": "📲 Inserisci", "pl": "📲 Wstaw"},
    "program_list.download": {"en": "⬇️ Download", "it": "⬇️ Scarica", "pl": "⬇️ Pobierz"},
    "program_list.close": {"en": "✖️ Close", "it": "✖️ Chiudi", "pl": "✖️ Zamknij"},
    "program_list.add_video": {"en": "🎞 Add Video", "it": "🎞 Aggiungi video", "pl": "🎞 Dodaj wideo"},
    "program_list.add_photo": {"en": "🌄 Add Photo", "it": "🌄 Aggiungi foto", "pl": "🌄 Dodaj zdjęcie"},
    "program_list.add_text": {"en": "🔠 Add Text", "it": "🔠 Aggiungi testo", "pl": "🔠 Dodaj tekst"},
    "program_list.add_singleline": {"en": "🔤 Add SingleLineText", "it": "🔤 Aggiungi testo su singola riga", "pl": "🔤 Dodaj tekst jednoliniowy"},
    "program_list.add_animation": {"en": "🎇 Add Animation", "it": "🎇 Aggiungi animazione", "pl": "🎇 Dodaj animację"},
    "program_list.add_clock": {"en": "🕓 Add Clock", "it": "🕓 Aggiungi orologio", "pl": "🕓 Dodaj zegar"},
    "program_list.add_timing": {"en": "⌛️ Add Timing", "it": "⌛️ Aggiungi timing", "pl": "⌛️ Dodaj czasowanie"},
    "program_list.add_weather": {"en": "🌦 Add Weather", "it": "🌦 Aggiungi meteo", "pl": "🌦 Dodaj pogodę"},
    "program_list.add_sensor": {"en": "📎 Add Sensor", "it": "📎 Aggiungi sensore", "pl": "📎 Dodaj czujnik"},
    "program_list.add_html": {"en": "🌐 Add HTML", "it": "🌐 Aggiungi HTML", "pl": "🌐 Dodaj HTML"},
    "program_list.add_hdmi": {"en": "🔌 Add HDMI", "it": "🔌 Aggiungi HDMI", "pl": "🔌 Dodaj HDMI"},
    # Toolbar
    "toolbar.program_tooltip": {"en": "Program", "it": "Programma", "pl": "Program"},
    "toolbar.play_tooltip": {"en": "Play", "it": "Riproduci", "pl": "Odtwórz"},
    "toolbar.pause_tooltip": {"en": "Pause", "it": "Pausa", "pl": "Wstrzymaj"},
    "toolbar.stop_tooltip": {"en": "Stop", "it": "Ferma", "pl": "Zatrzymaj"},
    "toolbar.insert_tooltip": {"en": "Insert", "it": "Inserisci", "pl": "Wstaw"},
    "toolbar.clear_tooltip": {"en": "Clear", "it": "Pulisci", "pl": "Wyczyść"},
    # Network setup
    "network.welcome": {"en": "Welcome to SLPlayer", "it": "Benvenuto in SLPlayer", "pl": "Witamy w SLPlayer"},
    "network.title": {"en": "Network Setup - First Launch", "it": "Configurazione di rete - Primo avvio", "pl": "Konfiguracja sieci - Pierwsze uruchomienie"},
}


def set_language(lang: str) -> None:
    global _LANG
    _LANG = lang


def get_language() -> str:
    return _LANG


def tr(key: str) -> str:
    lang = _LANG
    entry = _STRINGS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))
