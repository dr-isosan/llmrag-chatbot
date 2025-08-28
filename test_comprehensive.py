#!/usr/bin/env python3
"""
Gelişmiş RAG Chatbot Test Suite
Bu dosya tüm sistemin kapsamlı testlerini yapar.
"""

import sys
import time
from typing import Dict, Any, List, Optional
from rag_chatbot import AdvancedRAGChatbot
from quer import validate_llm_connection, test_llm_quality
from config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSystemTester:
    """RAG sistemi için kapsamlı test sınıfı"""

    def __init__(self):
        self.test_results = []
        self.chatbot = None

    def log_test(
        self,
        test_name: str,
        success: bool,
        message: str = "",
        details: 'Optional[Dict[str, Any]]' = None,
    ):
        """Test sonucunu kaydet"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")

        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time(),
        }

        if details:
            result["details"] = details

        self.test_results.append(result)

    def test_system_requirements(self) -> bool:
        """Sistem gereksinimlerini test et"""
        print("\n🔧 Sistem Gereksinimlerini Test Ediliyor...")

        # LLM bağlantısı
        llm_status = validate_llm_connection()
        if llm_status.get("connected"):
            self.log_test(
                "LLM Connection",
                True,
                f"Model: {llm_status.get('target_model', 'Unknown')}",
            )
        else:
            self.log_test(
                "LLM Connection", False, llm_status.get("error", "Unknown error")
            )
            return False

        # LLM kalitesi
        quality_test = test_llm_quality()
        quality_score = quality_test["passed"] / quality_test["total"]

        self.log_test(
            "LLM Quality",
            quality_score >= 0.5,
            f"Passed: {quality_test['passed']}/{quality_test['total']}",
        )

        return llm_status.get("connected", False)

    def test_chatbot_initialization(self) -> bool:
        """Chatbot başlatma testleri"""
        print("\n🤖 Chatbot Başlatma Testleri...")

        try:
            self.chatbot = AdvancedRAGChatbot()
            self.log_test("Chatbot Init", True, "Chatbot başarıyla başlatıldı")
            return True
        except Exception as e:
            self.log_test("Chatbot Init", False, f"Başlatma hatası: {e}")
            return False

    def test_query_processing(self) -> bool:
        """Query işleme testleri"""
        print("\n📝 Query İşleme Testleri...")

        if not self.chatbot:
            self.log_test("Query Processing", False, "Chatbot başlatılmamış")
            return False

        test_queries = [
            {
                "query": "Sınav kuralları nelerdir?",
                "expected_category": "general",
                "min_confidence": 0.3,
            },
            {
                "query": "Kayıt işlemi nasıl yapılır?",
                "expected_category": "procedure",
                "min_confidence": 0.3,
            },
            {
                "query": "Mezuniyet için kaç kredi gerekir?",
                "expected_category": "quantitative",
                "min_confidence": 0.3,
            },
            {
                "query": "Sınav tarihleri ne zaman açıklanır?",
                "expected_category": "temporal",
                "min_confidence": 0.3,
            },
        ]

        success_count = 0

        for i, test_case in enumerate(test_queries, 1):
            try:
                result = self.chatbot.process_query(test_case["query"])

                # Kategori kontrolü
                detected_category = result.get("query_analysis", {}).get(
                    "category", "unknown"
                )
                category_match = detected_category == test_case["expected_category"]

                # Güven skoru kontrolü
                confidence = result.get("confidence", 0)
                confidence_ok = confidence >= test_case["min_confidence"]

                # Yanıt varlığı kontrolü
                response_exists = bool(result.get("response", "").strip())

                test_success = category_match and confidence_ok and response_exists

                self.log_test(
                    f"Query Test {i}",
                    test_success,
                    f"Kategori: {detected_category}, Güven: {confidence:.2f}",
                    details={
                        "query": test_case["query"],
                        "detected_category": detected_category,
                        "expected_category": test_case["expected_category"],
                        "confidence": confidence,
                        "response_length": len(result.get("response", "")),
                    },
                )

                if test_success:
                    success_count += 1

            except Exception as e:
                self.log_test(f"Query Test {i}", False, f"Hata: {e}")

        overall_success = success_count >= len(test_queries) * 0.6  # %60 başarı oranı
        self.log_test(
            "Query Processing Overall",
            overall_success,
            f"Başarılı: {success_count}/{len(test_queries)}",
        )

        return overall_success

    def test_retrieval_system(self) -> bool:
        """Retrieval sistemi testleri"""
        print("\n🔍 Retrieval Sistemi Testleri...")

        if not self.chatbot:
            self.log_test("Retrieval System", False, "Chatbot başlatılmamış")
            return False

        retriever = self.chatbot.retriever

        test_queries = [
            "sınav kuralları",
            "öğrenci kayıt",
            "mezuniyet şartları",
            "devamsızlık limiti",
        ]

        success_count = 0

        for i, query in enumerate(test_queries, 1):
            try:
                # Semantic search testi
                semantic_results = retriever.semantic_search(query, n_results=3)
                semantic_docs = semantic_results.get("documents", [[]])[0]

                # Keyword search testi
                keyword_results = retriever.keyword_search(query, n_results=3)

                # Hybrid search testi
                hybrid_results = retriever.hybrid_search(query, n_results=3)

                # Advanced retrieval testi
                advanced_results = retriever.advanced_retrieve(query, n_results=3)

                # Başarı kriterleri
                semantic_ok = len(semantic_docs) > 0
                keyword_ok = len(keyword_results) > 0
                hybrid_ok = len(hybrid_results) > 0
                advanced_ok = advanced_results.get("total_found", 0) > 0

                test_success = all([semantic_ok, keyword_ok, hybrid_ok, advanced_ok])

                self.log_test(
                    f"Retrieval Test {i}",
                    test_success,
                    f"S:{len(semantic_docs)} K:{len(keyword_results)} H:{len(hybrid_results)} A:{advanced_results.get('total_found', 0)}",
                    details={
                        "query": query,
                        "semantic_count": len(semantic_docs),
                        "keyword_count": len(keyword_results),
                        "hybrid_count": len(hybrid_results),
                        "advanced_count": advanced_results.get("total_found", 0),
                    },
                )

                if test_success:
                    success_count += 1

            except Exception as e:
                self.log_test(f"Retrieval Test {i}", False, f"Hata: {e}")

        overall_success = success_count >= len(test_queries) * 0.75  # %75 başarı oranı
        self.log_test(
            "Retrieval System Overall",
            overall_success,
            f"Başarılı: {success_count}/{len(test_queries)}",
        )

        return overall_success

    def test_response_quality(self) -> bool:
        """Yanıt kalitesi testleri"""
        print("\n📊 Yanıt Kalitesi Testleri...")

        if not self.chatbot:
            self.log_test("Response Quality", False, "Chatbot başlatılmamış")
            return False

        quality_queries = [
            {
                "query": "Sınav sistemi nasıl işler?",
                "min_relevance": 0.5,
                "min_clarity": 0.6,
                "min_overall": 0.4,
            },
            {
                "query": "Öğrenci kayıt süreci adımları nelerdir?",
                "min_relevance": 0.5,
                "min_clarity": 0.6,
                "min_overall": 0.4,
            },
        ]

        success_count = 0

        for i, test_case in enumerate(quality_queries, 1):
            try:
                result = self.chatbot.process_query(test_case["query"])
                evaluation = result.get("evaluation", {})

                relevance = evaluation.get("relevance_score", 0)
                clarity = evaluation.get("clarity_score", 0)
                overall = evaluation.get("overall_score", 0)

                relevance_ok = relevance >= test_case["min_relevance"]
                clarity_ok = clarity >= test_case["min_clarity"]
                overall_ok = overall >= test_case["min_overall"]

                test_success = relevance_ok and clarity_ok and overall_ok

                self.log_test(
                    f"Quality Test {i}",
                    test_success,
                    f"İlgililik: {relevance:.2f}, Netlik: {clarity:.2f}, Genel: {overall:.2f}",
                    details={
                        "query": test_case["query"],
                        "relevance_score": relevance,
                        "clarity_score": clarity,
                        "overall_score": overall,
                        "quality_level": result.get("quality_level", "Unknown"),
                    },
                )

                if test_success:
                    success_count += 1

            except Exception as e:
                self.log_test(f"Quality Test {i}", False, f"Hata: {e}")

        overall_success = (
            success_count >= len(quality_queries) * 0.5
        )  # %50 başarı oranı
        self.log_test(
            "Response Quality Overall",
            overall_success,
            f"Başarılı: {success_count}/{len(quality_queries)}",
        )

        return overall_success

    def test_edge_cases(self) -> bool:
        """Sınır durumları testleri"""
        print("\n⚠️ Sınır Durumları Testleri...")

        if not self.chatbot:
            self.log_test("Edge Cases", False, "Chatbot başlatılmamış")
            return False

        edge_cases = [
            {"query": "", "test_name": "Empty Query", "should_handle": True},
            {
                "query": "xyz123 asdf qwerty nonexistent",
                "test_name": "Nonsense Query",
                "should_handle": True,
            },
            {
                "query": "a" * 1000,  # Çok uzun sorgu
                "test_name": "Very Long Query",
                "should_handle": True,
            },
            {
                "query": "!@#$%^&*()",
                "test_name": "Special Characters",
                "should_handle": True,
            },
        ]

        success_count = 0

        for test_case in edge_cases:
            try:
                result = self.chatbot.process_query(test_case["query"])

                # Sistem çökmemeli ve bir yanıt döndürmeli
                has_response = bool(result.get("response", "").strip())
                error_handled = (
                    "error" not in result or result.get("confidence", 0) >= 0
                )

                test_success = has_response and error_handled

                self.log_test(
                    test_case["test_name"],
                    test_success,
                    f"Yanıt var: {has_response}, Hata yönetimi: {error_handled}",
                )

                if test_success:
                    success_count += 1

            except Exception as e:
                # Sınır durumlarında bile sistem çökmemeli
                self.log_test(test_case["test_name"], False, f"Beklenmeyen hata: {e}")

        overall_success = success_count >= len(edge_cases) * 0.75  # %75 başarı oranı
        self.log_test(
            "Edge Cases Overall",
            overall_success,
            f"Başarılı: {success_count}/{len(edge_cases)}",
        )

        return overall_success

    def generate_test_report(self) -> Dict[str, Any]:
        """Test raporu oluştur"""
        if not self.test_results:
            return {"error": "Hiç test çalıştırılmamış"}

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = passed_tests / total_tests if total_tests > 0 else 0

        # Kategori bazlı analiz
        categories = {}
        for result in self.test_results:
            category = result["test"].split()[0] if " " in result["test"] else "Other"
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0}
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["passed"] += 1

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": success_rate,
                "overall_status": "PASS" if success_rate >= 0.7 else "FAIL",
            },
            "categories": categories,
            "failed_tests": [r for r in self.test_results if not r["success"]],
            "recommendations": self.get_recommendations(success_rate, categories),
        }

        return report

    def get_recommendations(
        self, success_rate: float, categories: Dict[str, Any]
    ) -> List[str]:
        """Test sonuçlarına göre öneriler"""
        recommendations = []

        if success_rate < 0.5:
            recommendations.append(
                "❌ Sistem genelinde ciddi sorunlar var. Temel bileşenleri gözden geçirin."
            )
        elif success_rate < 0.7:
            recommendations.append(
                "⚠️ Bazı kritik sorunlar mevcut. Başarısız testleri analiz edin."
            )
        else:
            recommendations.append("✅ Sistem genel olarak iyi çalışıyor.")

        # Kategori bazlı öneriler
        for category, stats in categories.items():
            category_rate = (
                stats["passed"] / stats["total"] if stats["total"] > 0 else 0
            )
            if category_rate < 0.5:
                recommendations.append(
                    f"🔧 {category} bileşeninde iyileştirme gerekli."
                )

        return recommendations

    def run_all_tests(self) -> Dict[str, Any]:
        """Tüm testleri çalıştır"""
        print("🚀 RAG Sistemi Kapsamlı Test Süreci Başlatılıyor...\n")

        start_time = time.time()

        # Test sırası
        test_methods = [
            self.test_system_requirements,
            self.test_chatbot_initialization,
            self.test_query_processing,
            self.test_retrieval_system,
            self.test_response_quality,
            self.test_edge_cases,
        ]

        for test_method in test_methods:
            try:
                success = test_method()
                if not success and test_method.__name__ in [
                    "test_system_requirements",
                    "test_chatbot_initialization",
                ]:
                    print(f"\n❌ Kritik test başarısız: {test_method.__name__}")
                    print("⚠️ Sonraki testler atlanıyor.")
                    break
            except Exception as e:
                print(f"\n❌ Test metodu hatası {test_method.__name__}: {e}")

        end_time = time.time()

        # Rapor oluştur
        report = self.generate_test_report()
        report["execution_time"] = end_time - start_time

        return report


def main():
    """Ana test fonksiyonu"""
    tester = RAGSystemTester()

    try:
        report = tester.run_all_tests()

        print("\n" + "=" * 60)
        print("📊 TEST RAPORU")
        print("=" * 60)

        summary = report["summary"]
        print(f"Toplam Test: {summary['total_tests']}")
        print(f"Başarılı: {summary['passed_tests']}")
        print(f"Başarısız: {summary['failed_tests']}")
        print(f"Başarı Oranı: {summary['success_rate']:.1%}")
        print(f"Genel Durum: {summary['overall_status']}")
        print(f"Çalışma Süresi: {report['execution_time']:.2f} saniye")

        print("\n📋 ÖNERİLER:")
        for rec in report["recommendations"]:
            print(f"  {rec}")

        if report["failed_tests"]:
            print("\n❌ BAŞARISIZ TESTLER:")
            for failed in report["failed_tests"]:
                print(f"  - {failed['test']}: {failed['message']}")

        # Exit code
        sys.exit(0 if summary["overall_status"] == "PASS" else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Test süreci kullanıcı tarafından durduruldu.")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Test süreci hatası: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()