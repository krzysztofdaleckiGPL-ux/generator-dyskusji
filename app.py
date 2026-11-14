import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Generator Dyskusji (Groq)", page_icon="🎯", layout="wide")

st.title("🎯 Generator Dyskusji i Symulator Postaci (Groq)")
st.markdown("Symulacja rozmowy z modelem behawioralnym przy użyciu darmowego API Groq.")

with st.sidebar:
    st.header("1. Konfiguracja Systemu")
    api_key_input = st.text_input("Wprowadź swój Klucz API Groq (zaczyna się od gsk_)", type="password")
    st.markdown("[Pobierz darmowy klucz z Groq Console](https://console.groq.com/keys)")
    
    selected_model = None
    if api_key_input:
        try:
            temp_client = OpenAI(api_key=api_key_input, base_url="https://api.groq.com/openai/v1")
            models_data = temp_client.models.list()
            available_models = [
                m.id for m in models_data.data 
                if "whisper" not in m.id.lower() and "guard" not in m.id.lower() and "tts" not in m.id.lower()
            ]
            if available_models:
                selected_model = st.selectbox("Wybierz aktywny model z Twojego konta:", available_models)
            else:
                st.error("Nie znaleziono aktywnych modeli tekstowych dla tego klucza.")
        except Exception as e:
            st.error(f"Błąd połączenia z API przy pobieraniu modeli: {e}")

    st.divider()
    st.header("2. Profil Postaci")
    character_name = st.text_input("Imię i nazwisko / Rola postaci", value="Jan Kowalski (Dyrektor Finansowy)")
    character_description = st.text_area(
        "Opis postaci, sposób bycia, poglądy i cele",
        value="Ostrożny menedżer, skupia się na twardych danych i ROI. Nie znosi lania wody, preferuje krótkie i konkretne komunikaty. Obawia się ryzyka budżetowego."
    )
    
    target_goal = st.text_area(
        "Cel Twojej dyskusji z postacią",
        value="Przekonać do zwiększenia budżetu marketingowego na Q3 o 15%."
    )

    # Przycisk do resetowania rozmowy po zmianie postaci
    if st.button("🔄 Zastosuj nową postać / Resetuj czat", use_container_width=True):
        st.session_state.pop("messages", None)
        st.rerun()

if not api_key_input:
    st.warning("👈 Wprowadź swój klucz API Groq w panelu bocznym, aby uruchomić symulator.")
elif not selected_model:
    st.warning("👈 Poczekaj na załadowanie listy modeli lub sprawdź poprawność klucza API w panelu bocznym.")
else:
    client = OpenAI(
        api_key=api_key_input,
        base_url="https://api.groq.com/openai/v1"
    )

    # Dynamiczna instrukcja systemowa bazująca na aktualnych polach w panelu bocznym
    system_prompt = (
        f"Jesteś postacią: {character_name}. Opis Twojego profilu i zachowania: {character_description}. "
        f"Twoim zadaniem jest wcielenie się w tę postać podczas dyskusji z użytkownikiem. "
        f"Użytkownik próbuje osiągnąć cel: {target_goal}. "
        f"Reaguj naturalnie, zgodnie ze swoim profilem, stawiaj opory tam, gdzie postać normalnie by je stawiała, "
        f"i daj się przekonać tylko wtedy, gdy argumenty będą spójne z Twoim profilem. Rozmawiaj wyłącznie po polsku."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": f"Dzień dobry. Jestem {character_name}. W czym mogę pomóc?"}
        ]
    else:
        # Nadpisanie promptu systemowego na bieżąco, gdyby użytkownik edytował pola bez klikania resetu
        st.session_state.messages[0]["content"] = system_prompt

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Napisz swoją wypowiedź do postaci..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Postać analizuje wypowiedź..."):
                try:
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=st.session_state.messages
                    )
                    assistant_reply = response.choices[0].message.content
                    st.markdown(assistant_reply)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                except Exception as e:
                    st.error(f"Wystąpił błąd: {e}")
