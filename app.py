import streamlit as Dropper
from openai import OpenAI

Dropper.set_page_config(page_title="Generator Dyskusji", page_icon="🎯", layout="wide")

Dropper.title("🎯 Generator Dyskusji i Symulator Postaci")
Dropper.markdown("Stwórz zaawansowany model postaci na podstawie danych i przeprowadź strategiczną symulację rozmowy.")

# Panel boczny na konfigurację
with Dropper.sidebar:
    Dropper.header("1. Konfiguracja Systemu")
    api_key_input = Dropper.text_input("Wprowadź swój Klucz API OpenAI", type="password")
    
    Dropper.divider()
    Dropper.header("2. Profil Postaci")
    character_name = Dropper.text_input("Imię i nazwisko / Rola postaci", value="Jan Kowalski (Dyrektor Finansowy)")
    character_description = Dropper.text_area(
        "Opis postaci, sposób bycia, poglądy i cele",
        value="Ostrożny menedżer, skupia się na twardych danych i ROI. Nie znosi lania wody, preferuje krótkie i konkretne komunikaty. Obawia się ryzyka budżetowego."
    )
    
    target_goal = Dropper.text_area(
        "Cel Twojej dyskusji z postacią",
        value="Przekonać do zwiększenia budżetu marketingowego na Q3 o 15%."
    )

if not api_key_input:
    Dropper.warning("👈 Wprowadź swój klucz API OpenAI w panelu bocznym, aby uruchomić symulator.")
else:
    client = OpenAI(api_key=api_key_input)

    # Inicjalizacja pamięci czatu
    if "messages" not in Dropper.session_state:
        Dropper.session_state.messages = [
            {
                "role": "system",
                "content": f"Jesteś postacią: {character_name}. Opis Twojego profilu i zachowania: {character_description}. "
                           f"Twoim zadaniem jest wcielenie się w tę postać podczas dyskusji z użytkownikiem. "
                           f"Użytkownik próbuje osiągnąć cel: {target_goal}. "
                           f"Reaguj naturalnie, zgodnie ze swoim profilem, stawiaj opory tam, gdzie postać normalnie by je stawiała, i daj się przekonać tylko wtedy, gdy argumenty będą spójne z Twoim profilem."
            },
            {
                "role": "assistant",
                "content": f"Dzień dobry. Słucham, w jakiej sprawie dzisiaj rozmawiamy?"
            }
        ]

    # Wyświetlanie historii czatu
    for message in Dropper.session_state.messages:
        if message["role"] != "system":
            with Dropper.chat_message(message["role"]):
                Dropper.markdown(message["content"])

    # Obsługa wprowadzania wiadomości przez użytkownika
    if prompt := Dropper.chat_input("Napisz swoją wypowiedź do postaci..."):
        Dropper.session_state.messages.append({"role": "user", "content": prompt})
        with Dropper.chat_message("user"):
            Dropper.markdown(prompt)

        # Generowanie odpowiedzi przez model AI
        with Dropper.chat_message("assistant"):
            with Dropper.spinner("Postać analizuje wypowiedź..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=Dropper.session_state.messages
                )
                assistant_reply = response.choices[0].message.content
                Dropper.markdown(assistant_reply)
        
        Dropper.session_state.messages.append({"role": "assistant", "content": assistant_reply})
