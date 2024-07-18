import itertools
import re

import nltk
import pymorphy3
from nltk.tokenize import word_tokenize
from num2words import num2words

# Загружаем необходимые ресурсы

nltk.download("punkt", quiet=True)

# Инициализация морфологического анализатора для русского языка
morph = pymorphy3.MorphAnalyzer()


def simple_preprocess_text(text):
    # Удаляем служебные символы (перенос строки, табуляция и т.д.)
    text = re.sub(r"[\n\t\r]", " ", text)

    # Удаление пунктуации
    text = re.sub(r"[^\w\s]", " ", text)

    # Удаление отдельных букв
    text = re.sub(r"\b[А-ЯЁа-яё]\b", " ", text)

    # Замена букв ё
    text = re.sub(r"[Ёё]", "е", text)

    # Регулярное выражение для поиска различных обозначений номера, включая случаи, когда за ними сразу идут цифры
    pattern = re.compile(r"\b(?:No|no|N|NO|№)(\d*)\b")

    # Замена найденных обозначений на "номер"
    text = pattern.sub(lambda match: f" {match.group(1)}", text)

    # Удаление лишних пробелов
    text = re.sub(r"\s+", " ", text)

    # Удаление пробелов в начале и в конце
    text = text.strip()

    # # Токенизация
    # words = word_tokenize(text.lower(), language="russian")

    # # Удаление стоп-слов
    # stop_words = set(stopwords.words("russian"))
    # filtered_words = [word for word in words if word not in stop_words]

    # return " ".join(filtered_words)
    return text


def replace_numbers_with_text(text):
    # Функция для замены чисел на их текстовое представление
    def num_to_text(match):
        num = match.group(0)
        return num2words(int(num), lang="ru")

    # Регулярное выражение для поиска чисел
    pattern = re.compile(r"\d+")

    # Замена чисел на текст
    return pattern.sub(num_to_text, text)


def abbr_preprocess_text(
    name,
    abbreviation_dict,
    output_list=False,
    unknown_answer=False,
    remove_unknown_abbr=False,
    remove_all_abbr=False,
):
    two_letter_prepositions = [
        " в ",
        " во ",
        " до ",
        " из ",
        " на ",
        " по ",
        " о ",
        " об ",
        " обо ",
        " у ",
    ]

    symbols = [" no", " NO", " No", "номер"]

    # Удаляем служебные символы (перенос строки, табуляция и т.д.)
    name = re.sub(r"[\n\t\r]", " ", name)

    # Создаем регулярное выражение для предлогов
    prepositions_pattern = (
        r"\b(?:" + "".join(two_letter_prepositions) + "".join(symbols) + r")\b"
    )

    # Заменяем все предлоги на пробел (предварительное решение вместо трудоемкого удаления стоп-слов)
    name = re.sub(prepositions_pattern, " ", name)

    # Удаление пунктуации
    name = re.sub(r"[^\w\s]", " ", name)

    # Удаление отдельных букв
    name = re.sub(r"\b[А-ЯЁа-яё]\b", " ", name)

    # Удаление букв ё
    name = re.sub(r"[Ёё]", "е", name)

    unknown_abbr = []
    # Находим аббревиатуры большими буквами и приводим их к нижнему регистру
    # Надо уточнить поиск неизвестных.
    # А если в конце аббревиатуры прописная буква?
    uppercase_abbreviations = re.findall(r"\b[А-ЯЁа-яё]+[а-яё]*[А-ЯЁ]+\b", name)
    for abbr in uppercase_abbreviations:
        abbr = abbr.lower()
        if abbr not in abbreviation_dict:
            unknown_abbr.append(abbr.upper())
            print(unknown_abbr)
            if remove_unknown_abbr:
                name = re.sub(r"\b" + re.escape(abbr.upper()) + r"\b", " ", name)

    # Удаление лишних пробелов
    name = re.sub(r"\s+", " ", name)

    # Удаление пробелов в начале и в конце
    name = name.strip()

    possible_replacements = []
    parts = name.lower().split()

    for part in parts:
        if part in abbreviation_dict:
            if not remove_all_abbr:
                replacements = abbreviation_dict[part]
                if isinstance(replacements, str):
                    replacements = [replacements]
                elif not output_list:
                    replacements = [""]
                possible_replacements.append(replacements)
            else:
                pass
        else:
            possible_replacements.append([part])

    # Генерируем все возможные комбинации
    all_combinations = list(itertools.product(*possible_replacements))

    # Формируем итоговые наименования
    final_phrases = [" ".join(combination).strip() for combination in all_combinations]

    if not output_list:
        final_phrases = final_phrases[0]

    if unknown_answer:
        return list(set(unknown_abbr))

    return final_phrases


def process_region(text, region_list, return_region=False):
    """
    Функция находит в тексте регион из списка регионов, удаляет его и возвращает
    либо новый текст без региона, либо регион в зависимости от флага return_region.

    :param text: исходный текст
    :param region_list: список регионов для поиска
    :param return_region: если True, возвращает найденный регион, иначе возвращает текст без региона
    :return: либо новый текст без региона, либо найденный регион
    """
    for region in region_list:
        # Используем регулярное выражение для точного поиска региона
        pattern = re.compile(r"\b" + re.escape(region) + r"\b", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            found_region = match.group(0)
            new_text = pattern.sub("", text).strip()
            return found_region if return_region else new_text
    return None if return_region else text


def remove_substrings(input_string, substrings):
    for substring in substrings:
        input_string = input_string.replace(substring, "").strip()
    return input_string


def process_cities(text, region_list, return_city=False):
    for cities_list in region_list.values():
        for city in cities_list:
            # Используем регулярное выражение для точного поиска региона
            pattern = re.compile(r"\b" + re.escape(city) + r"[а-я]*\b", re.IGNORECASE)
            match = pattern.search(text)
            if match:
                found_city = match.group(0)
                new_text = pattern.sub("", text).strip()
                return found_city if return_city else new_text
    return None if return_city else text


def lemmatize_text(text, stop_words_list):
    # Токенизация
    words = word_tokenize(text.lower(), language="russian")

    # Лемматизация
    lemmatized_words = [morph.parse(word)[0].normal_form for word in words]

    # Удаление стоп-слов
    filtered_words = [word for word in lemmatized_words if word not in stop_words_list]

    return " ".join(filtered_words)


def remove_short_words(text):
    words = text.split()  # разбиваем текст на слова
    filtered_words = [
        word for word in words if len(word) > 2
    ]  # фильтруем слова длиннее двух символов
    return " ".join(filtered_words)  # объединяем отфильтрованные слова в строку
