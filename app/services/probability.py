import os
import json
import logging
from typing import Optional

import httpx

from app.models import University, Academic

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """\
Ты — эксперт по университетским приёмным кампаниям. 
Тебе дают профиль абитуриента и требования университета.
Твоя задача — оценить вероятность поступления от 1 до 99 (целое число).

Верни ТОЛЬКО валидный JSON без лишнего текста, строго по схеме:
{
  "probability": <integer 1-99>,
  "reasoning": "<краткое объяснение на русском, 1-2 предложения>"
}

Критерии оценки:
- GPA: сравни GPA абитуриента с минимальным GPA вуза
- SAT: сравни SAT абитуриента с минимальным SAT вуза
- IELTS/TOEFL: сравни языковые баллы с требованиями вуза
- Сложность вуза (color): red = очень сложный, yellow = средний, green = доступный
- Если данные отсутствуют — делай умеренно консервативную оценку
- probability 1-30: маловероятно, 31-60: средние шансы, 61-99: хорошие шансы
"""


def _build_user_message(uni: University, academic: Optional[Academic]) -> str:
    uni_info = {
        "university_name": uni.name,
        "country": uni.country,
        "difficulty_color": uni.color or "yellow",
        "difficulty_label": uni.label or "Средне",
        "requirements": {
            "min_gpa": uni.min_gpa,
            "min_sat": uni.min_sat,
            "min_ielts": uni.min_ielts,
            "min_toefl": uni.min_toefl,
        },
    }

    if academic:
        student_info = {
            "gpa": academic.gpa,
            "sat": academic.sat,
            "ielts": academic.ielts,
            "toefl": academic.toefl,
            "act": academic.act,
        }
    else:
        student_info = None

    return json.dumps(
        {"university": uni_info, "student": student_info},
        ensure_ascii=False,
        indent=2,
    )


def _fallback_probability(uni: University, academic: Optional[Academic]) -> float:
    """Локальный расчёт на случай недоступности OpenAI API."""
    if not academic:
        base = {"red": 15.0, "yellow": 40.0, "green": 70.0}
        return base.get(uni.color or "yellow", 40.0)

    scores = []

    if uni.min_gpa and academic.gpa:
        scores.append(min((academic.gpa / uni.min_gpa) * 60, 80))
    elif uni.min_gpa is None and academic.gpa:
        scores.append(70)

    if uni.min_sat and academic.sat:
        scores.append(min((academic.sat / uni.min_sat) * 55, 80))
    elif uni.min_sat is None:
        scores.append(65)

    if uni.min_ielts:
        if academic.ielts:
            scores.append(min((academic.ielts / uni.min_ielts) * 50, 75))
        elif academic.toefl:
            approx_ielts = academic.toefl / 120 * 9
            scores.append(min((approx_ielts / uni.min_ielts) * 50, 75))

    if not scores:
        return 40.0

    raw = sum(scores) / len(scores)
    multipliers = {"red": 0.55, "yellow": 0.80, "green": 1.05}
    raw *= multipliers.get(uni.color or "yellow", 0.80)

    return round(min(max(raw, 1.0), 99.0), 1)


async def calculate_probability_async(
    uni: University, academic: Optional[Academic]
) -> float:
    """
    Асинхронно рассчитывает вероятность поступления через GPT-4o-mini.
    При ошибке падает на локальный алгоритм.
    """
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY не задан — используется локальный расчёт")
        return _fallback_probability(uni, academic)

    user_message = _build_user_message(uni, academic)

    payload = {
        "model": MODEL,
        "temperature": 0.2,
        "max_tokens": 256,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(OPENAI_API_URL, json=payload, headers=headers)
            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        result = json.loads(content)

        probability = float(result["probability"])
        probability = round(min(max(probability, 1.0), 99.0), 1)

        logger.info(
            "GPT probability for '%s': %.1f | %s",
            uni.name,
            probability,
            result.get("reasoning", ""),
        )
        return probability

    except httpx.HTTPStatusError as e:
        logger.error("OpenAI HTTP error %s: %s", e.response.status_code, e.response.text)
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        logger.error("Ошибка парсинга ответа GPT: %s", e)
    except Exception as e:
        logger.error("Неожиданная ошибка при вызове OpenAI: %s", e)

    # Fallback на локальный алгоритм
    return _fallback_probability(uni, academic)


def calculate_probability(uni: University, academic: Optional[Academic]) -> float:
    """
    Синхронная обёртка — используется там, где нет async-контекста.
    Вызывает локальный алгоритм напрямую (без GPT).
    Для полноценного GPT-расчёта вызывай calculate_probability_async().
    """
    return _fallback_probability(uni, academic)