# pylint: disable=line-too-long
# pylint: disable=dangerous-default-value
from enum import Enum
from typing import Callable, List
from datetime import datetime
import os

class Colors(Enum):
    """Colors for the terminal

    Args:
        Enum (str): All available ANSI formatting codes (some don't work)

    Returns:
        str: The ANSI formatting code
    """
    RESET = '\033[0m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    SLOW_BLINK = '\033[5m'
    REVERSE = '\033[7m'
    CONCEAL = '\033[8m'
    CROSSED_OUT = '\033[9m'
    REVEAL = '\033[28m'
    FRAMED = '\033[51m'  # doesn't work
    ENCIRCLED = '\033[52m'
    OVERLINED = '\033[53m'  # doesn't work
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'

    @classmethod
    def from_rgb(cls, red: int, green: int, blue: int) -> str:
        """Returns the ANSI formatting code for the given RGB color

        Args:
            red (int): The red value for the color (0-255)
            green (int): The green value for the color (0-255)
            blue (int): The blue value for the color (0-255)

        Returns:
            str: The ANSI formatting code for the color
        """
        return f"\033[38;2;{red};{green};{blue}m"


class Level(Enum):
    """The level of the log message
    
    Args:
        Enum (int): The number of the level
    """
    DEBUG = 0
    LOG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


class Handler:

    def __init__(self, formatter: Callable[[str, object, str, dict], str] = lambda text, level, name, colors: text) -> None:
        """A handler that gets called by the Logger when it logs something regardless of the level
        """
        pass

    def __call__(self, text: str, name: str, level: Level) -> None:
        """This method gets called when the Logger logs something

        Args:
            formatted_text (str): The text returned by the logger formatter
            level (Level): The Level of the log message
        """
        pass


class FileHandler(Handler):

    @staticmethod
    def filename_generator(directory: str, name: str, extension: str = "log") -> str:
        return f"{directory + '/' if directory else ''}{name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{extension}"

    @staticmethod
    def __latest_generator(directory: str, _: str, extension: str = "txt") -> str:
        return f"{directory + '/' if directory else ''}latest.{extension}"

    @staticmethod
    def __error_generator(directory: str, _: str, extension: str = "txt") -> str:
        return f"{directory + '/' if directory else ''}error.{extension}"

    @staticmethod
    def nameless_generator(directory: str, _: str, extension: str = "txt") -> str:
        return f"{directory + '/' if directory else ''}{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{extension}"

    latest_file_handler = lambda formatter, directory = "./logs": FileHandler(Level.DEBUG, formatter, directory, FileHandler.__latest_generator)
    error_file_handler = lambda formatter, directory = "./logs": FileHandler(Level.ERROR, formatter, directory, FileHandler.__error_generator)

    def __init__(self, level, formatter: Callable[[str, object, str, dict], str], directory: str = "./logs",  generator: Callable[[str, str], str] = filename_generator) -> None:
        self.generator = generator
        self.level = level
        self.formatter = formatter
        self.directory = directory

    def __call__(self, text: str, name: str, level: Level) -> None:
        if level.value >= self.level.value:
            file = self.generator(self.directory, name)
            if not os.path.exists(self.directory):
                os.mkdir(self.directory)
            with open(file, "a" if os.path.exists(file) else "w+") as f:
                f.write(self.formatter(str(text) + "\n", level, name, {}))


class Logger:

    # Default colors for the different levels
    default_colors = {
        "DEBUG": Colors.WHITE.value,
        "LOG": "",
        "INFO": Colors.GREEN.value,
        "WARNING": Colors.YELLOW.value,
        "ERROR": Colors.RED.value
    }

    @staticmethod
    def default_formatter(text, level: Level = Level.INFO, name: str = __name__, colors: dict = default_colors) -> str:
        """The default log formatter
        Args:
            text (any): The text to log
            level (Level, optional): The Level to use for logging. Defaults to Level.INFO.
            name (str, optional): The name for the current logger. Defaults to __name__.
        Returns:
            str: The formatted string for printing to the console
        """
        return f"{name} - {level.name}: {colors.get(level.name, '')}{str(text)}"

    @staticmethod
    def minecraft_formatter(text, level: Level = Level.INFO, name: str = __name__, colors: dict = default_colors) -> str:
        """The default log formatter for Minecraft
        Args:
            text (any): The text to log
            level (Level, optional): The Level to use for logging. Defaults to Level.INFO.
            name (str, optional): The name for the current logger. Defaults to __name__.
        Returns:
            str: The formatted string for printing to the console
        """
        return f"[{str(datetime.now().time()).split('.')[0]}] [{name}]: [{level.name}] {colors.get(level.name, '')}{str(text)}"

    def __init__(self, name: str = __name__, level: Level = Level.INFO,
                 formatter: Callable[[str, Level, str, dict], str] = default_formatter,
                 level_colors: dict = default_colors, handlers: List[Handler] = []):
        """A simple logger with color support and logging levels

        Args:
            name (str, optional): The name to use for the logger. Defaults to __name__.
            level (Level, optional): The lowest level to print to the console. Defaults to Level.INFO.
            formatter (Callable[[str, Level, str], str], optional): The formatter that returns a prettified string for logging. Defaults to default_formatter.
            level_colors (dict, optional): The colors to use for each level. Defaults to default_colors.
        """
        self.name = name
        self.formatter = formatter
        self.level = level
        self.colors = level_colors
        self.handlers = handlers

    def print(self, text: str, level: Level):
        for handler in self.handlers:
            handler(text, self.name, level)
        if self.level.value <= level.value:
            print(f"{self.formatter(str(text), level, self.name, self.colors)}{Colors.RESET.value}")

    def log(self, text="", level: Level = Level.LOG):
        """Logs the given text to the console

        Args:
            text (any): The text to log
            level (Level, optional): The level to use for logging. Defaults to Level.LOG.
        """
        self.print(text, level)


    def debug(self, text=""):
        """Logs a message at the Level.DEBUG level

        Args:
            text (any): The text to log
        """
        self.print(text, Level.DEBUG)

    def info(self, text=""):
        """Logs a message at the Level.INFO level

        Args:
            text (any): The text to log
        """
        self.print(text, Level.INFO)

    def warning(self, text=""):
        """Logs a message at the Level.WARNING level

        Args:
            text (any): The text to log
        """
        self.print(text, Level.WARNING)

    def error(self, text=""):
        """Logs a message at the Level.ERROR level

        Args:
            text (any): The text to log
        """
        self.print(text, Level.ERROR)


main_file_handler = FileHandler(Level.LOG, Logger.minecraft_formatter, "./logs", FileHandler.nameless_generator)

# Testing
if __name__ == "__main__":

    lg = Logger("Logger Test", level=Level.LOG, formatter=Logger.minecraft_formatter)

    for color in Colors:
        lg.log(f"{color.value}{color.name}")

    lg.log()
    lg.log()

    lg.debug("This won't get printed!")
    lg.info("This is an information!")
    lg.error(f"{Colors.ENCIRCLED.value}This is an error!")
    lg.error(f"{Colors.from_rgb(20, 100, 100)}This is an error with a color created from rgb")