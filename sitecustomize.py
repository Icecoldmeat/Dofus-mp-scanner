import sys
from dotenv import load_dotenv
from definitions import DOTENV_PATH, SOURCE_PATH

# load enviromental variables
load_dotenv(DOTENV_PATH)
sys.path.append(SOURCE_PATH)

print("Env files loaded!")

