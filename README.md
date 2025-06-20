<img src="vibely_logo.png" alt="Logo Vibely" width="650"/>

# 🎵 Vibely – Music Recommendation System

The project was carried out as part of a **undergraduate thesis** at the **Università Roma Tre**.

---

## 🧠 Objective of the project
Vibely is a web app aimed at creating personalized playlists based on the user's emotional state and tastes. 

I tried to go beyond traditional recommendation methods based on history and music genres by focusing specifically on the user's mood. 

Vibely uses a Gemini AI model by classifying the user's emotions through the Russell Circumplex Model. The mapping of the mood occurs directly and precisely with the use of valence and energy leading to a targeted musical choice.

---

## 🔗 Try the app online

👉 [Click here to use Vibely on Streamlit](https://vibelymrs-vibely-vibely-za9vfe.streamlit.app/)

---

## ⚙️ Instructions for local use

To run the app locally:

### 1. Clone the repository
```bash
git clone https://github.com/VibelyMRS/Vibely.git
cd vibely
```
### 2. Create the virtual environment
```bash
python -m venv .venv
```
### 3. Activate the ambient
```bash
.venv\Scripts\activate
```

### 4. Install the required packages
```bash
pip install -r requirements.txt
```

### 4. Launch the app
```bash
streamlit run vibely.py
```

## 📁 Contents of the repository

- `app.py` – Main code of the web app
- `dataset.csv` – Reference dataset for the recommendation
- `vibely_logo.png` – Logo displayed in the app and README
- `requirements.txt` – Necessary Python dependencies
- `README.md` – Project documentation
- `LICENSE` – MIT license of the code

---

## ✍️ Author

**Davide Marrocco**

Bachelor's Degree Thesis – Roma Tre University

Degree Course in **Computer Science and Artificial Intelligence Engineering**

Academic Year **2024/2025**

---

## 📄 License

This project is distributed under the **MIT** license. 
See the [`LICENSE`](LICENSE) file for more details.

---

## 🙏 Acknowledgements

- Roma Tre University
- All participants who tested Vibely and provided feedback via Google Form
