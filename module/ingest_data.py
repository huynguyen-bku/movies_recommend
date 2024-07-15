import json
import pandas as pd
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from constant import OPENAI_KEY


def create_dict_mapping(df_movies):
    # genres
    df_movies['genres'] = df_movies['genres'].apply(eval)
    exploded_genres = df_movies.explode('genres')
    genre_dict = exploded_genres.groupby('genres')['id'].apply(list).to_dict()
    genre_dict = {key: list(set(value)) for key, value in genre_dict.items()}
    # countries
    df_movies['countries'] = df_movies['countries'].apply(eval)
    exploded = df_movies.explode('countries')
    countries_dict = exploded.groupby('countries')['id'].apply(list).to_dict()
    countries_dict = {key: list(set(value)) for key, value in countries_dict.items()}
    # original_language
    language_dict = exploded.groupby('language')['id'].apply(list).to_dict()
    language_dict = {key: list(set(value)) for key, value in language_dict.items()}
    return genre_dict, countries_dict, language_dict


def dict_to_document(data_dict: dict):
    list_documents = []
    for x in data_dict.items():
        list_documents.append(Document(text=x[0], metadata=x[1]))
    return list_documents


def create_vector_store_cate(model,
                             path_save,
                             data_dict):
    docs = list(data_dict.keys())
    list_docs = [Document(text=x) for x in docs]
    index = VectorStoreIndex.from_documents(
        list_docs, embed_model=model, show_progress=True
    )
    index.storage_context.persist(persist_dir=path_save)


def create_vector_desc(list_desc, path_save):
    list_docs = [Document(text=x[0], metadata={"id": x[1]}) for x in list_desc]
    index = VectorStoreIndex.from_documents(
        list_docs, embed_model=model, show_progress=True
    )
    index.storage_context.persist(persist_dir=path_save)


def create_emb_cate(df_movies,
                    embed_model):
    genre_dict, countries_dict, language_dict = create_dict_mapping(df_movies)
    # genres
    with open('checkpoint/genres.json', 'w') as f:
        json.dump(genre_dict, f)
    create_vector_store_cate(model=embed_model, data_dict=genre_dict, path_save="checkpoint/genres")
    print(f"Created vector store index of genres: Done")
    # countries
    with open('checkpoint/countries.json', 'w') as f:
        json.dump(countries_dict, f)
    create_vector_store_cate(model=embed_model, data_dict=countries_dict, path_save='checkpoint/countries')
    print(f"Created vector store index of countries: Done")
    # language
    with open('checkpoint/language.json', 'w') as f:
        json.dump(language_dict, f)
    create_vector_store_cate(model=embed_model, data_dict=language_dict, path_save='checkpoint/language')
    print(f"Created vector store index of language: Done")
    # title
    list_title = list(zip(df_movies['title'], df_movies['id']))
    create_vector_desc(list_desc=list_title, path_save='checkpoint/title')
    print(f"Created vector store index of title: Done")
    # overview
    list_overview = list(zip(df_movies['overview'], df_movies['id']))
    create_vector_desc(list_desc=list_overview, path_save='checkpoint/overview')
    print(f"Created vector store index of overview: Done")
    return None


if __name__ == '__main__':
    path_data = 'data/movies.csv'
    df_movies_data = pd.read_csv(path_data)

    model = OpenAIEmbedding(model="text-embedding-3-small", api_key=OPENAI_KEY)
    create_emb_cate(df_movies=df_movies_data,
                    embed_model=model)
