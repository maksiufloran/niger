from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from pathlib import Path
import threading


class AI:
    def __init__(self, model, folder_name, response_analysis):
        self.model = model
        self.folder_name = folder_name
        load_dotenv()
        self.client = genai.Client()
        self.last_image = None
        self.last_response = None
        self.response_analysis = response_analysis

    def received_last_photo(self, last_image):
        print("Photo recived", last_image)

        thread = threading.Thread(
            target=self._run_async_query,
            args=(last_image,),
            daemon=True
        )
        thread.start()

    def _run_async_query(self, image_name):
        response = self.ask_ai(image_name)
        if response:
            self.last_response = response
            print(self.last_response.text)
            print(response.usage_metadata.prompt_token_count)
            print(response.usage_metadata.total_token_count)
            if self.response_analysis:
                self.response_analysis(response)


    def get_photo(self, image_name):
        try:
            image_path = Path(image_name)
            image = Image.open(image_path)
            return image
        except FileNotFoundError as e:
            print(e)
            return None

    def ask_ai(self, image_name):
        image = self.get_photo(image_name)
        if not image:
            return None

        img_width, img_height = image.size

        prompt = f"""
                Rozwiąż zadanie widoczne na zrzucie ekranu. Zwróć odpowiedź WYŁĄCZNIE w postaci surowego kodu JSON. 
                NIE używaj formatowania Markdown (nie dodawaj ```json na początku ani ``` na końcu).

                Zasady:
                1. Poprawnych odpowiedzi może być kilka, jedna lub zero.
                2. Współrzędne (x, y) w obiekcie "dots" podawaj TYLKO dla poprawnych odpowiedzi. 
                3. Współrzędne mają wskazywać na środek pola wyboru (checkboxa) lub środek tekstu poprawnej odpowiedzi.
                4. Jeżeli na zrzucie ekranu znajduje się więcej niż jedno pytanie, absolutnie NIE zwracaj listy obiektów (tablicy). Zwróć TYLKO JEDEN główny obiekt JSON.
                5. W przypadku wielu pytań na jednym obrazie, połącz wszystkie poprawne odpowiedzi i umieść ich współrzędne w jednej, wspólnej liście "dots". Pola "question" i "answers" mogą wtedy dotyczyć pierwszego pytania lub stanowić podsumowanie.

                Zastosuj się DOKŁADNIE do poniższego szablonu:
                {{
                  "question_nr": 1,
                  "resolution": "{img_width}x{img_height}",
                  "question": "Wpisz tutaj treść pytania (jeśli jest ich więcej, wpisz treść pierwszego)",
                  "answers": [
                    "Treść pierwszej odpowiedzi",
                    "Treść drugiej odpowiedzi",
                    "Treść trzeciej odpowiedzi"
                  ],
                  "dots": [
                    {{
                      "x": {int(img_width / 2)},
                      "y": {int(img_height / 2)},
                      "description": "Treść odpowiedzi oraz dlaczego ta odpowiedź na pierwsze pytanie jest poprawna"
                    }}
                  ]
                }}
                """

        if image:
            for i in range(3):
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=[
                            image,
                            prompt
                        ],
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            response_mime_type="application/json"
                        )
                    )
                    return response
                except Exception as e:
                    print(i, e)
