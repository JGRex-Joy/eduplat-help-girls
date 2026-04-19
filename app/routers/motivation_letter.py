from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import MotivationLetterRequest, MotivationLetterResponse
from app.auth import get_current_user
import os
import json

router = APIRouter(prefix="/motivation-letter", tags=["Motivation Letter"])

SYSTEM_PROMPT = """Ты — эксперт по приёмным комиссиям университетов. Оцени мотивационное письмо абитуриента.

Верни ТОЛЬКО валидный JSON (без markdown, без пояснений) строго в формате:
{
  "score": <число от 1 до 10>,
  "summary": "<краткое общее резюме на русском>",
  "strengths": ["<сильная сторона 1>", "<сильная сторона 2>"],
  "weaknesses": ["<слабая сторона 1>", "<слабая сторона 2>"],
  "suggestions": ["<совет 1>", "<совет 2>", "<совет 3>"]
}

Критерии оценки:
- 1–4: Слабое письмо (нет структуры, нет мотивации, клише)
- 5–8: Хорошее письмо (есть структура, есть мотивация, но можно улучшить)
- 9–10: Отличное письмо (конкретные примеры, чёткая мотивация, уникальность)

Отвечай на русском языке."""


def get_label_color(score: int):
    if score <= 4:
        return "Можно лучше", "red"
    elif score <= 8:
        return "Хорошо", "yellow"
    else:
        return "Отлично", "green"


@router.post("/analyze", response_model=MotivationLetterResponse)
def analyze_letter(
    data: MotivationLetterRequest,
    user: User = Depends(get_current_user),
):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        # Мок-ответ если нет ключа (для разработки)
        return MotivationLetterResponse(
            score=6,
            label="Хорошо",
            color="yellow",
            summary="Письмо имеет базовую структуру, но требует доработки для выделения на фоне других кандидатов.",
            strengths=[
                "Есть чёткое введение с указанием цели",
                "Выражена личная заинтересованность в специальности",
            ],
            weaknesses=[
                "Отсутствуют конкретные достижения и примеры из опыта",
                "Используются клишированные фразы",
            ],
            suggestions=[
                "Добавьте конкретные примеры проектов или достижений",
                "Объясните, почему именно этот университет и программа",
                "Покажите как ваш опыт соответствует требованиям программы",
            ],
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Мотивационное письмо:\n\n{data.text}"},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        score = int(parsed["score"])
        label, color = get_label_color(score)

        return MotivationLetterResponse(
            score=score,
            label=label,
            color=color,
            summary=parsed["summary"],
            strengths=parsed["strengths"],
            weaknesses=parsed["weaknesses"],
            suggestions=parsed["suggestions"],
        )

    except json.JSONDecodeError:
        raise HTTPException(500, "Ошибка обработки ответа ИИ. Попробуйте снова.")
    except Exception as e:
        raise HTTPException(500, f"Ошибка анализа: {str(e)}")
