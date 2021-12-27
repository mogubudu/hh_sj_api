import requests
import os
from itertools import count
from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_hh_language_stat(languages=[]):
    vacancies_stat = dict()
    for language in languages:
        query = f'Программист {language}'
        vacancies_found, salaries = get_vacancies_from_hh(query)
        salaries = predict_hh_salaries(salaries)
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


def predict_hh_salaries(vacancies):
    processed_vacancies = []
    for vacancy in vacancies:
        if (vacancy['salary'] and
                vacancy['salary']['currency'] == 'RUR'):

            processed_salary = predict_salaries(vacancy['salary']['from'],
                                                vacancy['salary']['to'])
            processed_vacancies.append(processed_salary)
    return processed_vacancies


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
        headers = {
            'X-Api-App-Id': secret_key,
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        response = response.json()
        vacancies.extend(response['objects'])
        if not response['more']:
            break

    vacancies_found = response['total']

    return vacancies_found, vacancies


def predict_superjob_salaries(vacancies):
    processed_vacancies = []
    for vacancy in vacancies:
        if vacancy['currency'] == 'rub':
            processed_salary = predict_salaries(vacancy['payment_from'],
                                                vacancy['payment_to'])
            processed_vacancies.append(processed_salary)
    return processed_vacancies


def get_superjob_language_stat(secret_key, languages=[]):
    vacancies_stat = dict()

    for language in languages:
        keywords = f'Программист {language}'
        vacancies_found, salaries = get_vacancies_from_superjob(secret_key, keywords=keywords)
        salaries = predict_superjob_salaries(salaries)
        vacancies_stat[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(salaries),
            'average_salary': get_mean_estimated_salary(salaries),
        }

    return vacancies_stat


def get_mean_estimated_salary(salaries):
    salaries = [salary for salary in salaries if salary]
    if salaries:
        summ_salaries = sum(salaries)
        len_salaries = len(salaries)

        mean_salary = int(summ_salaries / len_salaries)

        return mean_salary


def predict_salaries(salary_from, salary_to):
    estimated_salary = None

    if salary_from and salary_to:
        estimated_salary = (salary_from + salary_to) / 2
    elif salary_from:
        estimated_salary = salary_from * 1.2
    elif salary_to:
        estimated_salary = salary_to * 0.8

    return estimated_salary


def create_vacancies_stat_table(statistics, title=''):
    table = [['Язык программирования',
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

        table.append(row)

    table = AsciiTable(table, title)
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
    sj_statistics = get_superjob_language_stat(
        secret_key=secret_key,
        languages=most_popular_languages
    )

    hh_statistics = get_hh_language_stat(
        languages=most_popular_languages
    )

    sj_table = create_vacancies_stat_table(sj_statistics,
                                           title='SuperJob Moscow')
    hh_table = create_vacancies_stat_table(hh_statistics,
                                           title='HeadHunter Moscow')
    print(sj_table)
    print(hh_table)


if __name__ == "__main__":
    main()
