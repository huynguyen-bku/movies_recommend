import ast
import json
import pandas as pd


def extract_info(data_str):
    try:
        list_data = [x.get('name', '').lower().strip() for x in ast.literal_eval(data_str)]
    except:
        return []
    return list_data


def preprocess_df(path_df: str, path_language: str, path_save: str):
    df_movies = pd.read_csv(path_df, low_memory=False)
    # genres
    df_movies['genres'] = df_movies['genres'].apply(extract_info)
    # df_movies['companies'] = df_movies['production_companies'].apply(extract_info)
    # countries
    df_movies['countries'] = df_movies['production_countries'].apply(extract_info)
    # release_date
    df_movies['release_date'] = pd.to_datetime(df_movies['release_date'], errors='coerce')
    df_movies.dropna(subset=['release_date'], inplace=True)
    # language
    with open(path_language, "r") as file:
        languages = json.load(file)
    df_movies["language"] = df_movies["original_language"].map(languages)
    # process string columns
    for ele_name in ["title", "overview", "language"]:
        df_movies[ele_name] = df_movies[ele_name].str.lower().str.strip()
    # feature
    columns = ["title", "genres", "countries", "language", "overview",
               "revenue", "budget", "adult", "runtime"]
    df_movies = df_movies[columns]
    df_movies.reset_index(drop=True, inplace=True)
    df_movies['id'] = df_movies.index
    df_movies.to_csv(path_save, index=False)

    return df_movies


if __name__ == "__main__":
    path_data = 'data/movies_metadata.csv'
    path_language = 'data/languages.json'
    path_save = "data/movies.csv"
    preprocess_df(path_df=path_data,
                  path_language=path_language,
                  path_save=path_save)
