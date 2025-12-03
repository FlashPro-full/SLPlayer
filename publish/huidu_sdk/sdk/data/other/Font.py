class Font:
    def __init__(self, *args):
        # Set default values
        self.name = ""
        self.size = 14
        self.underline = False
        self.bold = False
        self.italic = False
        self.color = "#ff0000"

        # Handle different argument patterns
        if len(args) == 1:
            if isinstance(args[0], Font):
                # Copy constructor
                other = args[0]
                self.name = other.name
                self.size = other.size
                self.underline = other.underline
                self.bold = other.bold
                self.italic = other.italic
                self.color = other.color
            elif isinstance(args[0], int):
                # Size-only constructor
                self.size = args[0]
        elif len(args) == 2:
            # Size and color
            self.size = args[0]
            self.color = args[1]
        elif len(args) == 3:
            # Size, color, and bold
            self.size = args[0]
            self.color = args[1]
            self.bold = args[2]
        elif len(args) >= 6:
            # Full parameter set
            self.size = args[0]
            self.color = args[1]
            self.bold = args[2]
            self.italic = args[3]
            self.underline = args[4]
            self.name = args[5]

    # Getter and setter methods
    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_size(self) -> int:
        return self.size

    def set_size(self, size: int):
        self.size = size

    def is_underline(self) -> bool:
        return self.underline

    def set_underline(self, underline: bool):
        self.underline = underline

    def is_bold(self) -> bool:
        return self.bold

    def set_bold(self, bold: bool):
        self.bold = bold

    def is_italic(self) -> bool:
        return self.italic

    def set_italic(self, italic: bool):
        self.italic = italic

    def get_color(self) -> str:
        return self.color

    def set_color(self, color: str):
        self.color = color

    def __repr__(self) -> str:
        return (f"Font(name='{self.name}', size={self.size}, bold={self.bold}, "
                f"italic={self.italic}, underline={self.underline}, color='{self.color}')")