import google.generativeai as genai

# !!! WKLEJ TUTAJ SWÓJ KLUCZ !!!
genai.configure(api_key="AIzaSyBptJKuP0KOP2_lKZjMLmBoYKDki4im1No")

print("Szukam dostępnych modeli...")

try:
    for m in genai.list_models():
        # Szukamy tylko modeli, które potrafią generować tekst (czat)
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Błąd: {e}")