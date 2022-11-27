import os
import requests

from itertools import count

from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_vacancies_hh(search_text, page=0):
    url = 'https://api.hh.ru/vacancies'
    payload = {
        'text': search_text,
        'area': '1',
        'only_with_salary': True,
        'page': page,
        'per_page': 100
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()

def predict_rub_salary_hh(vacancy):
    if vacancy['salary']['currency'] == 'RUR':
        salary_from = vacancy['salary']['from']
        salary_to = vacancy['salary']['to']
        return predict_salary(salary_from, salary_to)
    return None

def vacancy_statistics_hh(languages):
    result = dict()
    for language in languages:
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
    return result


def get_vacancies_sj(search_text, secret_key_sj, page):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': secret_key_sj}
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

def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        return predict_salary(salary_from, salary_to)
    return None

def vacancy_statisctics_sj(languages, secret_key_sj):
    result = dict()
    for language in languages:
        salaries = []
        for page in count():
            vacancies_at_page = get_vacancies_sj(language, secret_key_sj, page)
            for vacancy in vacancies_at_page['objects']:
                salary = predict_rub_salary_sj(vacancy)
                if salary:
                    salaries.append(salary)
            pages_more = vacancies_at_page['more']
            if not pages_more:
                break

        if salaries:
            average_salary = int(sum(salaries) / len(salaries))
        result[language] = {
            'vacancies_found': vacancies_at_page['total'],
            'vacancies_processed': len(salaries),
            'average_salary': average_salary
        }
    return result

def predict_salary(salary_from, salary_to):
    if not salary_from:
        return salary_to * 0.8
    elif not salary_to:
        return salary_from * 1.2
    return (salary_from + salary_to) / 2

def results_table(title, result, languages):
    table_heading = [
        ['Language', 'Vacancies_found', 'Vacancies_processed', 'Average_salary']
        ]
    table_body = []
    for language in languages:
        table_body.append(
            [
                language,
                result[language]['vacancies_found'],
                result[language]['vacancies_processed'],
                result[language]['average_salary']
                ]
            )
    table_data = table_heading + table_body
    table = AsciiTable(table_data, title)
    return table.table

if __name__ == '__main__':
    load_dotenv()
    secret_key_sj = os.environ['SJ_SECRET_KEY']
    languages = ['Python', 'Java', 'Javascript', 'C#', 'Go', 'C++']

    results_hh = vacancy_statistics_hh(languages)
    print(results_table('HeadHunter Moscow', results_hh, languages))

    results_sj = vacancy_statisctics_sj(languages, secret_key_sj)
    print(results_table('SuperJob Moscow', results_sj, languages))
