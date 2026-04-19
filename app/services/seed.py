from app.models import University, Opportunity
from app.database import SessionLocal
from datetime import datetime


def seed():
    db = SessionLocal()
    try:
        if db.query(University).count() > 0:
            return

        universities = [
            University(
                name="Harvard University", country="США", city="Кембридж",
                full_description="Один из самых престижных университетов мира, основан в 1636 году. Входит в Лигу плюща. Предлагает программы по праву, медицине, бизнесу, гуманитарным и точным наукам.",
                website="https://harvard.edu", ranking=1,
                min_gpa=3.9, min_sat=1500, min_ielts=7.0,
                label="Сложно", color="red",
                deadline="1 января 2026", deadline_date=datetime(2026, 1, 1),
            ),
            University(
                name="MIT", country="США", city="Кембридж",
                full_description="Массачусетский технологический институт — мировой лидер в области науки и технологий. Сильнейшие программы по инженерии, CS, физике и математике.",
                website="https://mit.edu", ranking=2,
                min_gpa=3.9, min_sat=1550, min_ielts=7.0,
                label="Сложно", color="red",
                deadline="1 января 2026", deadline_date=datetime(2026, 1, 1),
            ),
            University(
                name="University of Toronto", country="Канада", city="Торонто",
                full_description="Крупнейший исследовательский университет Канады. Входит в топ-25 мировых рейтингов. Сильные программы по медицине, праву и бизнесу.",
                website="https://utoronto.ca", ranking=18,
                min_gpa=3.5, min_sat=1300, min_ielts=6.5,
                label="Средне", color="yellow",
                deadline="1 февраля 2026", deadline_date=datetime(2026, 2, 1),
            ),
            University(
                name="University of British Columbia", country="Канада", city="Ванкувер",
                full_description="Один из ведущих университетов Канады. Красивый кампус на берегу океана. Известен программами по экологии, CS и бизнесу.",
                website="https://ubc.ca", ranking=34,
                min_gpa=3.3, min_sat=1200, min_ielts=6.5,
                label="Средне", color="yellow",
                deadline="15 января 2026", deadline_date=datetime(2026, 1, 15),
            ),
            University(
                name="Bocconi University", country="Италия", city="Милан",
                full_description="Лучший университет Европы по экономике и бизнесу. Международная атмосфера, сильные связи с корпоративным миром.",
                website="https://unibocconi.it", ranking=7,
                min_gpa=3.7, min_sat=1400, min_ielts=7.0,
                label="Сложно", color="red",
                deadline="15 января 2026", deadline_date=datetime(2026, 1, 15),
            ),
            University(
                name="Free University of Berlin", country="Германия", city="Берлин",
                full_description="Крупный исследовательский университет в столице Германии. Бесплатное образование для всех студентов, включая иностранных.",
                website="https://fu-berlin.de", ranking=98,
                min_gpa=3.0, min_sat=None, min_ielts=6.0,
                label="Реально", color="green",
                deadline="1 июня 2026", deadline_date=datetime(2026, 6, 1),
            ),
            University(
                name="University of Kassel", country="Германия", city="Кассель",
                full_description="Современный немецкий университет с сильными техническими и социальными программами. Низкий порог поступления для иностранных студентов.",
                website="https://uni-kassel.de", ranking=450,
                min_gpa=2.5, min_sat=None, min_ielts=5.5,
                label="Реально", color="green",
                deadline="15 июля 2026", deadline_date=datetime(2026, 7, 15),
            ),
            University(
                name="University of Siena", country="Италия", city="Сиена",
                full_description="Один из старейших университетов мира (основан в 1240 году). Уютный город Сиена, доступная стоимость жизни, сильные программы по медицине и праву.",
                website="https://unisi.it", ranking=601,
                min_gpa=2.8, min_sat=None, min_ielts=5.5,
                label="Реально", color="green",
                deadline="30 апреля 2026", deadline_date=datetime(2026, 4, 30),
            ),
            University(
                name="University of Melbourne", country="Австралия", city="Мельбурн",
                full_description="Ведущий университет Австралии и один из лучших в мире. Мультикультурный кампус, сильные программы по медицине, праву, бизнесу.",
                website="https://unimelb.edu.au", ranking=14,
                min_gpa=3.4, min_sat=1300, min_ielts=6.5,
                label="Средне", color="yellow",
                deadline="31 октября 2025", deadline_date=datetime(2025, 10, 31),
            ),
            University(
                name="Oregon State University", country="США", city="Корваллис",
                full_description="Государственный университет с сильными STEM-программами и доступной стоимостью обучения. Хорошая стипендиальная база для иностранных студентов.",
                website="https://oregonstate.edu", ranking=301,
                min_gpa=2.8, min_sat=1050, min_ielts=6.0,
                label="Реально", color="green",
                deadline="1 февраля 2026", deadline_date=datetime(2026, 2, 1),
            ),
        ]

        opportunities = [
            Opportunity(
                type="hackathon", title="UMUT MUN III",
                short_description="Образовательная конференция, направленная на развитие дипломатических навыков учащихся.",
                full_description="UMUT MUN — крупнейшая модель ООН в Центральной Азии. Участники работают в комитетах, представляют страны, ведут дебаты на английском языке. Развивает публичные выступления, критическое мышление и дипломатию.",
                organizer="UMUT", is_online=True,
                event_date="23 Марта", deadline="30 Сентября",
                deadline_date=datetime(2025, 9, 30),
            ),
            Opportunity(
                type="volunteering", title="PEAK DAY",
                short_description="Международная молодёжная конференция от AIESEC.",
                full_description="Peak Day — ежегодная конференция AIESEC, собирающая студентов и молодых профессионалов со всего мира. Воркшопы, нетворкинг, лидерские программы.",
                organizer="AIESEC", is_online=True,
                event_date="24 Января", deadline="24 Января",
                deadline_date=datetime(2026, 1, 24),
            ),
            Opportunity(
                type="hackathon", title="RISE UP",
                short_description="Образовательный форум для молодых лидеров.",
                full_description="Rise Up — образовательный форум, объединяющий молодых лидеров из 15+ стран. Темы: образование, технологии, предпринимательство. Включает питч-сессии и менторство.",
                organizer="Rise Up Foundation", is_online=False,
                event_date="23 Марта", deadline="30 Сентября",
                deadline_date=datetime(2025, 9, 30),
            ),
            Opportunity(
                type="internship", title="Google Summer Internship",
                short_description="Летняя стажировка в Google для студентов CS и смежных направлений.",
                full_description="Google предлагает 12-недельную оплачиваемую стажировку для студентов. Работа над реальными проектами, менторство от инженеров Google, relocation package.",
                organizer="Google", is_online=False,
                event_date="Июнь–Август 2026", deadline="15 Февраля 2026",
                deadline_date=datetime(2026, 2, 15),
            ),
            Opportunity(
                type="volunteering", title="UNICEF Volunteer Program",
                short_description="Глобальная волонтёрская программа UNICEF — помощь детям по всему миру.",
                full_description="Присоединяйтесь к миссии UNICEF. Волонтёры работают в сфере образования, здравоохранения и защиты прав детей. Онлайн и офлайн позиции в 150+ странах.",
                organizer="UNICEF", is_online=True,
                event_date="Весь год", deadline="Скоро",
                deadline_date=datetime(2026, 3, 1),
            ),
            Opportunity(
                type="internship", title="UNICEF Internship Programme",
                short_description="Стажировка в UNICEF — дедлайн скоро!",
                full_description="Трёхмесячная стажировка в штаб-квартире UNICEF (Нью-Йорк) или региональных офисах. Работа в области политики, коммуникаций, аналитики.",
                organizer="UNICEF", is_online=False,
                event_date="Апрель 2026", deadline="1 Марта 2026",
                deadline_date=datetime(2026, 3, 1),
            ),
        ]

        db.add_all(universities + opportunities)
        db.commit()
    finally:
        db.close()
