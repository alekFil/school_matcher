from typing import List, Tuple, Union

import numpy as np
from sklearn.metrics.pairwise import (
    cosine_similarity,
    euclidean_distances,
    manhattan_distances,
)

from app.utils.load_functions import load_resources
from app.utils.preprocess_functions import (
    abbr_preprocess_text,
    lemmatize_text,
    process_region,
    remove_short_words,
    remove_substrings,
    replace_numbers_with_text,
    simple_preprocess_text,
)

# Загрузка необходимых ресурсов
VECTORIZER = load_resources("vectorizer", "joblib")
REFERENCE_VEC = load_resources("reference_vec", "joblib")
REFERENCE_ID = load_resources("reference_id", "joblib")
REFERENCE_REGION = load_resources("reference_region", "joblib")
REFERENCE_NAME = load_resources("reference_name", "joblib")
ABBR_DICT = load_resources("abbreviations_dict", "joblib")
REGION_DICT = load_resources("region_dict", "joblib")
BLACKLIST_OPF = load_resources("blacklist_opf", "joblib")
STOP_WORDS_LIST = load_resources("stop_words_list", "joblib")


def calculate_similarity(
    x: np.ndarray, y: np.ndarray, method: str = "cosine"
) -> np.ndarray:
    """
    Вычисляет схожесть между двумя векторами с использованием указанного метода.

    Parameters
    ----------
    x : np.ndarray
        Первый вектор.
    y : np.ndarray
        Второй вектор.
    method : str, optional
        Метод вычисления схожести. Может быть "cosine", "euclidean"
        или "manhattan" (default is "cosine").

    Returns
    -------
    np.ndarray
        Массив схожестей.
    """
    if method == "cosine":
        return cosine_similarity(x, y)
    elif method == "euclidean":
        return -euclidean_distances(x, y)  # Инвертируем, чтобы максимизировать схожесть
    elif method == "manhattan":
        return -manhattan_distances(x, y)  # Инвертируем, чтобы максимизировать схожесть
    else:
        raise ValueError(f"Unknown similarity method: {method}")


def find_matches(
    x_vec: np.ndarray,
    x_region: np.ndarray,
    reference_id: np.ndarray,
    reference_vec: np.ndarray,
    reference_region: np.ndarray,
    top_k: int = 5,
    threshold: float = 0.9,
    filter_by_region: bool = True,
    empty_region: str = "all",
    similarity_method: str = "cosine",
) -> Tuple[List[List[Tuple[Union[int, None], float]]], List[np.ndarray]]:
    """
    Находит совпадения для заданных векторов с использованием
    различных методов схожести и фильтрации по регионам.

    Parameters
    ----------
    x_vec : np.ndarray
        Векторизованные названия школ.
    x_region : np.ndarray
        Регионы для векторов названий школ.
    reference_id : np.ndarray
        Идентификаторы референсных школ.
    reference_vec : np.ndarray
        Векторизованные референсные названия школ.
    reference_region : np.ndarray
        Регионы для референсных школ.
    top_k : int, optional
        Количество топ-совпадений, которые нужно вернуть (default is 5).
    threshold : float, optional
        Порог схожести для отбора совпадений (default is 0.9).
    filter_by_region : bool, optional
        Флаг для включения фильтрации по регионам (default is True).
    empty_region : str, optional
        Способ обработки, если в текущем регионе нет школ для сравнения (default is "all").
    similarity_method : str, optional
        Метод вычисления схожести (default is "cosine").

    Returns
    -------
    Tuple[List[List[Tuple[Union[int, None], float]]], List[np.ndarray]]
        Список совпадений и список для ручной обработки.
    """
    y_pred = []
    manual_review = []

    for i, x in enumerate(x_vec):
        # Фильтруем reference_vec и reference_id по текущему региону,
        # если включена фильтрация по регионам
        if filter_by_region:
            # Фильтруем reference_vec и reference_id по текущему региону
            current_region = x_region[i]
            region_mask = reference_region == current_region
            filtered_reference_vec = reference_vec[region_mask]
            filtered_reference_id = reference_id[region_mask]

            # Способ обработки, если в текущем регионе нет школ для сравнения
            if empty_region == "all":
                # Если в текущем регионе нет школ для сравнения, используем все школы
                if filtered_reference_vec.shape[0] == 0:
                    filtered_reference_vec = reference_vec
                    filtered_reference_id = reference_id
            else:
                if filtered_reference_vec.shape[0] == 0:
                    # Если в текущем регионе нет школ для сравнения,
                    # то помечаем на ручную обработку
                    manual_review.append(x)
                    top_matches = [(None, 0.0)] * top_k
                    y_pred.append(top_matches)
                    continue
        else:
            filtered_reference_vec = reference_vec
            filtered_reference_id = reference_id

        # Вычисляем выбранное расстояние
        similarities = calculate_similarity(
            x, filtered_reference_vec, method=similarity_method
        ).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        max_similarity = max(similarities)

        # Учитываем пороговое значение для различных методов
        if similarity_method == "cosine":
            if max_similarity < threshold:
                manual_review.append(x)
                top_matches = [(None, 0.0)] * top_k
            else:
                top_matches = [
                    (filtered_reference_id[i], similarities[i]) for i in top_indices
                ]
                if len(top_matches) < top_k:
                    top_matches += [(None, 0.0)] * (top_k - len(top_matches))
        else:  # Для других методов расстояний (евклидово и манхэттенское)
            if max_similarity > -threshold:  # Обратим внимание на инверсию
                manual_review.append(x)
                top_matches = [(None, 0.0)] * top_k
            else:
                top_matches = [
                    (filtered_reference_id[i], -similarities[i]) for i in top_indices
                ]
                if len(top_matches) < top_k:
                    top_matches += [(None, 0.0)] * (top_k - len(top_matches))

        y_pred.append(top_matches)

    return y_pred, manual_review


def predict(school_name: str) -> List[int]:
    """
    Предсказывает соответствия для заданного названия школы.

    Parameters
    ----------
    school_name : str
        Название школы.

    Returns
    -------
    List[int]
        Список id наиболее вероятных совпадений.
    """

    def preprocess_name(x: str) -> str:
        """
        Предобрабатывает название школы.

        Parameters
        ----------
        x : str
            Название школы.

        Returns
        -------
        str
            Предобработанное название школы.
        """
        x = simple_preprocess_text(x)
        x = replace_numbers_with_text(x)
        x = abbr_preprocess_text(x, ABBR_DICT, False, False, True, False)
        x = process_region(x, REGION_DICT)
        x = remove_substrings(x, BLACKLIST_OPF)
        x = lemmatize_text(x, STOP_WORDS_LIST)
        x = remove_short_words(x)
        return x

    def preprocess_region(x: str) -> str:
        """
        Предобрабатывает регион школы.

        Parameters
        ----------
        x : str
            Название школы.

        Returns
        -------
        str
            Регион школы.
        """
        x = simple_preprocess_text(x)
        x = replace_numbers_with_text(x)
        x = abbr_preprocess_text(x, ABBR_DICT, False, False, True, False)
        return process_region(x, REGION_DICT, return_region=True)

    vectorized_preprocess = np.vectorize(preprocess_name)
    vectorized_region = np.vectorize(preprocess_region)

    x = vectorized_preprocess(np.array([school_name]))
    region = vectorized_region(np.array([school_name]))

    # Векторизация текста
    x_vec = VECTORIZER.transform(x)

    y_pred, manual_review = find_matches(
        x_vec,
        region,
        REFERENCE_ID,
        REFERENCE_VEC,
        REFERENCE_REGION,
        top_k=5,
        threshold=0.00000001,
        filter_by_region=True,
        empty_region="all",  # is ignored if filter_by_region=False
        similarity_method="cosine",
    )

    # Преобразование numpy типов в стандартные Python типы и обработка None
    converted_results_list = [
        int(id_) if id_ is not None else None for id_, _ in y_pred[0]
    ]

    return converted_results_list
