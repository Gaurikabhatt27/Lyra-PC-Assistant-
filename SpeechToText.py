from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

folder_path = os.path.join("..", "Data")
file_path = os.path.join(folder_path, "Voice.html")

# Ensure 'Data' folder exists
os.makedirs(folder_path, exist_ok=True)

# Modify HTML code with input language
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

with open(file_path, "w") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()
Link = f"file:///{os.path.abspath(file_path)}"  # Use absolute path

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"

chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--no-sandbox")  
chrome_options.add_argument("--disable-gpu")  
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  
chrome_options.add_argument("--remote-debugging-port=0")  # Forces Chrome to NOT expose a debugging port
chrome_options.add_argument("--disable-features=UseTensorFlowLiteForSpeechRecognition")
chrome_options.add_argument("--disable-component-update")  # Prevent Chrome from updating experimental AI models



service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
TempDirPath = rf"{current_dir}/Frontend/Files"

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's","Are","Am I"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    driver.get(Link)


    try:
        # Wait for the "start" button to be present
        start_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "start"))
        )
        start_button.click()

        while True:
            try:
                # Wait for the "output" element to have text
                output_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "output"))
                )
                Text = output_element.text

                if Text:
                    driver.find_element(by=By.ID, value="end").click()

                    if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                        return QueryModifier(Text)
                    else:
                        SetAssistantStatus("Translating...")
                        return QueryModifier(UniversalTranslator(Text))

            except Exception as e:
                print(f"Error during recognition: {e}")
                break

    except Exception as e:
        print(f"Error loading page or finding elements: {e}")

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        if Text:
            print(Text)