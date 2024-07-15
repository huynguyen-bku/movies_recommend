PROMPT_EXTRACT = """Instructions: Identify and extract the following information from a user's written request about a movie:
- Genre: The movie's genre

- Language: The language in which the film is made
- Country: The country where the movie originates

- Title: The name of the movie
- Overview: A brief description of the movie's content

- Budget: The movie's budget
- Release Date: The release date of the movie
- Revenue: The movie's revenue
- Runtime: The movie's duration
Your task is to find and list these details from the user's request."""


class Translation:
    def __init__(self, text):
        self.text = text
        self.prompt = f"""Translate the given input message into English, ensuring that no information is lost or summarized. The translation should be complete and accurate
- task:{self.text}
- output:"""


class Extract:
    def __init__(self, text):
        self.text = text
        self.get_genres = f"""* Instructions: Identify the following information from the user's request: "Genre". If any information is not available, return "none". For the genre, there may be multiple entries.
* Example 1: 
input : "find me some movies with romance, comedy in China"
output: romance, comedy
* Example 2: 
input: "show me adventure films"
output: adventure
* Task:
input: "{self.text}"
output: """

        self.get_cate_field = f"""Instructions: Extract the "Language" and "Country" fields from the input. If either field is missing, return "none" for that field. And if the text does not clearly indicate language or country, priority will be given to the country field
* Example 1: 
input : "I'm looking for movies in French from Canada."
output: French, Canada
* Example 2: 
input : "Find me films from Japan."
output:  none, Japan
* Example 3: 
input :  "Recommend some good movies."
output: none, none
* Example 4:
Input: "Recommend Vietnamese action movies."
Output: none, Vietnam
Example 5:
Input: "I want to watch Spanish movies."
Output: none, Spanish
* Task:
input: "{self.text}"
output: """
        self.get_title_overview = f"""* Instructions: Extract the "Title" and "Overview" fields from the input. If either field is missing, return "none" for that field.
*Example 1:
Input: "I'm interested in a movie called Inception. It's about a thief who steals corporate secrets through dream-sharing technology."
Output: Inception
It's about a thief who steals corporate secrets through dream-sharing technology.
*Example 2:
Input: "I want to watch The Matrix."
Output: The Matrix
none
*Example 3:
Input: "Tell me about a movie where a young girl navigates a dangerous world with the help of a mysterious guide."
Output: none
a young girl navigates a dangerous world with the help of a mysterious guide
*Example 4:
Input: "Recommend a movie."
Output: none
none
* Task:
input: "{self.text}"
output: """
        self.get_sql = f"""
* Instructions: Create an SQL statement to search for movies based on the "budget" and/or "revenue" fields in the WHERE clause. Always use SELECT * to retrieve all columns from the provided DataFrame.
- Table name: df_movies_recom
- Important note: Only use the fields "budget" and "revenue" to create sql statements. Absolutely do not use any other information fields such as 'genres', 'country', ... to create sql statements
- Table name: df_movies_recom
- If 'search text' does not require a query, 'none' can be returned.
* Schema: CREATE TABLE df_movies_recom (
    budget INT,
    revenue INT
);
* Example 1:
Input:  "Top 10 highest-grossing comedy movies in the US"
Output: SELECT *
FROM df_movies_recom
ORDER BY revenue DESC
LIMIT 10;
* Example 2:
Input: "highest revenue"
Output: SELECT *
FROM df_movies_recom
ORDER BY revenue DESC
LIMIT 1;
* Example 3:
Input: "Top 10 action movies from Vietnam with the highest budget"
Output:
SELECT * 
FROM df_movies_recom 
ORDER BY budget DESC 
LIMIT 10;
* Example 4:
Input: "Chinese movies that lost money"
Output:
SELECT * 
FROM df_movies_recom 
WHERE revenue < budget;
* Task: 
Input: "{self.text}"
Output: """
