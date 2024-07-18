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

VECTORIZER = load_resources("vectorizer", "joblib")
REFERENCE_VEC = load_resources("reference_vec", "joblib")
REFERENCE_ID = load_resources("reference_id", "joblib")
REFERENCE_REGION = load_resources("reference_region", "joblib")
REFERENCE_NAME = load_resources("reference_name", "joblib")
ABBR_DICT = load_resources("abbreviations_dict", "joblib")
REGION_DICT = load_resources("region_dict", "joblib")
BLACKLIST_OPF = load_resources("blacklist_opf", "joblib")
STOP_WORDS_LIST = load_resources("stop_words_list", "joblib")


def calculate_similarity(x, y, method="cosine"):
    if method == "cosine":
        return cosine_similarity(x, y)
    elif method == "euclidean":
        return -euclidean_distances(x, y)  # Инвертируем, чтобы максимизировать схожесть
    elif method == "manhattan":
        return -manhattan_distances(x, y)  # Инвертируем, чтобы максимизировать схожесть
    else:
        raise ValueError(f"Unknown similarity method: {method}")


def find_matches(
    x_vec,
    x_region,
    reference_id,
    reference_vec,
    reference_region,
    top_k=5,
    threshold=0.9,
    filter_by_region=True,
    empty_region="all",
    similarity_method="cosine",
):
    y_pred = []
    manual_review = []

    for i, x in enumerate(x_vec):
        # Фильтруем reference_vec и reference_id по текущему региону, если включена фильтрация по регионам
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
                    # Если в текущем регионе нет школ для сравнения, то помечаем на ручную обработку
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
            if max_similarity > -threshold:  # Обратите внимание на инверсию
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


def predict(school_name: str, region_name: str):
    def preprocess_name(x):
        x = simple_preprocess_text(x)
        x = replace_numbers_with_text(x)
        x = abbr_preprocess_text(x, ABBR_DICT, False, False, True, False)
        x = process_region(x, REGION_DICT)
        x = remove_substrings(x, BLACKLIST_OPF)
        x = lemmatize_text(x, STOP_WORDS_LIST)
        x = remove_short_words(x)
        return x

    def preprocess_region(x):
        x = simple_preprocess_text(x)
        x = replace_numbers_with_text(x)
        x = abbr_preprocess_text(x, ABBR_DICT, False, False, True, False)
        return process_region(x, REGION_DICT, return_region=True)

    vectorized_preprocess = np.vectorize(preprocess_name)
    vectorized_region = np.vectorize(preprocess_region)

    x = [school_name + ", " + region_name]
    x = vectorized_preprocess(np.array(x))
    region = vectorized_region(np.array(x))

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

    def get_name(id):
        if id is None:
            return None
        return str(REFERENCE_NAME[np.where(REFERENCE_ID == id)[0]][0])

    # Преобразование numpy типов в стандартные Python типы и обработка None
    converted_results = [
        {
            "id": int(id_) if id_ is not None else None,
            "score": float(score),
            "name": get_name(id_),
        }
        for id_, score in y_pred[0]
    ]

    return converted_results
