from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from pathlib import Path
import threading
import logging
from time import sleep
import csv
from datetime import datetime
import json
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AnswerBox(BaseModel):
    box_2d: list[int]
    description: str

class AllAnswers(BaseModel):
    answers: list[str]
    isRight: bool

class QuizResponse(BaseModel):
    question: str
    allAnswers: list[AllAnswers]
    analysis: str
    bgcolor: str
    answers: list[AnswerBox]


class AI:
    def __init__(self, model, folder_name, response_analysis):
        self.model = model
        self.folder_name = folder_name
        load_dotenv()
        self.client = genai.Client()
        self.last_image = None
        self.last_response = None
        self.response_analysis = response_analysis
        logger.info('init')
        logger.info(self.model)

    def received_last_photo(self, last_image):
        logger.info('- Photo received')

        thread = threading.Thread(
            target=self._run_async_query,
            args=(last_image,),
            daemon=True
        )
        thread.start()

        logger.info('- Thread end')

    def _run_async_query(self, image_name):
        response = self.ask_ai(image_name)
        if response:
            self.last_response = response

            try:
                data = json.loads(response.text)
                print("\n" + "=" * 40)
                print("PRZEMYŚLENIA AI (ANALIZA):")
                print(data.get('analysis', 'Brak analizy...'))
                print("=" * 40 + "\n")

                # Zapisujemy pytanie do pliku questions.json
                self.save_question(data, image_name)

            except Exception as e:
                logger.error(f"Błąd parsowania/zapisu JSON: {e}")
                print(response.text)

            print(f"Prompt Tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Total Tokens: {response.usage_metadata.total_token_count}")

            self.save_query_stats(
                self.model,
                response.usage_metadata.prompt_token_count,
                response.usage_metadata.total_token_count
            )
            logger.info(f"Used tokens: {response.usage_metadata.total_token_count}")

            if self.response_analysis:
                self.response_analysis(response)

    def save_question(self, question_data: dict, image_name: str, file_path="questions.json"):
        path = Path(file_path)
        questions = []

        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        questions = content
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Nie udało się odczytać istniejącego questions.json: {e}")
                questions = []

        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image": str(image_name),
            **question_data
        }
        questions.append(entry)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        logger.info(f"Pytanie zapisane do {file_path}")

    def save_query_stats(self, model, prompt_tokens, total_tokens, file_path="tokens.csv"):
        file_exists = Path(file_path).exists()

        with open(file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["Timestamp", "Model", "Prompt_Tokens", "Total_Tokens"])

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                model,
                prompt_tokens,
                total_tokens
            ])

    def get_photo(self, image_name):
        try:
            image_path = Path(image_name)
            image = Image.open(image_path)
            logger.info("Photo successfully found")
            return image
        except FileNotFoundError as e:
            logger.error(e)
            print(e)
            return None

    def ask_ai(self, image_name):
        image = self.get_photo(image_name)
        if not image:
            logger.error('No image')
            return None

        prompt = "Rozwiąż zadania widoczne na zrzucie ekranu. Zaznacz wszystkie poprawne odpowiedzi. Poprawnych odpowiedzi może być kilka, jedna bądź zero"

        sys_instruct = (
            "Jesteś precyzyjnym ekspertem rozwiązującym testy i egzaminy. "
            "Twoje zadanie to znalezienie poprawnych odpowiedzi na dostarczonym obrazie. "
            "KROK 1: W polu 'question' podaj treść pytania. "
            "KROK 2: W polu 'allAnswers' podaj wszystkie odpowiedzi. "
            "KROK 3: W polu 'analysis' krótko przeanalizuj widoczne opcje, zwracając uwagę na podchwytliwe słowa. "
            "KROK 4: W polu 'bgcolor' podaj w formacie HEX (np. '#00FF00', '#FF0000') kolor znacznika, który będzie o 50% ciemniejszy od koloru tła w przypadku tła jasnego lub o 50% jaśniejszy od koloru tła w przypadku tła ciemnego. "
            "KROK 5: W polu 'answers' podaj poprawne opcje. "
            "Współrzędne podawaj ZAWSZE w znormalizowanej skali 0-1000 w formacie [ymin, xmin, ymax, xmax]. Postaraj się podać miejsce checkboxa poprawnej odpowiedzi. Jeżeli takiego nie ma wskaż środek odpowiedzi."
        )

        for i in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        image,
                        prompt
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        top_k=1,
                        top_p=0.1,
                        response_mime_type="application/json",
                        response_schema=QuizResponse,
                        system_instruction=sys_instruct
                    )
                )
                logger.info("- Response received")
                return response
            except Exception as e:
                logger.error(f"Próba {i + 1}: {e}")
                print(f"Błąd API w próbie {i + 1}: {e}")
                sleep(1)

        return None