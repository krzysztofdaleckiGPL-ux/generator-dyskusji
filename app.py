import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Generator Dyskusji (Groq)", page_icon="🎯", layout="wide")

st.title("🎯 Generator Dyskusji i Symulator Postaci (Groq)")
st.markdown("Symulacja rozmowy z modelem behawioralnym przy użyciu darmowego API Groq.")

# Panel boczny na konfigurację
with st.sidebar:
    st.header("1. Konfiguracja Systemu")
    api_key_input = st.text_input("Wprowadź swój Klucz API Groq (zaczyna się od gsk_)", type="password")
    st.markdown("[Pobierz darmowy klucz z Groq Console](https://console.groq.com/keys)")
    
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

if not api_key_input:
    st.warning("👈 Wprowadź swój klucz API Groq w panelu bocznym, aby uruchomić symulator.")
else:
    # Klient OpenAI skierowany na serwery Groq
    client = OpenAI(
        api_key=api_key_input,
        base_url="https://api.groq.com/openai/v1"
    )

    # Inicjalizacja pamięci czatu
    if "messages" not in st.session_state:
        st.session_state.messages = [
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
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Obsługa wprowadzania wiadomości przez użytkownika
    if prompt := st.chat_input("Napisz swoją wypowiedź do postaci..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generowanie odpowiedzi przez Groq z użyciem stabilnego modelu llama-3.1-8b-instant
        with st.chat_message("assistant"):
            with st.spinner("Postać analizuje wypowiedź..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=st.session_state.messages
                    )
                    assistant_reply = response.choices[0].message.content
                    st.markdown(assistant_reply)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                except Exception as e:
                    st.error(f"Wystąpił błąd: {e}")
