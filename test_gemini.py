import google.generativeai as genai

# !!! WKLEJ TUTAJ SWÓJ KLUCZ GOOGLE !!!
genai.configure(api_key="AIzaSyBptJKuP0KOP2_lKZjMLmBoYKDki4im1No")

# Używamy modelu 'gemini-pro' (jest najbardziej stabilny)
model = genai.GenerativeModel('gemini-2.0-flash')

print("Wysyłam zapytanie do Gemini... Czekaj...")

response = model.generate_content("Opowiedz krótki żart o programistach.")

print("\n--- ODPOWIEDŹ ---")
print(response.text)