import json
from typing import Dict, List, Optional

import openai
from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_exponential

from config import Config


class GPTBlackSwanClassifier:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL
        self.system_prompt = self._create_system_prompt()

    def _create_system_prompt(self) -> str:
        """创建系统提示词，定义黑天鹅事件的判断标准"""
        return """你是一个专业的金融风险分析师，专门识别"黑天鹅"事件。根据纳西姆·塔勒布的理论，黑天鹅事件具有三个特征：
        1. 意外性（Unpredictable）：事件在常规预期之外，过去无法证明其发生的可能性
        2. 影响重大（High Impact）：事件会产生极端影响
        3. 事后可解释性（Retrospective Predictability）：事后人们会为它的发生编造理由，使其看起来可解释和可预测

        请严格根据以下标准分析新闻：
        - 评估事件的意外性和不可预测性
        - 评估事件的潜在影响范围和严重程度
        - 考虑事件对金融市场、经济体系、地缘政治的连锁反应
        - 判断是否具有系统性风险特征

        请以JSON格式回复，包含以下字段：
        {
            "is_black_swan": boolean,
            "confidence_score": float (0.0-1.0),
            "reasoning": string (详细的分析理由),
            "impact_areas": array of string (受影响的领域，如["financial_markets", "geopolitics", "technology"]),
            "risk_level": string ("low", "medium", "high", "extreme")
        }
        """

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_news_async(self, title: str, content: str, context: Optional[Dict] = None) -> Dict:
        """异步分析新闻是否为黑天鹅事件"""
        user_prompt = self._create_user_prompt(title, content, context)

        try:
            response = await acompletion(
                model=self.model,  # 例如 "openai/gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=Config.OPENAI_MAX_TOKENS,
                temperature=Config.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            return self._parse_response(result)

        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return self._get_fallback_response(title, content)

    def analyze_news_sync(self, title: str, content: str, context: Optional[Dict] = None) -> Dict:
        """同步分析新闻（用于非异步环境）"""
        import asyncio
        return asyncio.run(self.analyze_news_async(title, content, context))

    def _create_user_prompt(self, title: str, content: str, context: Optional[Dict]) -> str:
        """创建用户提示词"""
        prompt = f"""
        新闻标题: {title}
        新闻内容: {content[:2000]}  # 限制内容长度

        """

        if context:
            prompt += f"上下文信息: {json.dumps(context, ensure_ascii=False)}\n"

        prompt += "\n请分析这条新闻是否属于黑天鹅事件，并给出详细的分析。"
        return prompt

    def _parse_response(self, response_text: str) -> Dict:
        """解析GPT响应"""
        try:
            # 清理响应文本，确保是有效的JSON
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]

            result = json.loads(cleaned_text)

            # 验证必需字段
            required_fields = ['is_black_swan', 'confidence_score', 'reasoning']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            return result

        except (json.JSONDecodeError, ValueError) as e:
            print(f"解析GPT响应失败: {e}")
            print(f"原始响应: {response_text}")
            return self._get_fallback_response("", "")

    def _get_fallback_response(self, title: str, content: str) -> Dict:
        """备用的基于规则的响应"""
        # 简单的关键词匹配作为备用方案
        black_swan_keywords = [
            'black swan', 'unexpected', 'crisis', 'collapse', 'emergency',
            'market crash', 'economic shock', 'systemic risk', 'tail risk',
            'geopolitical risk', 'extreme event', 'unforeseen'
        ]

        text = f"{title} {content}".lower()
        keyword_count = sum(1 for keyword in black_swan_keywords if keyword in text)

        return {
            "is_black_swan": keyword_count > 2,
            "confidence_score": min(keyword_count / 5, 0.8),
            "reasoning": "Fallback analysis based on keyword matching",
            "impact_areas": ["general"],
            "risk_level": "medium" if keyword_count > 1 else "low"
        }

    def batch_analyze(self, news_items: List[Dict]) -> List[Dict]:
        """批量分析多条新闻"""
        results = []
        for item in news_items:
            result = self.analyze_news_sync(item['title'], item['content'])
            results.append({**item, **result})
        return results

if __name__ == "__main__":
    classifier = GPTBlackSwanClassifier()
    test_title = "全球金融市场突发大幅波动"
    test_content = "由于突发的地缘政治事件，全球主要金融市场出现剧烈波动，投资者恐慌情绪蔓延。"
    result = classifier.analyze_news_sync(test_title, test_content)
    print("分析结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))