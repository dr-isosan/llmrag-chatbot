from rag_chatbot impor    "OMÜ öğrencileri Office365 uygulamalarını bilgisayarlarına indirip kurabilir mi?", 
    "OMÜ'de yeni bir web alan adı açtırmak isteyen birim veya projelerin nasıl bir yol izlemesi gerekmektedir?",
    "Tokatta hava kaç derece?",
    "Tokatta hava kaç derece?"_answer

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
   " OMÜ öğrencileri eduroam ağına bağlanırken hangi kullanıcı adı ve parolayı kullanmalıdır?",

    "Android cihazlarda eduroam bağlantısı için hangi EAP ve Phase 2 ayarları yapılmalıdır?",
    "OMÜ öğrencileri Office365 hesabına girişte hangi e-posta adresi formatını kullanmalıdır?",
    
    "OMÜ öğrencileri Office365 hesabına girişte hangi e-posta adresi formatını kullanmalıdır?",

    "OMÜ öğrencileri Office365 uygulamalarını bilgisayarlarına indirip kurabilir mi?", 
    "OMÜ’de yeni bir web alan adı açtırmak isteyen birim veya projelerin nasıl bir yol izlemesi gerekmektedir?"

    "Tokatta hava kaç derece?",
    "Tokatta hava kaç derece?",


    
]

def main():
    answers = []
    sources = []
    for q in questions:
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
    print("\nSoru-Cevap-Kaynak Listesi:")
    for idx, (q, a, s) in enumerate(answers, 1):
        print(f"{idx}. Soru: {q}\n   Cevap: {a}\n   Kaynak: {s}\n")

if __name__ == "__main__":
    main()
