import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

function_descriptions = [
    {
        "name": "extract_info_from_email",
        "description": "Extraitre les informations d'un eamil sur une centrale de production électrique pour créer une demande de travail dans un système EAM",
        "parameters": {
            "type": "object",
            "properties": {
                "TITRE": {
                    "type": "string",
                    "description": "un résumé de l'email envoyé"
                },
                "EQUIPEMENT": {
                    "type": "string",
                    "description": "essayer d'identifier la référence de l'équipement, uniquement l'identifiant"
                },
                "PRIORITE":{
                    "type": "string",
                    "priority": "Essayer d'identifier la priorité de l'anomale parmi les 3 valeurs suivantes: 1. HAUT; 2. MOYEN; 3. BAS"
                },
                "DISCIPLINE": {
                    "type": "string",
                    "description": "Essayer de classifier le corps de métier concerné parmi: 1. MECANICIEN 2. ELECTRICIEN ; 3. AUTOMATICIEN; 4. ROBINETIER"
                },
            },
            "required": ["TITRE", "EQUIPEMENT", "PRIORITE", "DISCIPLINE"]
        }
    }
]


email = """
Bonjour,
Nous venons de trouver une grosse fuite sur la pompe 1EASOO1PO. Nous avons mis un seau sous la fuite mais il faut le vider toutes les heures. La conduite s'en occupe.
Pourriez-vous demander à l'équipe réactive d'intervenir.
"""

prompt = f"Pouvez-vous extraire les informations clés de l'email?: {email} "
message = [{"role": "user", "content": prompt}]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=message,
    functions = function_descriptions,
    function_call="auto"
)

print(response)

class Email(BaseModel):
     from_email: str
     content: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/")
def analyse_email(email: Email):
     content = email.content
     query = f"Extraire l'information clé de cet email: {content} "

     messages = [{"role": "user", "content": query}]

     response = openai.ChatCompletion.create(
         model="gpt-3.5-turbo",
         messages=messages,
         functions = function_descriptions,
         function_call="auto"
     )

     arguments = response.choices[0]["message"]["function_call"]["arguments"]
     TITRE = eval(arguments).get("TITRE")
     EQUIPEMENT = eval(arguments).get("EQUIPEMENT")
     PRIORITE = eval(arguments).get("PRIORITE")
     DISCIPLINE = eval(arguments).get("DISCIPLINE")

     return {
         "TITRE": TITRE,
         "EQUIPEMENT": EQUIPEMENT,
         "PRIORITE": PRIORITE,
         "DISCIPLINE": DISCIPLINE
     }