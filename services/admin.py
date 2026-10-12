"""{
    "email": "ahmad@example.com",
    "password": "StrongPassword123"
}

{
//   "username": "Akhmad",
//   "email": "akhmad@mail.ru",
//   "password": "AdminPassword123"
}


Обычный пользователь
{
  "username": "student2",
  "email": "student2@main.ru",
  "password": "StudentPassword123"
}

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYWI5YzUxYy1hZTY2LTRmZmYtYjIzNS0zMTdiZmExOTcwOWIiLCJyb2xlIjoidXNlciIsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjE3OTE1MzM3MzIsImV4cCI6MTc5MTUzNTUzMn0.BJuhnr__r6VyC8LdaFzG_lF3mTBF2WbTsFcp8Y3lS9o",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYWI5YzUxYy1hZTY2LTRmZmYtYjIzNS0zMTdiZmExOTcwOWIiLCJyb2xlIjoidXNlciIsInR5cGUiOiJyZWZyZXNoIiwiaWF0IjoxNzkxNTMzNzMyLCJleHAiOjE3OTIxMzg1MzJ9.VfKMaWFubMrmLDLRNJD7Vb1QTTHb6Rs5ZZV-6m-oEBg",
  "token_type": "bearer"
}

{
  "id": "2d04d784-177c-40aa-a420-411ab00d92bb",
  "username": "Akhmad",
  "email": "akhmad@mail.ru",
  "role": "user",
  "is_active": true,
  "created_at": "2026-10-09T06:48:44.573836Z"
}

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZDA0ZDc4NC0xNzdjLTQwYWEtYTQyMC00MTFhYjAwZDkyYmIiLCJyb2xlIjoiYWRtaW4iLCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzkxNTI4NzczLCJleHAiOjE3OTE1MzA1NzN9.EQ0_ytop3pI6uqV1RYtk4MmmBl3i-PRw3OcunhXyPSM",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZDA0ZDc4NC0xNzdjLTQwYWEtYTQyMC00MTFhYjAwZDkyYmIiLCJyb2xlIjoiYWRtaW4iLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc5MTUyODc3MywiZXhwIjoxNzkyMTMzNTczfQ.DgyGpm7X2FSeNk-FH37GEAGb3Oy2uxRj3GhE7bjUlBo",
  "token_type": "bearer"
}


КАТЕГОРИЯ
{
  "id": "1ddd8995-00d1-4ed0-8b36-c16910afe41c",
  "name": "База Python",
  "slug": "baza-python"
}

КУРС
{
  "id": "c3ec1457-056c-4b8f-a9ce-190046ca9154",
  "title": "Python с нуля",
  "description": "Курс Python для начинающих разработчиков",
  "level": "beginner",
  "is_published": true,
  "created_at": "2026-10-09T07:01:49.763626Z",
  "updated_at": "2026-10-09T07:01:49.763626Z",
  "modules": []
}

МОДУЛЬ
{
  "id": "8acb143b-84cf-4ccb-b664-b0e9ca3b9e39",
  "course_id": "c3ec1457-056c-4b8f-a9ce-190046ca9154",
  "title": "База Python",
  "description": "Базовые конструкции языка Python",
  "position": 1,
  "topics": []
},
{
  "id": "aa389057-e7f5-49b0-9aea-d64a126e944f",
  "course_id": "c3ec1457-056c-4b8f-a9ce-190046ca9154",
  "title": "Управляющие конструкции",
  "description": "Условия и циклы Python",
  "position": 2,
  "topics": []
}

ТЕМА
{
  "id": "93f18ee7-3b64-42f1-bc5f-9969bdc84c32",
  "module_id": "8acb143b-84cf-4ccb-b664-b0e9ca3b9e39",
  "title": "Переменные в Python",
  "description": "Переменные, правила именования и присваивание значений",
  "position": 1,
  "required_tasks_count": 3,
  "required_test_score": 70,
  "is_published": true
},

{
  "id": "d85540e5-aa34-40f0-a8e0-5301ee05388e",
  "module_id": "8acb143b-84cf-4ccb-b664-b0e9ca3b9e39",
  "title": "Типы данных Python",
  "description": "int, float, str, bool",
  "position": 2,
  "required_tasks_count": 4,
  "required_test_score": 70,
  "is_published": true
}

СТАТЬЯ
{
  "id": "818321b7-f4c9-4e24-a6f6-d2d24c3ee2bc",
  "topic_id": "93f18ee7-3b64-42f1-bc5f-9969bdc84c32",
  "title": "Переменные в Python",
  "slug": "peremennye-v-python",
  "content": "# Переменные в Python\n\nПеременная — это имя, связанное со значением.\n\n```python\nname = \"Ahmad\"\nage = 29\n```\n\nВ Python тип переменной определяется автоматически.",
  "is_published": true,
  "created_at": "2026-10-09T07:24:03.711700Z",
  "updated_at": "2026-10-09T07:24:03.711700Z",
  "category": {
    "id": "1ddd8995-00d1-4ed0-8b36-c16910afe41c",
    "name": "База Python",
    "slug": "baza-python"
  }
}

МАТЕРИАЛ
{
  "id": "650d474e-d231-452d-b63a-4852fbc5d4f2",
  "topic_id": "93f18ee7-3b64-42f1-bc5f-9969bdc84c32",
  "title": "Официальная документация Python",
  "description": "Официальная документация языка Python",
  "material_type": "documentation",
  "url": "https://docs.python.org/3/"
},

{
  "id": "107d8246-dbe1-470c-a448-1d8a4f611e61",
  "topic_id": "93f18ee7-3b64-42f1-bc5f-9969bdc84c32",
  "title": "Видео по переменным Python",
  "description": "Дополнительное видео для закрепления темы",
  "material_type": "video",
  "url": "https://www.youtube.com/"
},

{
  "id": "071d89fa-028e-4528-96c7-148c805a8220",
  "topic_id": "93f18ee7-3b64-42f1-bc5f-9969bdc84c32",
  "title": "Шпаргалка Python",
  "description": "Краткая шпаргалка по базовому синтаксису",
  "material_type": "pdf",
  "url": "https://example.com/python-cheatsheet.pdf"
}

ЗАДАНИЕ 
{
  "id": "a0bccefe-0363-4d5f-9bce-da1d7c69e8e5",
  "topic_id": "93f18ee7-3b64-42f1-bc5f-9969bdc84c32",
  "title": "Квадрат числа",
  "description": "Напишите функцию square(n), которая возвращает квадрат переданного числа.",
  "difficulty": "easy",
  "task_type": "write_function",
  "starter_code": "def square(n):\n    # ваш код\n    pass",
  "is_published": true,
  "created_at": "2026-10-09T18:22:37.282185Z",
  "updated_at": "2026-10-09T18:22:37.282185Z",
  "test_cases": [],
  "options": []
},

{
  "id": "3c3d2df3-a8d7-4275-bf32-24a976a1bf58",
  "topic_id": "93f18ee7-3b64-42f1-bc5f-9969bdc84c32",
  "title": "Тип числа",
  "description": "Какой тип имеет значение 5 в Python?",
  "difficulty": "easy",
  "task_type": "multiple_choice",
  "starter_code": null,
  "is_published": true,
  "created_at": "2026-10-09T18:48:17.138738Z",
  "updated_at": "2026-10-09T18:48:17.138738Z",
  "test_cases": [],
  "options": []
}"""