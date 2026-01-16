"""翻译Agent - 负责多语言翻译
支持百度翻译API / 有道翻译API / LLM翻译
"""
import os
import hashlib
import random
import httpx
from typing import Dict, Any, Optional
import json

from app.agents.base_agent import BaseAgent
from app.core.config import settings
from app.core.prompt_service import prompt_service


class TranslationAgent(BaseAgent):
    """翻译Agent，负责多语言翻译和语言检测"""
    
    # 语言代码映射
    LANG_MAP = {
        "中文": "zh", "chinese": "zh", "汉语": "zh",
        "英文": "en", "english": "en", "英语": "en",
        "日文": "jp", "japanese": "jp", "日语": "jp",
        "韩文": "kor", "korean": "kor", "韩语": "kor",
        "法文": "fra", "french": "fra", "法语": "fra",
        "德文": "de", "german": "de", "德语": "de",
        "俄文": "ru", "russian": "ru", "俄语": "ru",
        "西班牙文": "spa", "spanish": "spa", "西班牙语": "spa",
        "葡萄牙文": "pt", "portuguese": "pt",
        "意大利文": "it", "italian": "it",
        "阿拉伯文": "ara", "arabic": "ara",
        "泰文": "th", "thai": "th",
        "越南文": "vie", "vietnamese": "vie",
    }
    
    def __init__(self):
        super().__init__(
            name="TranslationAgent",
            description="负责多语言翻译、语言检测和本地化"
        )
        # 百度翻译API配置
        self.baidu_appid = getattr(settings, 'BAIDU_TRANSLATE_APPID', None) or os.getenv('BAIDU_TRANSLATE_APPID')
        self.baidu_secret = getattr(settings, 'BAIDU_TRANSLATE_SECRET', None) or os.getenv('BAIDU_TRANSLATE_SECRET')
        self.baidu_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行翻译任务
        
        Args:
            input_data: {
                "user_input": "用户输入",
                "parameters": {"target_lang": "目标语言"}
            }
        """
        user_input = input_data.get("user_input", "")
        parameters = input_data.get("parameters", {})
        
        return await self._translate(user_input, parameters)
    
    async def _translate(self, user_input: str, parameters: Dict) -> Dict[str, Any]:
        """执行翻译"""
        # 解析翻译请求
        parsed = await self._parse_translation_request(user_input, parameters)
        text_to_translate = parsed.get("text", user_input)
        target_lang = parsed.get("target_lang", "英文")
        source_lang = parsed.get("source_lang", "auto")
        
        # 转换语言代码
        target_code = self._get_lang_code(target_lang)
        source_code = self._get_lang_code(source_lang) if source_lang != "auto" else "auto"
        
        # 尝试使用百度翻译API
        if self.baidu_appid and self.baidu_secret:
            result = await self._baidu_translate(text_to_translate, source_code, target_code)
            if result.get("success"):
                return self._format_translation_result(result, text_to_translate, target_lang)
        
        # 回退到LLM翻译
        return await self._llm_translate(text_to_translate, target_lang)
    
    async def _baidu_translate(self, text: str, from_lang: str, to_lang: str) -> Dict[str, Any]:
        """使用百度翻译API"""
        try:
            salt = str(random.randint(32768, 65536))
            sign_str = self.baidu_appid + text + salt + self.baidu_secret
            sign = hashlib.md5(sign_str.encode()).hexdigest()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.baidu_url,
                    data={
                        "q": text,
                        "from": from_lang,
                        "to": to_lang,
                        "appid": self.baidu_appid,
                        "salt": salt,
                        "sign": sign,
                    }
                )
                
                data = response.json()
                
                if "trans_result" in data:
                    translated = "\n".join([item["dst"] for item in data["trans_result"]])
                    return {
                        "success": True,
                        "original": text,
                        "translated": translated,
                        "source_lang": data.get("from", from_lang),
                        "target_lang": to_lang,
                        "api": "baidu"
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("error_msg", "翻译失败")
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _llm_translate(self, text: str, target_lang: str) -> Dict[str, Any]:
        """使用LLM进行翻译"""
        system_prompt = f"""你是一个专业的翻译专家，精通多国语言。
请将用户提供的文本翻译成{target_lang}。

翻译要求：
1. 准确传达原文意思
2. 翻译结果自然、地道
3. 保持原文的语气和风格
4. 对于专业术语，提供准确的翻译

只需返回翻译结果，不需要额外解释。"""

        try:
            translated = await self.process_with_llm(text, system_prompt)
            
            return {
                "success": True,
                "original": text,
                "translated": translated.strip(),
                "source_lang": "auto",
                "target_lang": target_lang,
                "api": "llm"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"翻译失败: {str(e)}"
            }
    
    async def _parse_translation_request(self, user_input: str, parameters: Dict) -> Dict[str, Any]:
        """解析翻译请求"""
        # 如果已经有明确的参数
        if parameters.get("text") and parameters.get("target_lang"):
            return parameters
        
        # 使用LLM解析
        system_prompt = """从用户输入中提取翻译信息：
1. text: 需要翻译的文本
2. target_lang: 目标语言
3. source_lang: 源语言（如果明确指定）

返回JSON格式：
{
    "text": "要翻译的文本",
    "target_lang": "目标语言",
    "source_lang": "auto"
}

只返回JSON。"""
        
        try:
            response = await self.process_with_llm(user_input, system_prompt)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
        except:
            # 简单的启发式解析
            return self._heuristic_parse(user_input)
    
    def _heuristic_parse(self, user_input: str) -> Dict[str, Any]:
        """启发式解析翻译请求"""
        import re
        
        # 常见的翻译模式
        patterns = [
            (r"把[「「]?(.+?)[」」]?翻译成(.+)", lambda m: {"text": m.group(1), "target_lang": m.group(2).strip()}),
            (r"翻译成(.+?)[：:](.+)", lambda m: {"text": m.group(2).strip(), "target_lang": m.group(1).strip()}),
            (r"(.+)的(.+?)怎么说", lambda m: {"text": m.group(1), "target_lang": m.group(2)}),
            (r"(.+?)翻译[：:](.+)", lambda m: {"text": m.group(2).strip(), "target_lang": m.group(1).strip()}),
        ]
        
        for pattern, extractor in patterns:
            match = re.search(pattern, user_input)
            if match:
                return extractor(match)
        
        # 默认翻译成英文
        return {"text": user_input, "target_lang": "英文", "source_lang": "auto"}
    
    def _get_lang_code(self, lang_name: str) -> str:
        """获取语言代码"""
        lang_lower = lang_name.lower().strip()
        return self.LANG_MAP.get(lang_lower, "en")
    
    def _format_translation_result(self, result: Dict, original: str, target_lang: str) -> Dict[str, Any]:
        """格式化翻译结果"""
        translated = result.get("translated", "")
        api_used = result.get("api", "unknown")
        
        message = f"""🌐 **翻译结果**

**原文**：
> {original}

**{target_lang}**：
> {translated}

---
*翻译引擎: {api_used}*"""
        
        return {
            "success": True,
            "translation": {
                "original": original,
                "translated": translated,
                "target_lang": target_lang,
            },
            "message": message
        }
