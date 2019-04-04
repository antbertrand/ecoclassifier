"""See https://stackoverflow.com/questions/287871/print-in-terminal-with-colors"""

# Symbolic
HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKGREEN = "\033[92m"
ENDC = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# Semantic
CONFIG_INFO = "\033[95m"  # Display config information
DESCRIBE = "\033[2m"  # Describe what we're doing
WARNING = "\033[93m"
SUCCESS = "\033[92m"
TITLE = "\033[93m"  # Used for help titles
NONE = "\033[0m"
INFO = "\033[96m"  # Context-specific information / heads up
ECHO = "\033[94m"  # Echo a shell command
FAIL = "\033[91m"
