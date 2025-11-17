"""
Simple i18n helper.
"""
from typing import Dict
from config.settings import settings

_LANG: str = settings.get("language", "en")

_STRINGS: Dict[str, Dict[str, str]] = {
    "app.title": {
        "en": "SLPlayer",
        "it": "SLPlayer",
        "zh": "SLPlayer",
        "pl": "SLPlayer",
    },
    # Content types (tooltips)
    "content.custom_area": {"en": "Custom Area", "it": "Area personalizzata", "zh": "自定义区域", "pl": "Obszar niestandardowy"},
    "content.video": {"en": "Video", "it": "Video", "zh": "视频", "pl": "Wideo"},
    "content.photo": {"en": "Photo", "it": "Foto", "zh": "照片", "pl": "Zdjęcie"},
    "content.text": {"en": "Text", "it": "Testo", "zh": "文本", "pl": "Tekst"},
    "content.single_line_text": {"en": "Single Line Text", "it": "Testo su singola riga", "zh": "单行文本", "pl": "Tekst jednoliniowy"},
    "content.animation": {"en": "Animation", "it": "Animazione", "zh": "动画", "pl": "Animacja"},
    "content.text3d": {"en": "3D Text", "it": "Testo 3D", "zh": "3D 文字", "pl": "Tekst 3D"},
    "content.clock": {"en": "Clock", "it": "Orologio", "zh": "时钟", "pl": "Zegar"},
    "content.calendar": {"en": "Calendar", "it": "Calendario", "zh": "日历", "pl": "Kalendarz"},
    "content.timing": {"en": "Timing", "it": "Timing", "zh": "定时", "pl": "Czasowanie"},
    "content.weather": {"en": "Weather", "it": "Meteo", "zh": "天气", "pl": "Pogoda"},
    "content.sensor": {"en": "Sensor", "it": "Sensore", "zh": "传感器", "pl": "Czujnik"},
    "content.neon": {"en": "Neon", "it": "Neon", "zh": "霓虹", "pl": "Neon"},
    "content.wps": {"en": "WPS", "it": "WPS", "zh": "WPS", "pl": "WPS"},
    "content.table": {"en": "Table", "it": "Tabella", "zh": "表格", "pl": "Tabela"},
    "content.office": {"en": "Office", "it": "Office", "zh": "Office", "pl": "Office"},
    "content.digital_watch": {"en": "Digital Watch", "it": "Orologio digitale", "zh": "数字时钟", "pl": "Zegar cyfrowy"},
    "content.html": {"en": "HTML", "it": "HTML", "zh": "HTML", "pl": "HTML"},
    "content.live_stream": {"en": "Live Stream", "it": "Live", "zh": "直播", "pl": "Transmisja na żywo"},
    "content.qr_code": {"en": "QR Code", "it": "QR Code", "zh": "二维码", "pl": "Kod QR"},
    "content.hdmi": {"en": "HDMI", "it": "HDMI", "zh": "HDMI", "pl": "HDMI"},
    # Menus
    "menu.file": {"en": "File", "it": "File", "zh": "文件", "pl": "Plik"},
    "menu.setting": {"en": "Setting", "it": "Impostazioni", "zh": "设置", "pl": "Ustawienia"},
    "menu.control": {"en": "Control", "it": "Controllo", "zh": "控制", "pl": "Sterowanie"},
    "menu.language": {"en": "Language", "it": "Lingua", "zh": "语言", "pl": "Język"},
    "menu.help": {"en": "Help", "it": "Aiuto", "zh": "帮助", "pl": "Pomoc"},
    # File actions
    "action.new": {"en": "🖥 New", "it": "🖥 Nuovo", "zh": "🖥 新建", "pl": "🖥 Nowy"},
    "action.open": {"en": "📂 Open", "it": "📂 Apri", "zh": "📂 打开", "pl": "📂 Otwórz"},
    "action.save": {"en": "💾 Save", "it": "💾 Salva", "zh": "💾 保存", "pl": "💾 Zapisz"},
    "action.exit": {"en": "🚪 Exit", "it": "🚪 Esci", "zh": "🚪 退出", "pl": "🚪 Wyjście"},
    # Setting actions
    "action.screen_setting": {"en": "🖥 Screen Setting", "it": "🖥 Impostazioni Schermo", "zh": "🖥 屏幕设置", "pl": "🖥 Ustawienia ekranu"},
    "action.sync_setting": {"en": "🔄 Sync Setting", "it": "🔄 Impostazioni Sync", "zh": "🔄 同步设置", "pl": "🔄 Ustawienia synchronizacji"},
    # Control actions
    "action.device_info": {"en": "🧾 Controller Information", "it": "🧾 Informazioni Controller", "zh": "🧾 控制器信息", "pl": "🧾 Informacje o kontrolerze"},
    "action.clear_program": {"en": "🧹 Clear program", "it": "🧹 Pulisci programma", "zh": "🧹 清空节目", "pl": "🧹 Wyczyść program"},
    "action.upload": {"en": "⬆️ Upload", "it": "⬆️ Carica", "zh": "⬆️ 上传", "pl": "⬆️ Wyślij"},
    "action.download": {"en": "⬇️ Download", "it": "⬇️ Scarica", "zh": "⬇️ 下载", "pl": "⬇️ Pobierz"},
    # Help actions
    "action.about": {"en": "About", "it": "Informazioni", "zh": "关于", "pl": "O programie"},
    # Toolbar groups
    "toolbar.program": {"en": "Program", "it": "Programma", "zh": "节目", "pl": "Program"},
    "toolbar.visible_content": {"en": "Visible Content", "it": "Contenuti Visibili", "zh": "可见内容", "pl": "Widoczna zawartość"},
    "toolbar.control": {"en": "Control", "it": "Controllo", "zh": "控制", "pl": "Sterowanie"},
    "toolbar.playback": {"en": "Playback", "it": "Riproduzione", "zh": "回放", "pl": "Odtwarzanie"},
    "toolbar.download": {"en": "Download program to controller", "it": "Scarica programma al controller", "zh": "下载节目到控制器", "pl": "Pobierz program do kontrolera"},
    "toolbar.usb": {"en": "Download to USB disk", "it": "Scarica su disco USB", "zh": "下载到U盘", "pl": "Pobierz na dysk USB"},
    "toolbar.insert": {"en": "Insert program", "it": "Wstaw program", "zh": "插入节目", "pl": "Wstaw program"},
    "toolbar.clear": {"en": "Clear program", "it": "Wyczyść program", "zh": "清空节目", "pl": "Wyczyść program"},
    # Short labels for toolbar button texts
    "label.program": {"en": "Program", "it": "Programma", "zh": "节目", "pl": "Program"},
    "label.download": {"en": "Download", "it": "Scarica", "zh": "下载", "pl": "Pobierz"},
    "label.usb": {"en": "To U-disk", "it": "Su U-disk", "zh": "到U盘", "pl": "Na U-disk"},
    "label.insert": {"en": "Insert", "it": "Inserisci", "zh": "插入", "pl": "Wstaw"},
    "label.clear": {"en": "Clear", "it": "Pulisci", "zh": "清空", "pl": "Wyczyść"},
    "label.first": {"en": "First", "it": "Pierwszy", "zh": "第一个", "pl": "Pierwszy"},
    "label.prev": {"en": "Previous", "it": "Poprzedni", "zh": "上一个", "pl": "Poprzedni"},
    "label.next": {"en": "Next", "it": "Następny", "zh": "下一个", "pl": "Następny"},
    "label.last": {"en": "Last", "it": "Ostatni", "zh": "最后一个", "pl": "Ostatni"},
    "label.play": {"en": "Play", "it": "Odtwórz", "zh": "播放", "pl": "Odtwórz"},
    "label.pause": {"en": "Pause", "it": "Wstrzymaj", "zh": "暂停", "pl": "Wstrzymaj"},
    "label.stop": {"en": "Stop", "it": "Zatrzymaj", "zh": "停止", "pl": "Zatrzymaj"},
    "toolbar.nav_first": {"en": "Go to first program", "it": "Idź do pierwszego", "zh": "跳到第一个", "pl": "Idź do pierwszego"},
    "toolbar.nav_prev": {"en": "Previous program", "it": "Poprzedni program", "zh": "上一个", "pl": "Poprzedni program"},
    "toolbar.nav_next": {"en": "Next program", "it": "Następny program", "zh": "下一个", "pl": "Następny program"},
    "toolbar.nav_last": {"en": "Go to last program", "it": "Idź do ostatniego", "zh": "跳到最后一个", "pl": "Idź do ostatniego"},
    "toolbar.play": {"en": "Play program", "it": "Odtwórz", "zh": "播放", "pl": "Odtwórz"},
    "toolbar.pause": {"en": "Pause playback", "it": "Wstrzymaj", "zh": "暂停", "pl": "Wstrzymaj"},
    "toolbar.stop": {"en": "Stop playback", "it": "Zatrzymaj", "zh": "停止", "pl": "Zatrzymaj"},
    # Program list panel
    "program_list.new": {"en": "New", "it": "Nuovo", "zh": "新建", "pl": "Nowy"},
    "program_list.duplicate": {"en": "Duplicate", "it": "Duplica", "zh": "复制", "pl": "Duplikuj"},
    "program_list.move_up": {"en": "Move Up", "it": "Przenieś w górę", "zh": "上移", "pl": "Przenieś w górę"},
    "program_list.move_down": {"en": "Move Down", "it": "Przenieś w dół", "zh": "下移", "pl": "Przenieś w dół"},
    "program_list.delete": {"en": "Delete", "it": "Elimina", "zh": "删除", "pl": "Usuń"},
    # Properties panel
    "prop.program_properties": {"en": "Program properties", "it": "Proprietà programma", "zh": "节目属性", "pl": "Właściwości programu"},
    "prop.frame": {"en": "Frame", "it": "Rama", "zh": "边框", "pl": "Ramka"},
    "prop.background_music": {"en": "Background Music", "it": "Musica di sottofondo", "zh": "背景音乐", "pl": "Muzyka w tle"},
    "prop.select_file": {"en": "Select File...", "it": "Seleziona file...", "zh": "选择文件...", "pl": "Wybierz plik..."},
    "prop.play_mode": {"en": "Play mode", "it": "Modalità di riproduzione", "zh": "播放模式", "pl": "Tryb odtwarzania"},
    "prop.play_times": {"en": "Play times", "it": "Czas odtwarzania", "zh": "播放次数", "pl": "Liczba odtworzeń"},
    "prop.fixed_length": {"en": "Fixed length", "it": "Długość stała", "zh": "固定时长", "pl": "Stała długość"},
    "prop.play_control": {"en": "Play control", "it": "Sterowanie odtwarzaniem", "zh": "播放控制", "pl": "Sterowanie odtwarzaniem"},
    "prop.specified_time": {"en": "specified time", "it": "określony czas", "zh": "指定时间", "pl": "określony czas"},
    "prop.specify_week": {"en": "Specify the week", "it": "Wybierz dni tygodnia", "zh": "指定星期", "pl": "Wybierz dni tygodnia"},
    "prop.specify_date": {"en": "Specify the date", "it": "Wybierz datę", "zh": "指定日期", "pl": "Wybierz datę"},
    "prop.select_date": {"en": "Select Date...", "it": "Seleziona data...", "zh": "选择日期...", "pl": "Wybierz datę..."},
    "prop.select_date_title": {"en": "Select Date", "it": "Seleziona data", "zh": "选择日期", "pl": "Wybierz datę"},
    "weekday.mon": {"en": "Monday", "it": "Lunedì", "zh": "星期一", "pl": "Poniedziałek"},
    "weekday.tue": {"en": "Tuesday", "it": "Martedì", "zh": "星期二", "pl": "Wtorek"},
    "weekday.wed": {"en": "Wednesday", "it": "Mercoledì", "zh": "星期三", "pl": "Środa"},
    "weekday.thu": {"en": "Thursday", "it": "Giovedì", "zh": "星期四", "pl": "Czwartek"},
    "weekday.fri": {"en": "Friday", "it": "Venerdì", "zh": "星期五", "pl": "Piątek"},
    "weekday.sat": {"en": "Saturday", "it": "Sabato", "zh": "星期六", "pl": "Sobota"},
    "weekday.sun": {"en": "Sunday", "it": "Domenica", "zh": "星期日", "pl": "Niedziela"},
    # Screen settings dialog
    "screen.device_list": {"en": "Device list", "it": "Elenco dispositivi", "zh": "设备列表", "pl": "Lista urządzeń"},
    "screen.use_device_setting": {"en": "Use Device Setting", "it": "Usa impostazioni dispositivo", "zh": "使用设备设置", "pl": "Użyj ustawień urządzenia"},
    "screen.device_type": {"en": "Device Type", "it": "Tipo dispositivo", "zh": "设备类型", "pl": "Typ urządzenia"},
    "screen.rotate": {"en": "Rotate", "it": "Obróć", "zh": "旋转", "pl": "Obrót"},
    "screen.suggested_range": {"en": "Suggested range", "it": "Intervallo suggerito", "zh": "建议范围", "pl": "Sugerowany zakres"},
    "screen.max_width": {"en": "Maximum width", "it": "Larghezza massima", "zh": "最大宽度", "pl": "Maksymalna szerokość"},
    "screen.max_height": {"en": "Maximum height", "it": "Altezza massima", "zh": "最大高度", "pl": "Maksymalna wysokość"},
    "screen.storage_capacity": {"en": "Storage capacity", "it": "Capacità di archiviazione", "zh": "存储容量", "pl": "Pojemność pamięci"},
    "screen.gray_scale": {"en": "Gray scale", "it": "Skala szarości", "zh": "灰度", "pl": "Skala szarości"},
    "screen.comm_interface": {"en": "Communication Interface", "it": "Interfaccia di comunicazione", "zh": "通信接口", "pl": "Interfejs komunikacyjny"},
    "screen.other": {"en": "Other", "it": "Altro", "zh": "其他", "pl": "Inne"},
    "screen.controller_list": {"en": "Controller list", "it": "Elenco controller", "zh": "控制器列表", "pl": "Lista kontrolerów"},
    "screen.use_controller_setting": {"en": "Use Controller Setting", "it": "Usa impostazioni controller", "zh": "使用控制器设置", "pl": "Użyj ustawień kontrolera"},
    "screen.device_type": {"en": "Controller list", "it": "Lista controller", "zh": "控制器列表", "pl": "Lista kontrolerów"},
    "screen.width": {"en": "Width", "it": "Larghezza", "zh": "宽度", "pl": "Szerokość"},
    "screen.height": {"en": "Height", "it": "Altezza", "zh": "高度", "pl": "Wysokość"},
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


