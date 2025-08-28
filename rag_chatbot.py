import chromadb
from sentence_transformers import SentenceTransformer
from quer import ask_local_llm, temizle_yanit
from config import config
from query_processor import QueryProcessor
from hybrid_retriever import HybridRetriever
from evaluator import ResponseEvaluator
import logging
import re
from typing import Dict, List, Any, Optional

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedRAGChatbot:
    """Gelişmiş RAG Chatbot sistemi"""

    def __init__(self, chroma_path: str = "./chroma"):
        self.retriever = HybridRetriever(chroma_path)
        self.query_processor = QueryProcessor()
        self.evaluator = ResponseEvaluator()

        logger.info("🤖 Gelişmiş RAG Chatbot başlatıldı!")

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Kullanıcı sorgusunu kapsamlı şekilde işle"""
        try:
            # 1. Query preprocessing
            processed_query = self.query_processor.process_query(user_query)
            logger.info(f"📝 İşlenmiş sorgu kategorisi: {processed_query['category']}")

            # 2. Advanced retrieval
            retrieval_result = self.retriever.advanced_retrieve(
                user_query, n_results=config.DEFAULT_N_RESULTS
            )

            if not retrieval_result["results"]:
                return self._handle_no_results(user_query)

            # 3. Filter by similarity threshold
            filtered_results = self.retriever.filter_by_similarity_threshold(
                retrieval_result["results"]
            )

            if not filtered_results:
                return self._handle_low_similarity(
                    user_query, retrieval_result["results"]
                )

            # 4. Context preparation
            context_info = self._prepare_context(filtered_results, processed_query)

            # 5. Generate response
            response_data = self._generate_response(
                user_query, context_info, processed_query
            )

            # 6. Evaluate response quality
            evaluation = self._evaluate_response(
                response_data["response"],
                user_query,
                context_info["sources"],
                context_info["documents"],
            )

            # 7. Prepare final result
            # Sadece gerçekten kullanılan ilk source'u döndür (en yüksek skorlu)
            result = {
                "response": response_data["response"],
                "sources": context_info["sources"][:1],  # İlk source (en alakalı)
                "confidence": evaluation["overall_score"],
                "quality_level": evaluation["quality_level"],
                "query_analysis": processed_query,
                "retrieval_info": {
                    "total_found": len(retrieval_result["results"]),
                    "after_filtering": len(filtered_results),
                    "best_score": (
                        filtered_results[0]["combined_score"] if filtered_results else 0
                    ),
                },
                "evaluation": evaluation,
            }

            return result

        except Exception as e:
            logger.error(f"❌ Query işleme hatası: {e}")
            return self._handle_error(user_query, str(e))

    def _prepare_context(
        self, results: List[Dict[str, Any]], processed_query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieval sonuçlarından context hazırla"""

        context_parts = []
        sources = []  # Set yerine list - sıralamayı koru
        documents = []
        user_query = processed_query.get('original_query', processed_query.get('query', ''))

        for i, result in enumerate(results[: config.DEFAULT_N_RESULTS], 1):
            doc = result["document"]
            metadata = result.get("metadata", {})
            score = result.get("combined_score", 0)

            # Document relevans kontrolü - alakasız dökümanları filtrele
            if not self._is_document_relevant_to_query(doc, user_query):
                continue

            # Document preprocessing
            clean_doc = self._clean_document_for_context(doc)
            documents.append(clean_doc)

            # Source tracking - sıralı ve tekrarsız
            source_file = metadata.get("source_file", f"Belge_{i}")
            if source_file not in sources:  # Duplicate check
                sources.append(source_file)

            # Context formatting
            context_parts.append(
                {
                    "index": i,
                    "content": clean_doc,
                    "source": source_file,
                    "score": score,
                    "chunk_index": metadata.get("chunk_index", 0),
                }
            )

        # Generate rich context
        formatted_context = self._format_context_for_llm(context_parts, processed_query)

        return {
            "formatted_context": formatted_context,
            "sources": sources,  # Artık list olarak döndür
            "documents": documents,
            "context_parts": context_parts,
        }

    def _clean_document_for_context(self, document: str) -> str:
        """Dokümanı context için temizle"""
        # Fazla boşlukları temizle
        clean_doc = " ".join(document.split())

        # Çok uzun dokümanları kısalt
        words = clean_doc.split()
        if (
            len(words) > config.MAX_CONTEXT_LENGTH // 5
        ):  # Yaklaşık kelime başına 5 karakter
            clean_doc = " ".join(words[: config.MAX_CONTEXT_LENGTH // 5]) + "..."

        return clean_doc

    def _is_document_relevant_to_query(self, document: str, user_query: str) -> bool:
        """Dökümanın sorguyla alakalı olup olmadığını kontrol et"""
        doc_lower = document.lower()
        
        # Genel anahtar kelime kontrolü
        query_keywords = self._extract_query_keywords(user_query)
        if not query_keywords:
            return True  # Anahtar kelime yoksa tüm dökümanları al
            
        # En az bir anahtar kelime geçmeli
        keyword_matches = sum(1 for keyword in query_keywords if keyword in doc_lower)
        return keyword_matches > 0

    def _format_context_for_llm(
        self, context_parts: List[Dict[str, Any]], processed_query: Dict[str, Any]
    ) -> str:
        """LLM için context'i formatla"""

        context_lines = []

        for part in context_parts:
            source_info = f"[{part['source']}]"
            content = part["content"]
            score_info = f"(Uygunluk: {part['score']:.2f})"

            context_lines.append(
                f"{part['index']}. {source_info} {content} {score_info}"
            )

        return "\n\n".join(context_lines)

    def _generate_response(
        self,
        user_query: str,
        context_info: Dict[str, Any],
        processed_query: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Gelişmiş prompt ile yanıt üret"""

        # Query kategorisine göre özelleştirilmiş prompt
        specialized_instructions = self._get_specialized_instructions(
            processed_query["category"]
        )

        # Tek soruya odaklanan prompt oluştur
        focused_system_prompt = config.SYSTEM_PROMPT + "\n" + specialized_instructions + """

ÖNEMLI: Sadece kullanıcının şu anda sorduğu soruya cevap ver. Önceki sorular veya konularla ilgili bilgi verme.
Bu sorguya özgü ve kesin bir yanıt ver. Başka konulara değinme."""

        # Ana prompt oluştur
        prompt = config.RAG_PROMPT_TEMPLATE.format(
            system_prompt=focused_system_prompt,
            question=user_query,
            context=context_info["formatted_context"],
        )

        # LLM'den yanıt al
        raw_response = ask_local_llm(prompt, model=config.LLM_MODEL)
        clean_response = temizle_yanit(raw_response)

        # Yanıt post-processing - tek soruya odaklanarak
        processed_response = self._post_process_response(
            clean_response, context_info["sources"], user_query
        )

        return {
            "response": processed_response,
            "raw_response": raw_response,
            "prompt_used": prompt,
        }

    def _get_specialized_instructions(self, query_category: str) -> str:
        """Query kategorisine göre özel talimatlar"""
        instructions = {
            "procedure": "\nProsedür sorularında adım adım açıklama yap. Sıralı işlemler ver.",
            "temporal": "\nTarih ve zaman bilgilerini kesin olarak belirt. 'yaklaşık' gibi belirsiz ifadeler kullanma.",
            "quantitative": "\nSayısal bilgileri tam olarak ver. Belirsizlik varsa bunu açıkça belirt.",
            "definition": "\nTanımları net ve anlaşılır şekilde yap. Örnekler ver.",
            "explanation": "\nSebep-sonuç ilişkilerini açıkla. Mantıklı gerekçeler sun.",
            "location": "\nYer bilgilerini spesifik olarak belirt.",
            "general": "\nKapsamlı ve düzenli bir açıklama yap.",
        }

        return instructions.get(query_category, instructions["general"])

    def _post_process_response(self, response: str, sources: List[str], user_query: str = None) -> str:
        """Yanıtı son işleme tabi tut"""

        # Kaynak bilgilerini temizle - LLM'den gelen kaynak referanslarını kaldır
        import re
        
        # Daha kapsamlı kaynak referansı temizleme
        # "Kaynak:" ile başlayan tüm kısımları temizle
        response = re.sub(r'\s*Kaynak:\s*\[.*?\].*?$', '', response, flags=re.IGNORECASE | re.MULTILINE)
        response = re.sub(r'\s*Kaynak:\s*.*?\.pdf.*?$', '', response, flags=re.IGNORECASE | re.MULTILINE)
        response = re.sub(r'\s*Kaynak:\s*.*?\.docx.*?$', '', response, flags=re.IGNORECASE | re.MULTILINE)
        response = re.sub(r'\s*Kaynak belge:\s*.*?$', '', response, flags=re.IGNORECASE | re.MULTILINE)
        
        # Köşeli parantez içindeki dosya referanslarını temizle
        response = re.sub(r'\s*\[.*?\.pdf\].*?$', '', response, flags=re.IGNORECASE | re.MULTILINE)
        response = re.sub(r'\s*\[.*?\.docx\].*?$', '', response, flags=re.IGNORECASE | re.MULTILINE)
        response = re.sub(r'\s*\[Anasayfa.*?\].*?$', '', response, flags=re.IGNORECASE | re.MULTILINE)
        
        # "......" ile biten kısımları temizle
        response = re.sub(r'\.{3,}.*?$', '', response, flags=re.MULTILINE)
        
        # Satır sonundaki gereksiz boşlukları temizle
        response = re.sub(r'\s+$', '', response, flags=re.MULTILINE)
        
        # Çok kısa yanıtları genişlet
        if len(response) < config.MIN_ANSWER_LENGTH:
            response += " Bu konuda daha detaylı bilgi için ilgili belgeleri inceleyebilirsiniz."

        return response.strip()

    def _filter_response_for_single_query(self, response: str, user_query: str) -> str:
        """Yanıtı tek soruya odaklayacak şekilde filtrele"""
        
        # Önce alakasız ifadeleri temizle
        response = self._remove_irrelevant_phrases(response, user_query)
        
        # Eğer yanıt çok kısa kaldıysa, LLM'den gelen orijinal yanıtı kullan
        if len(response.strip()) < 50:
            return response
        
        # Kullanıcının sorusundaki anahtar kelimeleri çıkar
        query_keywords = self._extract_query_keywords(user_query)
        
        # Yanıtı cümlelere böl (nokta, ünlem, soru işaretiyle)
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]  # Boş cümleleri temizle
        
        filtered_sentences = []
        
        # İlk iki cümleyi her zaman dahil et (genellikle doğru cevap)
        if sentences:
            filtered_sentences.extend(sentences[:2])
        
        # Diğer cümleleri relevans kontrolünden geçir
        for sentence in sentences[2:]:
            if self._is_sentence_relevant_to_query(sentence, query_keywords, user_query):
                filtered_sentences.append(sentence)
            else:
                # İlgisiz cümle bulunduğunda dur (çoklu konu yanıtını önle)
                break
        
        # Cümleleri doğru şekilde birleştir
        if filtered_sentences:
            filtered_response = '. '.join(filtered_sentences)
            if not filtered_response.endswith('.'):
                filtered_response += '.'
        else:
            filtered_response = response  # Fallback
        
        return filtered_response.strip()

    def _extract_query_keywords(self, query: str) -> list:
        """Sorgudan anahtar kelimeleri çıkar"""
        # Türkçe stop words
        stop_words = {'ve', 'ile', 'için', 'de', 'da', 'bir', 'bu', 'şu', 'o', 'ben', 'sen', 'biz', 'siz', 'onlar',
                     'nasıl', 'ne', 'nedir', 'kim', 'nerede', 'neden', 'niçin', 'hangi', 'kaç', 'ne zaman'}
        
        words = query.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords

    def _is_sentence_relevant_to_query(self, sentence: str, query_keywords: list, user_query: str) -> bool:
        """Cümlenin sorguyla alakalı olup olmadığını kontrol et"""
        sentence_lower = sentence.lower()
        
        # Anahtar kelime match kontrolü
        keyword_matches = sum(1 for keyword in query_keywords if keyword in sentence_lower)
        
        # Eğer hiç anahtar kelime yoksa alakasız
        return keyword_matches > 0

    def _remove_irrelevant_phrases(self, response: str, user_query: str) -> str:
        """Alakasız ifadeleri temizle"""
        
        # Genel alakasız başlangıçları temizle
        irrelevant_starts = [
            r'^[^.]*belgede[^.]*kurallar[^.]*\.',
            r'^[^.]*ancak[^.]*\.',
            r'^[^.]*eğer[^.]*\.'
        ]
        
        for pattern in irrelevant_starts:
            response = re.sub(pattern, '', response, flags=re.IGNORECASE)
        
        # Çoklu boşlukları ve nokta hatalarını düzelt
        response = re.sub(r'\s+', ' ', response)
        response = re.sub(r'\.+', '.', response)
        response = re.sub(r'\s*\.\s*', '. ', response)
        
        # Başında/sonunda gereksiz boşluk ve nokta temizle
        response = response.strip(' .')
        
        # Eğer cümle noktayla bitmiyorsa ekle
        if response and not response.endswith('.'):
            response += '.'
            
        return response

    def _evaluate_response(
        self, response: str, query: str, sources: List[str], documents: List[str]
    ) -> Dict[str, Any]:
        """Yanıt kalitesini değerlendir"""
        return self.evaluator.evaluate_response(response, query, sources, documents)

    def _handle_no_results(self, query: str) -> Dict[str, Any]:
        """Sonuç bulunamadığında"""
        return {
            "response": config.FALLBACK_RESPONSE,
            "sources": [],
            "confidence": 0.0,
            "quality_level": "Bilgi Yok",
            "query_analysis": self.query_processor.process_query(query),
            "retrieval_info": {"total_found": 0, "after_filtering": 0, "best_score": 0},
            "evaluation": {
                "overall_score": 0.0,
                "improvement_suggestions": ["Daha spesifik soru sorun"],
            },
        }

    def _handle_low_similarity(
        self, query: str, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Düşük benzerlik skorlarında"""
        best_score = results[0]["combined_score"] if results else 0

        response = (
            f"Bu konuda kesin bilgi bulunamadı. "
            f"En yakın benzerlik skoru: {best_score:.2f}. "
            f"Daha spesifik bir soru sormayı deneyebilirsiniz."
        )

        return {
            "response": response,
            "sources": [],
            "confidence": best_score,
            "quality_level": "Düşük Güven",
            "query_analysis": self.query_processor.process_query(query),
            "retrieval_info": {
                "total_found": len(results),
                "after_filtering": 0,
                "best_score": best_score,
            },
            "evaluation": {
                "overall_score": 0.2,
                "improvement_suggestions": ["Sorguyu yeniden formüle edin"],
            },
        }

    def _handle_error(self, query: str, error_msg: str) -> Dict[str, Any]:
        """Hata durumunda"""
        return {
            "response": f"Üzgünüm, sorunuzu işlerken bir hata oluştu: {error_msg}",
            "sources": [],
            "confidence": 0.0,
            "quality_level": "Hata",
            "error": error_msg,
            "evaluation": {"overall_score": 0.0},
        }

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Conversation summary - now delegated to external conversation manager"""
        return {"total_queries": 0, "avg_confidence": 0.0, "recent_queries": []}


def run_interactive_chatbot():
    """Interaktif chatbot'u çalıştır"""
    chatbot = AdvancedRAGChatbot()

    print("\n🤖 Gelişmiş RAG Chatbot başlatıldı!")
    print("💡 Komutlar: 'exit' (çıkış), 'history' (geçmiş), 'help' (yardım)\n")

    while True:
        try:
            user_input = input("Kullanıcı: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                summary = chatbot.get_conversation_summary()
                print(
                    f"\nBot: Görüşmek üzere! Toplam {summary['total_queries']} soru sordunuz."
                )
                print(f"Ortalama güven skoru: {summary['avg_confidence']:.2f}")
                break

            elif user_input.lower() == "history":
                summary = chatbot.get_conversation_summary()
                print(f"\n📊 Konuşma Özeti:")
                print(f"Toplam soru: {summary['total_queries']}")
                print(f"Ortalama güven: {summary['avg_confidence']:.2f}")
                if summary["recent_queries"]:
                    print("Son sorular:", summary["recent_queries"])
                continue

            elif user_input.lower() == "help":
                print("\n🔧 Yardım:")
                print("- Normal sorularınızı yazabilirsiniz")
                print("- 'history' komutu konuşma geçmişini gösterir")
                print("- 'exit' komutu chatbot'tan çıkar")
                print("- Daha kesin cevaplar için spesifik sorular sorun")
                continue

            if not user_input:
                continue

            # Process query
            result = chatbot.process_query(user_input)

            # Display response
            print(f"\nBot: {result['response']}")

            # Display quality info (opsiyonel)
            print(
                f"\n📊 Güven: {result['confidence']:.2f} | Kalite: {result['quality_level']}"
            )
            if result.get("sources"):
                print(f"📚 Kaynaklar: {', '.join(result['sources'][:3])}")

            print()  # Boş satır

        except KeyboardInterrupt:
            print("\nBot: Görüşmek üzere!")
            break
        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")
            continue


if __name__ == "__main__":
    run_interactive_chatbot()


def get_answer(question: str) -> str:
    """Basit API fonksiyonu - batch_ask.py için"""
    try:
        chatbot = AdvancedRAGChatbot()
        result = chatbot.process_query(question)
        
        # Kaynak bilgisini ekle
        response = result['response']
        if result.get('sources'):
            sources = ', '.join(result['sources'][:2])  # İlk 2 kaynağı al
            response += f"\n\nKullanılan kaynak: {sources}"
        
        return response
    except Exception as e:
        return f"Hata oluştu: {str(e)}"