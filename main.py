import requests
import os
from itertools import count
from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_stat_to_most_popular_language_hh(languages=[]):
    vacancies_stat = dict()
    for language in languages:
        query = f'Программист {language}'
        response = get_vacancies_from_hh(query)
        vacancies_found, salaries = response
        salaries = get_salaries_hh(salaries)
        vacancies_stat[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(salaries),
            'average_salary': get_mean_estimated_salary(salaries),
        }

    return vacancies_stat


def get_vacancies_from_hh(text):
    url = 'https://api.hh.ru/vacancies'
    vacancies = []
    moscow_id = 1
    days = 30
    for page in count(0):
        params = {
            'area': moscow_id,
            'text': text,
            'page': page,
            'period': days,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        response = response.json()
        vacancies.extend(response['items'])

        last_page = response['pages'] - 1
        if page == last_page:
            break

    vacancies_found = response['found']

    return vacancies_found, vacancies


def get_salaries_hh(vacancies):
    processed_vacancies = []
    for vacancy in vacancies:
        salary = get_salary_from_hh(vacancy)
        if salary:
            processed_salary = predict_salaries(salary)
            processed_vacancies.append(processed_salary)
    return processed_vacancies


def get_salary_from_hh(vacancy):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        salary = {
            'from': vacancy['salary']['from'],
            'to': vacancy['salary']['to']
        }
        return salary


def get_vacancies_from_superjob(secret_key, keywords=''):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    vacancies = []
    moscow_id = 4
    it_vacancies_catalog_id = 48
    for page in count(0):
        params = {
            'town': moscow_id,
            'catalogues': it_vacancies_catalog_id,
            'page': page,
            'keywords': ['keys', keywords]
        }
        data = {
            'X-Api-App-Id': secret_key,
        }
        response = requests.get(url, params=params, headers=data)
        response.raise_for_status()
        response = response.json()
        vacancies.extend(response['objects'])
        if not response['more']:
            break

    vacancies_found = response['total']

    return vacancies_found, vacancies


def get_salaries_superjob(vacancies):
    processed_vacancies = []
    for vacancy in vacancies:
        salary = get_salary_from_superjob(vacancy)
        if salary:
            processed_salary = predict_salaries(salary)
            processed_vacancies.append(processed_salary)
    return processed_vacancies

def get_salary_from_superjob(vacancy):
    if vacancy['currency'] == 'rub':
        salary = {
            'from': vacancy['payment_from'],
            'to': vacancy['payment_to']
        }
        return salary


def get_stat_to_most_popular_language_superjob(secret_key, languages=[]):
    vacancies_stat = dict()

    for language in languages:
        keywords = f'Программист {language}'
        response = get_vacancies_from_superjob(secret_key, keywords=keywords)
        vacancies_found, salaries = response
        salaries = get_salaries_superjob(salaries)
        vacancies_stat[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(salaries),
            'average_salary': get_mean_estimated_salary(salaries),
        }

    return vacancies_stat

def get_mean_estimated_salary(salaries):
    if salaries:
        salaries = [salary for salary in salaries if salary is not None]
        summ_salaries = sum(salaries)
        len_salaries = len(salaries)

        mean_salary = int(summ_salaries / len_salaries)

        return mean_salary

def predict_salaries(salary):
    estimated_salary = None

    if salary['from'] and salary['to']:
        estimated_salary = (salary['from'] + salary['to']) / 2
    elif salary['from']:
        estimated_salary = salary['from'] * 1.2
    elif salary['to']:
        estimated_salary = salary['to'] * 0.8

    return estimated_salary

def create_vacancies_stat_table(statistics, title=''):
    table_data = [['Язык программирования',
                   'Вакансий найдено',
                   'Вакансий обработано',
                   'Средняя зарплата']]

    for language, language_statistics in statistics.items():
        row = [
            language,
            language_statistics['vacancies_found'],
            language_statistics['vacancies_processed'],
            language_statistics['average_salary']
        ]

        table_data.append(row)

    table = AsciiTable(table_data, title)
    return table.table


def main():
    load_dotenv()
    secret_key = os.getenv('SUPERJOB_TOKEN')
    most_popular_languages = [
        'javascript',
        'java',
        'python',
        'ruby',
        'php',
        'c++',
        'c#',
        'go',
        'objective-c',
        'scala',
        'swift'
    ]
    statistics_sj = get_stat_to_most_popular_language_superjob(
        secret_key=secret_key,
        languages=most_popular_languages
    )

    statistics_hh = get_stat_to_most_popular_language_hh(
        languages=most_popular_languages
    )

    sj_table = create_vacancies_stat_table(statistics_sj, title='SuperJob Moscow')
    hh_table = create_vacancies_stat_table(statistics_hh, title='HeadHunter Moscow')
    print(sj_table)
    print(hh_table)


if __name__ == "__main__":
    main()
