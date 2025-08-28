#!/usr/bin/env python3
"""
RAG Chatbot API Comprehensive Test Suite
Bu dosya API'nin tüm endpoint'lerini test eder.
"""

import requests
import json
import time
import os
from pathlib import Path

# API Base URL
BASE_URL = "http://localhost:5000"


class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name, success, message=""):
        """Test sonucunu kaydet"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append(
            {"test": test_name, "success": success, "message": message}
        )

    def test_health_check(self):
        """Health check endpoint'ini test et"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK":
                    self.log_test("Health Check", True, "API çalışıyor")
                    return True
            self.log_test("Health Check", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_chat_endpoint(self):
        """Chat endpoint'ini test et"""
        try:
            # Boş mesaj testi
            response = self.session.post(
                f"{self.base_url}/api/chat", json={"message": ""}
            )
            if response.status_code == 400:
                self.log_test(
                    "Chat - Empty Message", True, "Boş mesaj doğru şekilde reddedildi"
                )
            else:
                self.log_test(
                    "Chat - Empty Message", False, f"Status: {response.status_code}"
                )

            # Normal soru testi
            test_question = "Sınav kuralları nedir?"
            response = self.session.post(
                f"{self.base_url}/api/chat", json={"message": test_question}
            )

            if response.status_code == 200:
                data = response.json()
                if "response" in data and "sources" in data:
                    self.log_test(
                        "Chat - Normal Question",
                        True,
                        f"Cevap alındı: {len(data['response'])} karakter",
                    )
                else:
                    self.log_test(
                        "Chat - Normal Question", False, "Invalid response format"
                    )
            else:
                self.log_test(
                    "Chat - Normal Question", False, f"Status: {response.status_code}"
                )

        except Exception as e:
            self.log_test("Chat Endpoint", False, f"Error: {str(e)}")

    def test_admin_endpoints(self):
        """Admin endpoint'lerini test et"""
        try:
            # Doküman listesi
            response = self.session.get(f"{self.base_url}/api/admin/documents")
            if response.status_code == 200:
                data = response.json()
                if "documents" in data and "total" in data:
                    self.log_test(
                        "Admin - Document List",
                        True,
                        f"{data['total']} doküman bulundu",
                    )
                else:
                    self.log_test(
                        "Admin - Document List", False, "Invalid response format"
                    )
            else:
                self.log_test(
                    "Admin - Document List", False, f"Status: {response.status_code}"
                )

            # Doküman durumu
            response = self.session.get(f"{self.base_url}/api/admin/documents/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Admin - Document Status",
                    True,
                    f"Total: {data.get('total_files', 0)}, "
                    f"Processed: {data.get('processed_files', 0)}",
                )
            else:
                self.log_test(
                    "Admin - Document Status", False, f"Status: {response.status_code}"
                )

            # Embedding bilgisi
            response = self.session.get(f"{self.base_url}/api/admin/embeddings/info")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Admin - Embeddings Info",
                    True,
                    f"Folder exists: {data.get('exists', False)}",
                )
            else:
                self.log_test(
                    "Admin - Embeddings Info", False, f"Status: {response.status_code}"
                )

        except Exception as e:
            self.log_test("Admin Endpoints", False, f"Error: {str(e)}")

    def test_search_functionality(self):
        """Arama fonksiyonalitesini test et"""
        try:
            # Doküman arama
            response = self.session.get(
                f"{self.base_url}/api/admin/documents/search",
                params={"q": "test", "type": "pdf"},
            )
            if response.status_code == 200:
                data = response.json()
                if "documents" in data and "total" in data:
                    self.log_test(
                        "Search - Document Search",
                        True,
                        f"{data['total']} sonuç bulundu",
                    )
                else:
                    self.log_test(
                        "Search - Document Search", False, "Invalid response format"
                    )
            else:
                self.log_test(
                    "Search - Document Search", False, f"Status: {response.status_code}"
                )

        except Exception as e:
            self.log_test("Search Functionality", False, f"Error: {str(e)}")

    def test_file_upload(self):
        """Dosya yükleme işlemini test et"""
        try:
            # Test dosyası oluştur
            test_content = """
            Test PDF İçeriği
            Bu bir test belgesidir.
            RAG sistemi için test amaçlıdır.
            """

            # Geçici test dosyası
            test_file_path = "/tmp/test_document.txt"
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(test_content)

            # Dosya yükleme testi
            with open(test_file_path, "rb") as f:
                files = {"files": ("test_document.txt", f, "text/plain")}
                response = self.session.post(
                    f"{self.base_url}/api/admin/upload", files=files
                )

            if response.status_code == 201:
                data = response.json()
                if "uploaded" in data and data["uploaded"]:
                    self.log_test(
                        "File Upload",
                        True,
                        f"Dosya yüklendi: {data['uploaded'][0]['saved_name']}",
                    )

                    # Yüklenen dosyayı temizle
                    filename = data["uploaded"][0]["saved_name"]
                    delete_response = self.session.delete(
                        f"{self.base_url}/api/admin/document/{filename}"
                    )
                    if delete_response.status_code == 200:
                        self.log_test("File Cleanup", True, "Test dosyası silindi")
                else:
                    self.log_test("File Upload", False, "No files uploaded")
            else:
                self.log_test("File Upload", False, f"Status: {response.status_code}")

            # Test dosyasını temizle
            if os.path.exists(test_file_path):
                os.remove(test_file_path)

        except Exception as e:
            self.log_test("File Upload", False, f"Error: {str(e)}")

    def test_error_handling(self):
        """Hata yönetimini test et"""
        try:
            # Geçersiz endpoint
            response = self.session.get(f"{self.base_url}/api/invalid-endpoint")
            if response.status_code == 404:
                self.log_test("Error - Invalid Endpoint", True, "404 döndü")
            else:
                self.log_test(
                    "Error - Invalid Endpoint", False, f"Status: {response.status_code}"
                )

            # Geçersiz dosya silme
            response = self.session.delete(
                f"{self.base_url}/api/admin/document/nonexistent.pdf"
            )
            if response.status_code == 404:
                self.log_test("Error - Delete Nonexistent", True, "404 döndü")
            else:
                self.log_test(
                    "Error - Delete Nonexistent",
                    False,
                    f"Status: {response.status_code}",
                )

            # Geçersiz JSON chat
            response = self.session.post(
                f"{self.base_url}/api/chat", data="invalid json"
            )
            if response.status_code in [400, 500]:
                self.log_test(
                    "Error - Invalid JSON", True, "Hata doğru şekilde yakalandı"
                )
            else:
                self.log_test(
                    "Error - Invalid JSON", False, f"Status: {response.status_code}"
                )

        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print("🚀 RAG Chatbot API Test Suite Başlatılıyor...")
        print(f"📍 Test URL: {self.base_url}")
        print("=" * 60)

        # API'nin çalışıp çalışmadığını kontrol et
        if not self.test_health_check():
            print("❌ API çalışmıyor! Lütfen önce API'yi başlatın:")
            print("   python api.py")
            return

        # Testleri çalıştır
        print("\n📋 Temel Testler:")
        self.test_chat_endpoint()

        print("\n👮 Admin Testleri:")
        self.test_admin_endpoints()

        print("\n🔍 Arama Testleri:")
        self.test_search_functionality()

        print("\n📁 Dosya İşleme Testleri:")
        self.test_file_upload()

        print("\n🚫 Hata Yönetimi Testleri:")
        self.test_error_handling()

        # Sonuç özeti
        self.print_summary()

    def print_summary(self):
        """Test sonuçlarının özetini yazdır"""
        print("\n" + "=" * 60)
        print("📊 TEST SONUÇ ÖZETİ")
        print("=" * 60)

        passed = sum(1 for r in self.test_results if r["success"])
        failed = len(self.test_results) - passed

        print(f"✅ Başarılı: {passed}")
        print(f"❌ Başarısız: {failed}")
        print(f"📊 Toplam: {len(self.test_results)}")
        print(f"🎯 Başarı Oranı: {(passed/len(self.test_results)*100):.1f}%")

        if failed > 0:
            print(f"\n❌ Başarısız Testler:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")


def main():
    """Ana test fonksiyonu"""
    tester = APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()