import streamlit as st
import pandas as pd
import re
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Vibely", layout="centered")

# --- STILE CSS UNIFICATO ---
st.markdown("""
    <style>
        .stApp {
            background-color: #000000;
            color: #FFFFFF;
            font-family: 'Arial', sans-serif;
        }

        h1, h2, h3, h4, p, label {
            color: #1DB954 !important;
        }

        .stButton>button {
            background-color: #000000;
            color: #1DB954;
            border: 1px solid #1DB954;
            border-radius: 10px;
            padding: 0.5em 1em;
            font-weight: bold;
        }

        a {
            color: #1DB954;
            text-decoration: underline;
        }

        .centered {
            text-align: center;
        }
        
    </style>
""", unsafe_allow_html=True)

# --- LOGO CENTRALE ---
st.markdown("<br>", unsafe_allow_html=True)
st.image("vibely_logo.png", width=650)

# --- CONFIGURA API ---
genai.configure(api_key="AIzaSyAvuhTgURgvzTRIp51CzIggks-top10DRs")

# --- LOAD DATA ---
df = pd.read_csv("spotify_songs.csv")
similarity_df = pd.read_csv("correlation_matrix.csv", index_col=0)

# --- SESSION STATE ---
if "step_done" not in st.session_state:
    st.session_state.step_done = False
if "mood_analyzed" not in st.session_state:
    st.session_state.mood_analyzed = False
if "mood_text" not in st.session_state:
    st.session_state.mood_text = ""

# --- ARTISTI PREFERITI ---
st.markdown("<h3 class='centered'>🎤 Now tell us your favorite artists</h3>", unsafe_allow_html=True)

artist_list = sorted(df['Artist'].dropna().unique())
selected_artists = st.multiselect("Choose one or more artists", options=artist_list)

if st.button("Done!"):
    if not selected_artists:
        st.warning("Please select at least one artist.")
    else:
        st.session_state.step_done = True
        st.session_state.selected_artists = selected_artists

# --- ANALISI MOOD ---
if st.session_state.step_done:

    selected_artists = st.session_state.selected_artists

    def get_similar_artists(favourite_artists, ascending=False):
        size = len(favourite_artists)
        total_artists = 25
        new_artists = int(total_artists / size)
        top_similar = []
        for artist in favourite_artists:
            similar_artists = similarity_df[artist].sort_values(ascending=ascending)[0:new_artists]
            top_similar.extend(similar_artists.index.tolist())
        return top_similar

    top_artists = get_similar_artists(selected_artists, ascending=False)
    preferred_df = df[df["Artist"].isin(top_artists)]

    st.markdown("<h3 class='centered'>💭 How are you feeling today?</h3>", unsafe_allow_html=True)
    mood_input = st.text_area("Write your mood here 👇", value=st.session_state.mood_text, placeholder="E.g., I feel happy and full of energy!")

    if mood_input:
        st.session_state.mood_text = mood_input

    if st.button("Analyze"):
        if not st.session_state.mood_text.strip():
            st.warning("Please write something before continuing.")
        else:
            st.info("Analyzing your mood... please wait ⏳")
            st.session_state.mood_analyzed = True

    if st.session_state.mood_analyzed:
        mood = st.session_state.mood_text
        model = genai.GenerativeModel('models/gemma-3-27b-it')

        emotional_analysis_prompt= f"""
            Definisci quanto è pacato il testo. La pacatezza può avere valore compreso tra 0.1433 e 0.777.
            Definisci anche quanto è felice il testo. La felicità può avere valore compreso tra 0.166 e 0.88
            Se nel testo si esprime un desiderio (ad esempio, "vorrei ascoltare qualcosa di energetico"),
            considera il desiderio come un'indicazione per il parametro da impostare. Per esempio,
            se il testo esprime un desiderio di energia, l'energia dovrebbe essere alta.
            La risposta generata deve avere solo due valori scritti come segue: energia = 0.5, felicità = 0.6.
            Le cifre devono essere arrotondate alla quarta cifra dopo la virgola.
            Dai un breve motivo delle tue scelte.


            Testo da anallizzare: {mood}
            """
        response = model.generate_content(contents=[emotional_analysis_prompt])

        def extract_values_and_justification(answer_text):
            # Cerca i valori di calma e felicità (numeri con punto come separatore)
            match = re.search(r"energia\s*=\s*([\d.]+)\s*,\s*felicit[àa]\s*=\s*([\d.]+)", answer_text)

            if not match:
                raise ValueError("Values not found in response.")

            calmness = float(match.group(1))
            valence = float(match.group(2))

            justification_match = re.search(r"\*\*Motivazione:\*\*\s*(.*)", answer_text, re.DOTALL)
            justification = justification_match.group(1).strip() if justification_match else "Justification not found."

            return calmness, valence, justification

        parts = response.to_dict()["candidates"][0]["content"]["parts"]
        energy, valence, justification = extract_values_and_justification(parts[0].get('text'))

        radius = 0.05
        increment = 0.05
        n_recommended_songs = 10

        def recommend_songs(radius, data_frame, extra_songs = 25):
            print(f"Radius", {radius})
            
            #Get all the songs in a certain radius
            filtered_df = data_frame[(data_frame['Energy'] >= energy - radius) & (data_frame['Energy'] <= energy + radius) & 
                        (data_frame['Valence'] >= valence - radius) & (data_frame['Valence'] <= valence + radius)]

            if filtered_df.shape[0] < n_recommended_songs+extra_songs:
                #Do not get songs too far away
                if (radius>0.2)and(filtered_df.shape[0]>=15):
                    print(f"Found music: ({filtered_df.shape[0]}).")
                    return filtered_df
                
                #If the number of songs is not enough
                print(f"There are not enough songs. I increase the radius to {radius}")
                return recommend_songs(radius+increment, data_frame)  #Recursive call
            else:
                print(f"I found enough songs ({filtered_df.shape[0]}).")
                return filtered_df

        preferred_songs = recommend_songs(radius, preferred_df)
        all_songs = recommend_songs(radius, df, extra_songs=17)

        n_preferred_songs = preferred_songs.shape[0]
        if n_preferred_songs < n_recommended_songs:
            recommended_songs = preferred_songs.sample(n=n_preferred_songs)
        else:
            recommended_songs = preferred_songs.sample(n=n_recommended_songs)

        def check_set(df, search_in_preferred_songs=True):
            df = df.drop_duplicates()
            df_X_size = df.shape[0]
            if df_X_size == n_recommended_songs:
                return df
            else:
                missing_songs = n_recommended_songs - df_X_size
                new_songs = (preferred_songs if search_in_preferred_songs else all_songs).sample(n=missing_songs)
                df = pd.concat([df, new_songs], ignore_index=True)
                return check_set(df, False)

        recommended_songs = check_set(recommended_songs)

        st.markdown("<h3 class='centered'>🎶 Songs we recommend based on your mood and favorite artists</h3>", unsafe_allow_html=True)
        st.dataframe(recommended_songs[['Track', 'Artist', 'Album']].reset_index(drop=True), use_container_width=True)

        st.markdown("<h3 class='centered'>🌟 Most popular songs</h3>", unsafe_allow_html=True)
        popular_songs = all_songs.sort_values(by='Views', ascending=False).head(n_recommended_songs)
        popular_songs = check_set(popular_songs, search_in_preferred_songs=False)
        st.dataframe(popular_songs[['Track', 'Artist', 'Album']].reset_index(drop=True), use_container_width=True)

        st.markdown("<h3 class='centered'>🎵 Random songs</h3>", unsafe_allow_html=True)
        random_songs = df.sample(n_recommended_songs)
        st.dataframe(random_songs[['Track', 'Artist', 'Album']].reset_index(drop=True), use_container_width=True)

        # --- FEEDBACK SECTION ---
        st.markdown(
            """
            <h3 class='centered'>📋 Would you like to leave me some feedback?</h3>
            <p class='centered' style='color: #1DB954; font-size: 16px;'>
                Fill out this short 
                <a href='https://docs.google.com/forms/d/e/1FAIpQLSfQoB5g3yhcP2omysUej-0QUgJ7Ti4PxUgX45GXvbk7lTPLZg/viewform?usp=header' 
                target='_blank'>Google Form</a> to help us improve.
            </p>
            """,
            unsafe_allow_html=True
        )

        # --- RESET SESSION ---
        st.session_state.step_done = False
        st.session_state.mood_analyzed = False
        del st.session_state["selected_artists"]
