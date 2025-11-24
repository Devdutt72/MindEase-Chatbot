import os
import dotenv # pip install python-dotenv

# 1. Print where we are looking
print(f"Current Working Directory: {os.getcwd()}")

# 2. Try to load the .env file
success = dotenv.load_dotenv()

# 3. Check the results
print(f"Did .env load? {success}")
key = os.getenv("GEMINI_API_KEY")

if key:
    print(f"SUCCESS! Found Key: {key[:5]}********")
else:
    print("FAILURE: Key is None. Check your .env file name!")
    print("Files in this folder:")
    print(os.listdir(os.getcwd()))