"""
Gelişmiş sohbet sistemi test scripti
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_enhanced_chat():
    """Gelişmiş sohbet sistemini test et"""
    
    user_id = f"test_user_{int(time.time())}"
    
    print("🧪 Gelişmiş Sohbet Sistemi Test Başlıyor...")
    print(f"👤 Test Kullanıcı ID: {user_id}")
    print("-" * 50)
    
    # Test senaryoları
    test_cases = [
        {
            "message": "Merhaba",
            "expected_type": "greeting",
            "description": "Selamlama testi"
        },
        {
            "message": "Sınav kuralları nelerdir?",
            "expected_type": "knowledge_answer",
            "expected_category": "sınav",
            "description": "Sınav kuralları bilgi testi"
        },
        {
            "message": "Final sınavı ne zaman?",
            "expected_type": "knowledge_answer",
            "expected_category": "tarih",
            "description": "Tarih bilgisi testi"
        },
        {
            "message": "Rastgele bir soru ki cevabı yok",
            "expected_type": "no_answer",
            "description": "Cevap bulunamama testi"
        },
        {
            "message": "Teşekkürler",
            "expected_type": "goodbye",
            "description": "Veda testi"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"📝 Mesaj: {test_case['message']}")
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat", 
                json={
                    "message": test_case["message"],
                    "user_id": user_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Yanıt: {data.get('response', '')[:100]}...")
                print(f"🏷️  Tip: {data.get('type', 'N/A')}")
                print(f"📂 Kategori: {data.get('category', 'N/A')}")
                print(f"🎯 Güven: {data.get('confidence', 0):.2f}")
                print(f"⭐ Kalite: {data.get('quality_level', 'N/A')}")
                print(f"📚 Kaynaklar: {len(data.get('sources', []))}")
                
                # Beklenen sonuçları kontrol et
                if 'expected_type' in test_case:
                    if data.get('type') == test_case['expected_type']:
                        print("✅ Tip kontrolü başarılı")
                    else:
                        print(f"❌ Tip kontrolü başarısız. Beklenen: {test_case['expected_type']}, Alınan: {data.get('type')}")
                
                if 'expected_category' in test_case:
                    if data.get('category') == test_case['expected_category']:
                        print("✅ Kategori kontrolü başarılı")
                    else:
                        print(f"❌ Kategori kontrolü başarısız. Beklenen: {test_case['expected_category']}, Alınan: {data.get('category')}")
                        
            else:
                print(f"❌ API Hatası: {response.status_code}")
                print(f"📄 Hata: {response.text}")
                
        except Exception as e:
            print(f"❌ Test hatası: {e}")
        
        time.sleep(1)  # API'yi yormamak için
    
    # Sohbet geçmişini test et
    print(f"\n📜 Sohbet geçmişi kontrolü...")
    try:
        history_response = requests.get(f"{BASE_URL}/api/conversation/history", 
            params={"user_id": user_id}
        )
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            print(f"✅ Toplam mesaj: {history_data.get('total_messages', 0)}")
            print(f"📝 Geçmiş mevcut: {len(history_data.get('conversation_history', []))}")
        else:
            print(f"❌ Geçmiş kontrolü başarısız: {history_response.status_code}")
            
    except Exception as e:
        print(f"❌ Geçmiş kontrolü hatası: {e}")
    
    # Sohbet geçmişini temizle
    print(f"\n🧹 Sohbet geçmişi temizleme...")
    try:
        clear_response = requests.post(f"{BASE_URL}/api/conversation/clear", 
            json={"user_id": user_id}
        )
        
        if clear_response.status_code == 200:
            print("✅ Sohbet geçmişi temizlendi")
        else:
            print(f"❌ Temizleme başarısız: {clear_response.status_code}")
            
    except Exception as e:
        print(f"❌ Temizleme hatası: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test tamamlandı!")


if __name__ == "__main__":
    test_enhanced_chat()
