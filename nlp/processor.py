from typing import Dict

import numpy as np
from sentence_transformers import SentenceTransformer

from config import Config
from nlp.gpt_classifier import GPTBlackSwanClassifier


class EnhancedNewsProcessor:
    def __init__(self):
        self.gpt_classifier = GPTBlackSwanClassifier()
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.historical_context = []

    async def process_news_async(self, news_item: Dict) -> Dict:
        """异步处理新闻"""
        # 生成文本嵌入
        embedding = self._generate_embedding(news_item['content'])

        # 使用GPT分析
        gpt_result = await self.gpt_classifier.analyze_news_async(
            news_item['title'],
            news_item['content'],
            self._get_context()
        )

        # 计算意外性分数
        surprise_score = self._calculate_surprise_score(embedding)

        # 综合评分
        final_score = self._calculate_final_score(gpt_result, surprise_score)

        return {
            **news_item,
            'embedding': embedding,
            'gpt_analysis': gpt_result,
            'surprise_score': surprise_score,
            'final_black_swan_score': final_score,
            'is_black_swan': final_score >= 0.7
        }

    def _generate_embedding(self, text: str) -> np.ndarray:
        """生成文本嵌入向量"""
        return self.embedding_model.encode([text])[0]

    def _calculate_surprise_score(self, current_embedding: np.ndarray) -> float:
        """基于嵌入相似度计算意外性分数"""
        if not self.historical_context:
            return 1.0

        similarities = []
        for hist_embedding in self.historical_context[-100:]:  # 最近100条
            similarity = np.dot(current_embedding, hist_embedding) / (
                    np.linalg.norm(current_embedding) * np.linalg.norm(hist_embedding)
            )
            similarities.append(similarity)

        avg_similarity = np.mean(similarities) if similarities else 0
        return 1 - avg_similarity

    def _calculate_final_score(self, gpt_result: Dict, surprise_score: float) -> float:
        """计算最终的黑天鹅评分"""
        gpt_confidence = gpt_result.get('confidence_score', 0.5)

        # 加权综合评分：GPT置信度权重0.7，意外性权重0.3
        return (gpt_confidence * 0.7) + (surprise_score * 0.3)

    def _get_context(self) -> Dict:
        """获取历史上下文"""
        if not self.historical_context:
            return {}

        return {
            'recent_trends': f"最近分析了 {len(self.historical_context)} 条新闻",
            'avg_surprise_score': np.mean(
                [ctx.get('surprise_score', 0) for ctx in self.historical_context]) if self.historical_context else 0
        }

    def update_context(self, processed_news: Dict):
        """更新历史上下文"""
        self.historical_context.append({
            'title': processed_news['title'],
            'surprise_score': processed_news['surprise_score'],
            'black_swan_score': processed_news['final_black_swan_score'],
            'timestamp': processed_news.get('crawled_at')
        })

        # 保持上下文大小
        if len(self.historical_context) > 1000:
            self.historical_context = self.historical_context[-1000:]
