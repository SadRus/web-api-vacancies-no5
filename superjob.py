import os
import requests

from itertools import count

from dotenv import load_dotenv

def predict_salary(salary_from, salary_to):
    if not salary_from:
        return salary_to * 0.8
    elif not salary_to:
        return salary_from * 1.2
    return (salary_from + salary_to) / 2

def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        return predict_salary(salary_from, salary_to)
    return None


def get_vacancies_sj(search_text, page=0):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': os.environ['SUPERJOB_KEY']}
    payload = {
        'keyword': search_text,
        'town': 'Москва',
        'catalogues': 'Разработка, программирование',
        'no_agreement': 1,
        'page': page
        }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


load_dotenv()

languages = ['Python', 'Java', 'Javascript', 'C#', 'Golang', 'C++']
result = dict()
for language in languages:
    salaries = []
    pages_more = True
    for page in count():
        if not pages_more:
            break
        vacancies_at_page = get_vacancies_sj(language, page)
        for vacancy in vacancies_at_page['objects']:
            salary = predict_rub_salary_sj(vacancy)
            salaries.append(salary)
        pages_more = vacancies_at_page['more']

    salaries = [i for i in salaries if i]
    if salaries:
        average_salary = int(sum(salaries) / len(salaries))
    result[language] = {
        'vacancies_found': vacancies_at_page['total'],
        'vacancies_processed': len(salaries),
        'average_salary': average_salary
    }

    print(language, result[language])
