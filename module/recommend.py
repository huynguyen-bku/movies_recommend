import os
import openai
import json
import pandas as pd
import pandasql as psql
from collections import Counter

from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import StorageContext, load_index_from_storage

from module.prompt import *
from module.constant import OPENAI_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_KEY
openai.api_key = os.environ["OPENAI_API_KEY"]


class Recommend:
    def __init__(self,
                 vector_store='checkpoint',
                 path_movies='data/movies.csv'):
        self.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        self.llm = OpenAI(model="gpt-4")
        self.extract = OpenAI(model="gpt-3.5-turbo",
                              system_prompt=PROMPT_EXTRACT)
        #
        self.retriever_genres = self.get_retriever(path_persist_dir=vector_store + '/genres')
        self.retriever_countries = self.get_retriever(path_persist_dir=vector_store + '/countries')
        self.retriever_language = self.get_retriever(path_persist_dir=vector_store + '/language')
        self.retriever_title = self.get_retriever(path_persist_dir=vector_store + '/title', k_docs=10)
        self.retriever_overview = self.get_retriever(path_persist_dir=vector_store + '/overview', k_docs=10)

        with open(vector_store + "/genres.json", "r") as f:
            self.genres = json.load(f)
        with open(vector_store + "/countries.json", "r") as f:
            self.countries = json.load(f)
        with open(vector_store + "/language.json", "r") as f:
            self.language = json.load(f)
        self.movies = pd.read_csv(path_movies)

    def get_retriever(self, path_persist_dir, k_docs=1):
        storage_context = StorageContext.from_defaults(persist_dir=path_persist_dir)
        index = load_index_from_storage(storage_context=storage_context, embed_model=self.embed_model)
        retriever = index.as_retriever(similarity_top_k=k_docs)
        return retriever

    def extract_info(self, query):
        prompt_trans = Translation(query)
        query_en = self.llm.chat([ChatMessage(role="user", content=prompt_trans.prompt)]).message.content
        print(query_en)
        prompt_extract = Extract(query_en)
        # get genres
        genres = self.extract.chat(
            [ChatMessage(role="user", content=prompt_extract.get_genres)]).message.content.lower()
        dict_out = {}
        if "none" not in genres:
            dict_out["genres"] = genres.split(',')
        else:
            dict_out["genres"] = []
        # get "Language" and "Country"
        info_lang_coun = self.extract.chat(
            [ChatMessage(role="user", content=prompt_extract.get_cate_field)]).message.content.lower()
        language, country = info_lang_coun.split(',')
        dict_out['language'] = language.strip()
        dict_out['country'] = country.strip()
        # get "Title" and "Overview"
        info_desc = (self.extract.chat([ChatMessage(role="user", content=prompt_extract.get_title_overview)]).message
                     .content)
        title, overview = info_desc.split('\n')
        dict_out['title'] = title.strip()
        dict_out['overview'] = overview.strip()
        # get filter
        info_filter = (self.llm.chat([ChatMessage(role="user", content=prompt_extract.get_sql)]).message
                       .content.strip())
        dict_out['sql'] = info_filter
        print(dict_out)

        return dict_out

    def get_candidate(self, dict_feature):
        # genres
        all_candidate = []
        for ele in dict_feature["genres"]:
            text = self.retriever_genres.retrieve(ele)[0].text
            print("genres:", text)
            genres_list = self.genres[text]
            all_candidate += genres_list
        # country
        if 'none' not in dict_feature["country"]:
            text = self.retriever_countries.retrieve(dict_feature["country"])[0].text
            print("country:", text)
            all_candidate += self.countries[text]
        # language
        if 'none' not in dict_feature["language"]:
            text = self.retriever_language.retrieve(dict_feature["language"])[0].text
            all_candidate += self.language[text]
            print("language:", text)
        # feature_dict
        if 'none' not in dict_feature["title"]:
            candidate_title = self.retriever_title.retrieve(dict_feature['title'])
            all_candidate += [x.metadata['id'] for x in candidate_title]
        # overview
        if 'none' not in dict_feature["overview"]:
            candidate_overview = self.retriever_overview.retrieve(dict_feature['overview'])
            all_candidate += [x.metadata['id'] for x in candidate_overview]
        # process all_candidate
        candidate_counter = Counter(all_candidate)
        cnd_dict = {}
        for item, count in candidate_counter.items():
            if count not in cnd_dict:
                cnd_dict[count] = []
            cnd_dict[count].append(item)
            # result
        if cnd_dict:
            candidate_id = cnd_dict[max(cnd_dict.keys())]
            return candidate_id
        else:
            return []

    def get_recommend(self, query):
        feature_dict = self.extract_info(query)
        candidate_id = self.get_candidate(feature_dict)
        df_movies_recom = self.movies[self.movies['id'].isin(candidate_id)] if candidate_id else self.movies
        # filter
        try:
            result_recom = psql.sqldf(feature_dict["sql"], locals())
        except:
            print('Cannot run sql query')
            result_recom = df_movies_recom
        if result_recom.shape[0] == self.movies.shape[0]:
            return None
        return result_recom


if __name__ == '__main__':
    # %%
    worker_recommend = Recommend(vector_store='checkpoint',
                                 path_movies='data/movies.csv')
    while True:
        query_text = input()
        df_candidate = worker_recommend.get_recommend(query_text)
        print(df_candidate)
