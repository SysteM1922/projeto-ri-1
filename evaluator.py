import json
from math import log2

class Evaluator:
    def __init__(self, gold_standard_file: str, run_file: str, metrics: list = ["F1", "DCG", "AP", "precision", "recall"]):

        self.gold_standard_file_name = gold_standard_file.split("/")[-1].split(".")[0]
        self.gold_standard_file = self.load_files(gold_standard_file)
        self.run_file = self.load_files(run_file)
        self.metrics = metrics
            
    def evaluate(self):
        evals = {}
        
        for j in [10, 50, 100]:
            precision_list = []
            recall_list = []
            f_measure_list = []
            average_precision_list = []
            dcg_list = []

            for gold_query, run_query in zip(self.gold_standard_file, self.run_file):
                gold_pmid = set(gold_query["documents_pmid"])
                run_pmid = set(run_query["documents_pmid"][:j])
                intersection = gold_pmid.intersection(run_pmid)

                # Precision
                precision = len(intersection) / len(gold_pmid) if len(gold_pmid) > 0 else 0
                precision_list.append(precision)

                # Recall
                recall = len(intersection) / len(gold_pmid) if len(gold_pmid) > 0 else 0
                recall_list.append(recall)

                # F-measure
                f_measure = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                f_measure_list.append(f_measure)

                # Average Precision (AP)
                ap = 0
                relevant_count = 0
                for i, doc in enumerate(run_query["documents_pmid"]):
                    if doc in gold_pmid:
                        relevant_count += 1
                        ap += relevant_count / (i + 1)
                ap /= len(gold_pmid) if len(gold_pmid) > 0 else 1
                average_precision_list.append(ap)

                # Discounted Cumulative Gain (DCG)
                dcg = 0
                for i, doc in enumerate(run_query["documents_pmid"]):
                    if doc in gold_pmid:
                        dcg += 1 / log2(i + 2)
                dcg_list.append(dcg)

            avg_precision = sum(precision_list) / len(precision_list) if len(precision_list) > 0 else 0
            avg_dcg = sum(dcg_list) / len(dcg_list) if len(dcg_list) > 0 else 0

            evals["top_" + str(j)] = {
                "Precision": avg_precision,
                "Recall": sum(recall_list) / len(recall_list) if len(recall_list) > 0 else 0,
                "F-measure": sum(f_measure_list) / len(f_measure_list) if len(f_measure_list) > 0 else 0,
                "Average Precision (AP)": sum(average_precision_list) / len(average_precision_list) if len(
                    average_precision_list) > 0 else 0,
                "Discounted Cumulative Gain (DCG)": avg_dcg
            }

        # Save results to file
        with open(f"{self.gold_standard_file_name}_eval.json", "w") as f:
            f.write("[")
            json.dump({"query_file_name":self.gold_standard_file_name},f)
            f.write(",\n")
            json.dump(evals, f, indent=4)
            f.write("]")

        self.eval_results = evals
        self.print_results()

    def print_results(self,):

        for i in [10, 50, 100]:
            print("Top " + str(i) + ":")
            if "F1" in self.metrics:
                print("F1: " + str(self.eval_results["top_" + str(i)]["F-measure"]))
            if "DCG" in self.metrics:
                print("DCG: " + str(self.eval_results["top_" + str(i)]["Discounted Cumulative Gain (DCG)"]))
            if "AP" in self.metrics:
                print("AP: " + str(self.eval_results["top_" + str(i)]["Average Precision (AP)"]))
            if "precision" in self.metrics:
                print("Precision: " + str(self.eval_results["top_" + str(i)]["Precision"]))
            if "recall" in self.metrics:
                print("Recall: " + str(self.eval_results["top_" + str(i)]["Recall"]))
            print("\n")
    
    def load_files(self, file_path):
        with open(file_path, "r") as f:
            lines = [json.loads(line) for line in f]
        return lines


