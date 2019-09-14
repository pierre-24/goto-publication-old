API_KEY = {}

# Load the production settings, overwrite the existing ones if needed
try:
    from settings_prod import *  # noqa
except ImportError:
    pass
