from rag_chatbot import get_answer

# Sırasıyla sorulacak sorular
questions = [
    "eduroam şifremi nasıl alırım",
    "eduroam parolamı nasıl alırım", 
    "eduroam şifremi nasıl alırım",
    "OMÜ Mühendislik Fakültesi'nde sınav sırasında cep telefonu bulundurmanın kuralları nelerdir?",
    "Sınav sırasında hesap makinesi kullanımına izin verildiğinde hangi özelliklere sahip makineler yasaktır?",
    "Sınav başladıktan sonra ilk 15 dakika içinde salona gelen bir öğrenci sınava katılabilir mi?",
    "Bilgisayar laboratuvarlarında yapılan sınavlara su getirmek serbest midir?",
    "Sınav sırasında başka bir öğrenciden kalem veya hesap makinesi istemek ne olarak değerlendirilir?",
    "OMÜ öğrencileri eduroam ağına bağlanırken hangi kullanıcı adı ve parolayı kullanmalıdır?",
    "Android cihazlarda eduroam bağlantısı için hangi EAP ve Phase 2 ayarları yapılmalıdır?",
    "OMÜ öğrencileri Office365 hesabına girişte hangi e-posta adresi formatını kullanmalıdır?",
    "OMÜ öğrencileri Office365 uygulamalarını bilgisayarlarına indirip kurabilir mi?", 
    "OMÜ'de yeni bir web alan adı açtırmak isteyen birim veya projelerin nasıl bir yol izlemesi gerekmektedir?",
    "Tokatta hava kaç derece?",
    "EndNote programı nedir ve nasıl kullanılır?"
]

def main():
    answers = []
    sources = []
    for q in questions:
        try:
            answer = get_answer(q)
            # Kaynak bilgisini ayır
            if "Kullanılan kaynak:" in answer:
                ans, src = answer.split("Kullanılan kaynak:", 1)
                ans = ans.strip()
                src = src.strip()
            else:
                ans = answer.strip()
                src = "-"
            answers.append((q, ans, src))
            print(f"✅ İşlendi: {q[:50]}...")
        except Exception as e:
            print(f"❌ Hata: {q[:50]}... -> {e}")
            answers.append((q, f"Hata: {e}", "-"))
    
    print("\n" + "="*80)
    print("SORU-CEVAP-KAYNAK LİSTESİ")
    print("="*80)
    
    for idx, (q, a, s) in enumerate(answers, 1):
        print(f"\n{idx}. SORU: {q}")
        print(f"   CEVAP: {a}")
        print(f"   KAYNAK: {s}")
        print("-" * 60)

if __name__ == "__main__":
    main()
