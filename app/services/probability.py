from app.models import University, Academic
from typing import Optional


def calculate_probability(uni: University, academic: Optional[Academic]) -> float:
    """
    Рассчитывает вероятность поступления (1–99%) на основе профиля.
    Учитывает GPA, SAT, IELTS/TOEFL и сложность вуза.
    """
    if not academic:
        # Нет данных — возвращаем нейтральное значение по сложности
        base = {"red": 15.0, "yellow": 40.0, "green": 70.0}
        return base.get(uni.color or "yellow", 40.0)

    scores = []

    # GPA
    if uni.min_gpa and academic.gpa:
        ratio = academic.gpa / uni.min_gpa
        scores.append(min(ratio * 60, 80))
    elif uni.min_gpa is None and academic.gpa:
        scores.append(70)

    # SAT
    if uni.min_sat and academic.sat:
        ratio = academic.sat / uni.min_sat
        scores.append(min(ratio * 55, 80))
    elif uni.min_sat is None:
        scores.append(65)

    # IELTS / TOEFL
    if uni.min_ielts:
        if academic.ielts:
            ratio = academic.ielts / uni.min_ielts
            scores.append(min(ratio * 50, 75))
        elif academic.toefl:
            # конвертируем TOEFL→IELTS приблизительно
            approx_ielts = academic.toefl / 120 * 9
            ratio = approx_ielts / uni.min_ielts
            scores.append(min(ratio * 50, 75))

    if not scores:
        return 40.0

    raw = sum(scores) / len(scores)

    # Коэффициент сложности
    multipliers = {"red": 0.55, "yellow": 0.80, "green": 1.05}
    raw *= multipliers.get(uni.color or "yellow", 0.80)

    return round(min(max(raw, 1.0), 99.0), 1)
