import os
import requests

from dotenv import load_dotenv


load_dotenv()

def get_vacancies_hh(search_text, page=0):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'text': search_text,
        'area': '1',
        'only_with_salary': True,
        'page': page,
        'per_page': 100
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def predict_salary(salary_from, salary_to):
    if not salary_from:
        return salary_to * 0.8
    elif not salary_to:
        return salary_from * 1.2
    return (salary_from + salary_to) / 2

def predict_rub_salary_hh(vacancy):
    if vacancy['salary']['currency'] == 'RUR':
        salary_from = vacancy['salary']['from']
        salary_to = vacancy['salary']['to']
        return predict_salary(salary_from, salary_to)
    return None

def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        return predict_salary(salary_from, salary_to)
    return None


languages = ['Python', 'Java', 'Javascript', 'C#', 'Go', 'C++']
for language in languages:
    result = dict()
    vacancies = get_vacancies_hh(language)
    page = 0
    pages_number = vacancies['pages']
    salaries = []

    while page < pages_number:
        vacancies_at_page = get_vacancies_hh(language, page)
        for vacancy in vacancies_at_page['items']:
            salary = predict_rub_salary_hh(vacancy)
            if salary:
                salaries.append(salary)
        page += 1

    average_salary = int(sum(salaries) / len(salaries))
    result[language] = {
        'vacancies_found': vacancies['found'],
        'vacancies_processed': len(salaries),
        'average_salary': average_salary
    }
    
    print(language, result[language])
# res = sorted(result, key=lambda x: result[x]['average_salary'])