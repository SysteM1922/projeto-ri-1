from searcher import Searcher

searcher = Searcher(searcher_mode='interactive',
                    index_folder="",
                    path_to_questions="questions/question_E8B1_gs.jsonl",
                    output_file="output",
                    top_k=10,
                    ranking_mode="ranking.tfidf").start()
                    