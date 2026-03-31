from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _ask(message: str) -> str:
    res = client.post('/chat', json={'message': message, 'language': 'en'})
    assert res.status_code == 200
    return res.json()['answer'].lower()


def test_recruiter_consistency_regression_suite():
    cases = []

    intro_q = [
        'Present yourself in 4-5 lines.',
        'Introduce yourself briefly.',
        'Tell me about yourself as a candidate.',
        'Who are you?',
        'Short self introduction please.',
        'Give me your profile summary.'
    ]
    for q in intro_q:
        cases.append((q, ['ai engineer', 'sissi']))

    exp_q = [
        'What professional experience do you have?',
        'What work experience do you have?',
        'What roles did you work in?',
        'Tell me your job history.',
        'Did you work before SISSI?',
        'Share your experience timeline.'
    ]
    for q in exp_q:
        cases.append((q, ['sissi', 'institut curie']))

    internship_q = [
        'Do you have internship experience?',
        'Do you have alternance experience?',
        'Did you do an M1 internship?',
        'Any stage or alternance background?',
        'Have you worked in apprenticeship mode?',
        'Internship and alternance details?'
    ]
    for q in internship_q:
        cases.append((q, ['m1', 'm2', 'institut curie']))

    contract_q = [
        'What contract types are you looking for?',
        'Are you looking for CDI or CDD?',
        'What is your contract preference?',
        'Do you target full-time permanent contracts?',
        'Are you looking for internship positions?',
        'Contract type?'
    ]
    for q in contract_q:
        cases.append((q, ['cdi', 'cdd']))

    edu_q = [
        'What is your education?',
        'Bachelor?',
        'Master and bachelor details?',
        'What degrees do you have?',
        'Tell me your academic background.',
        'Where did you study?'
    ]
    for q in edu_q:
        cases.append((q, ['master', 'bachelor']))

    pub_q = [
        'Any publication from Institut Curie?',
        'Do you have a paper?',
        'Is there a manuscript from your Curie work?',
        'Published article status?',
        'Any scientific publication in progress?',
        'Tell me about your Curie manuscript.'
    ]
    for q in pub_q:
        cases.append((q, ['manuscript', 'lifex']))

    hire_q = [
        'Why should we hire you?',
        'Why hire you for an AI engineer role?',
        'Give me your hiring value proposition.',
        'What makes you a strong hire?',
        'Why are you a good fit?',
        'Convince me to hire you.'
    ]
    for q in hire_q:
        cases.append((q, ['deployable', 'backend']))

    skills_q = [
        'Do you have LangChain experience?',
        'Any experience in knowledge graphs?',
        'Do you have Kubernetes experience?',
        'Have you used FastAPI?',
        'Experience with RAG?',
        'Do you know pgvector?'
    ]
    for q in skills_q:
        cases.append((q, ['yes']))

    # 48 baseline + 12 extra variants = 60
    extra_q = [
        ('Who are you as an engineer?', ['ai engineer']),
        ('What is your bachelor degree?', ['bachelor', 'liu']),
        ('Are you open to CDD?', ['cdd']),
        ('Do you have internship and alternance both?', ['m1', 'm2']),
        ('Paper status from Curie?', ['manuscript']),
        ('How do you present your profile?', ['sissi', 'institut curie']),
        ('Do you have experience with model context protocol?', ['yes']),
        ('Do you have experience with Neo4j?', ['yes']),
        ('Do you have experience with LangGraph?', ['yes']),
        ('Do you have experience with Spark?', ['yes']),
        ('Why should a product team hire you?', ['product', 'backend']),
        ('Education summary in one answer.', ['master', 'bachelor']),
    ]
    cases.extend(extra_q)

    assert len(cases) >= 60

    for question, required_tokens in cases:
        answer = _ask(question)
        for token in required_tokens:
            assert token in answer, f"Missing token '{token}' for question: {question}\nAnswer: {answer}"
