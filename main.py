import os
import requests

from itertools import count

from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_vacancies_hh(search_text, page=0):
    url = 'https://api.hh.ru/vacancies'
    town_id = '1'
    vacancies_per_page = 100
    payload = {
        'text': search_text,
        'area': town_id,
        'only_with_salary': True,
        'page': page,
        'per_page': vacancies_per_page
        }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()

def predict_rub_salary_hh(vacancy):
    if not vacancy['salary']['currency'] == 'RUR':return
    return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])

def get_vacancies_statistic_hh(languages):
    vacancies_statistic = dict()
    for language in languages:
        salaries = []
        for page in count():
            vacancies = get_vacancies_hh(language, page)
            pages_number = vacancies['pages']
            for vacancy in vacancies['items']:
                salary = predict_rub_salary_hh(vacancy)
                if salary:
                    salaries.append(salary)
            if page == pages_number:
                break
            page += 1

        if salaries:
            average_salary = int(sum(salaries) / len(salaries))
        vacancies_statistic[language] = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': len(salaries),
            'average_salary': average_salary
            }
    return vacancies_statistic


def get_vacancies_sj(search_text, secret_key_sj, page):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': secret_key_sj}
    only_with_salary = True
    payload = {
        'keyword': search_text,
        'town': 'Москва',
        'catalogues': 'Разработка, программирование',
        'no_agreement': only_with_salary,
        'page': page
        }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()

def predict_rub_salary_sj(vacancy):
    if not vacancy['currency'] == 'rub': return
    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])

def get_vacancies_statisctic_sj(languages, secret_key_sj):
    vacancies_statistic = dict()
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
        vacancies_statistic[language] = {
            'vacancies_found': vacancies_at_page['total'],
            'vacancies_processed': len(salaries),
            'average_salary': average_salary
            }
    return vacancies_statistic

def predict_salary(salary_from, salary_to):
    if not salary_from:
        return salary_to * 0.8
    elif not salary_to:
        return salary_from * 1.2
    return (salary_from + salary_to) / 2

def get_vacancies_table(title, result, languages):
    vacancies_table_heading = [
        ['Language', 'Vacancies_found', 'Vacancies_processed', 'Average_salary']
        ]
    vacancies_table_body = []
    for language in languages:
        vacancies_table_body.append(
            [
                language,
                result[language]['vacancies_found'],
                result[language]['vacancies_processed'],
                result[language]['average_salary']
                ]
            )
    vacancies_data_table = vacancies_table_heading + vacancies_table_body
    vacancies_table = AsciiTable(vacancies_data_table, title)
    return vacancies_table.table

if __name__ == '__main__':
    load_dotenv()
    secret_key_sj = os.environ['SJ_SECRET_KEY']
    languages = ['Python', 'Java', 'Javascript', 'C#', 'Go', 'C++']

    vacancies_statistic_hh = get_vacancies_statistic_hh(languages)
    print(get_vacancies_table('HeadHunter Moscow', vacancies_statistic_hh, languages))

    vacancies_statistic_sj = get_vacancies_statisctic_sj(languages, secret_key_sj)
    print(get_vacancies_table('SuperJob Moscow', vacancies_statistic_sj, languages))
