[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/Er3VCUTS)
# RI-2023 practical assignment (IR-system)

This repository contains the CLI definition for implementing a fully functional IR system, it was projected to serve as guidelines to the RI students during their class assignments. Here, the students will find a definition of a generic enough search engine API (indexer, searcher and evaluator), that they should complete with the most adequate IR methods learned during the classes.

**NOTE: If you have any doubts, please use the issues of this repository to ask questions. This way, you can assist other colleagues who may share the same doubts or benefit from their assistance as well.**

## Table-of-Contents

* [Overview](overview)
	* [Indexer Mode](#indexer-mode)
    * [Searcher Mode](#searcher-mode)
    * [Evaluator Mode](#evaluator-mode)
* [How to Run](#how-to-run)
    * [How to Start](#how-to-start)
* [Assigment Evaluation](#assigment-evaluation)
* [FAQs](#faqs)

## Overview

The file `main.py` serves as the main entry point of the system and defines the CLI interface that students are expected to follow. It includes three modes of operation: the **indexer mode**, the **searcher mode**, and the **evaluator mode**. Each of these modes corresponds to specific functionalities that students should implement as part of the assignment1. 

The `main.py` file has been provided to fulfill the necessary implementation for the first assignment. While it is recommended that students adhere to the designated CLI interface, it is not an absolute requirement. If students find it more convenient to implement or expand upon the existing CLI, they are free to do so. However, it is essential that they update the `assignment1-*.sh` files to reflect the CLI changes so that we can run their code successfully.

### Indexer Mode

The indexer is responsible for building an inverted index from a collection of documents. It takes two mandatory arguments: path_to_collection, which specifies the location of the document collection to be indexed, and index_output_folder, which specifies the folder where all index-related files will be stored. Additionally, there are several indexer settings that can be adjusted, such as the indexing algorithm, RAM consumption limit, and options for storing term positions and intermediate BM25 or TFIDF cache files.

For more details:
```bash
python main.py indexer --help
```

### Searcher Mode

The searcher mode is designed for querying the built inverted index and offers two operating modes. In interactive mode, the searcher loads the index and repeatedly prompts for a query,  showing the top k results. This operating mode requires one mandatory argument: index_folder, which specifies the folder where the index-related files are located. In batch mode, the searcher loads the index and a batch of queries, executes the queries and saves the results to a file. This operating mode requires three mandatory arguments: index_folder, path_to_questions, and output_file. The index_folder specifies the folder where the index-related files are located, path_to_queries is the path to the file containing the queries to be processed (one per line), and output_file is the file where the documents returned for each query will be written. Additionally, in both operating modes the user can specify the maximum number of documents to be returned per query using the --top_k option. Both operating modes also allows the selection of ranking methods, such as BM25 or TFIDF, and the customization of their parameters.

For more details:
```bash
python main.py searcher interactive --help
```

```bash
python main.py searcher batch --help
```

### Evaluator Mode

The evaluator mode is used to assess the performance of the implemented IR system. It takes two mandatory arguments: gold_standard_file and run_file. The gold_standard_file is the path to the file containing the questions and the corresponding gold standard judgments. The run_file contains the questions and the ranked list of documents produced by the IR system. Additionally, the user can specify a list of evaluation metrics to be calculated, with default options being F1, nDCG, and MAP.

For more details:
```bash
python main.py evaluator --help
```

## How to run

As an initial step, we recommend running the provided code and examining the output it generates. This will help you understand how we parse the arguments. For instance, execute the following command:

```bash
python main.py indexer collections/pubmed_tiny.jsonl pubmed_indexer_folder
```

For a more comprehensive explanation, here's an example of how to run the indexer. However, for additional examples and various operation modes, please consult the assignment1-*.sh files.


```bash
python main.py indexer collections/pubmed_tiny.jsonl pubmed_indexer_folder --tokenizer.minL 3 --tokenizer.stopwords stopw.txt --tokenizer.stemmer potterNLTK --indexer.algorithm SPIMI
```

In this example, the program indexes the documents present in pubmed_tiny.jsonl and saves the resulting index in the pubmed_indexer_folder. Special options are also specified for the tokenizer, such as using the stopword file stopw.txt.

### How to Start

Once the students have grasped the CLI interface, they should be ready to commence the development of their systems. They can utilize the `args` variable (located on line 198) to initialize the corresponding modules within their systems, based on the modes and parameters provided in `args`.

## Assigment Evaluation

In addition to the standard code evaluation, we aim to evaluate the real-world performance of your developed system by benchmarking it in terms of time, memory, and retrieval performance. To facilitate this evaluation, we provide three `assignment1-*.sh` scripts containing the commands that will be executed for benchmarking. Therefore, we expect these scripts to be functional, and students should confirm their functionality before submitting the code. If any changes are made to the CLI (`main.py`), students must also update the corresponding `assignment1-*.sh` scripts. Furthermore, any changes made to the `assignment1-*.sh` scripts should be documented and explained in a readme or PDF file.

Also note, that in the scripts we are using virtual environments (python-venv) and we are installing the dependencies specified on the `requirements.txt` files, so please do not forget to add your requirements there. 

For the intermediate delivery (11/12 October), it is anticipated that students verify the correct functionality of the assignment-indexer.sh script. This script will play a pivotal role as the primary file used in the automated evaluation process. Additionally, students should also ensure that their code generates the expected output and behavior as described within the script.

## FAQs

### Why not enforcing a strict CLI and evaluation format?

Ultimately, the presented CLI covers only the most generic retrieval scenarios sufficient to solve Assignment 1. However, it lacks the details required to implement highly efficient indexing and retrieval algorithms. Therefore, if an exceptional group of students wishes to undertake the challenge of implementing the best possible search engine, we want to leave that door open.

### I want to extend the current CLI, but I am not understanding how?

The current CLI was implemented using the `argparse` standard library and was extended to support argument groups (variables that belong to group). A group is created when the "." character is found in a variable name. For instance, the optional argument `--indexer.bm25.k1 0.7` assigns the value `0.7` to the variable `k1`, which belongs to the subgroup `bm25`, which in turn belongs to the group `indexer`. This allows us to structure our CLI arguments in a more interpretable way. Internally, this information is stored under the Params class (defined in the `cliutils.py` file).

To add more options, you need to follow the basic argparse syntax and respect the grouping schema explained above. For example, if you want to add a flag to enable index compression to the indexer, you can do it by adding the following line:

```python
indexer_settings_parser.add_argument('--indexer.storing.index_compression', 
                                         action="store_true",
                                         help='If this flag is added the variable index_compression becomes True else it will be False')
```

### Can I write my index in other format?
No, all students should respect the index format, such that we can automaticly evaluate and compute index statistics. 

### Can I do my own CLI?

Yes, but adjust the `assignment1-*.sh` scripts accordingly. 

### Why there is no tokenizer in the searcher. How should I tokenize my query?

The correct practice when constructing the inverted index is to include the tokenizer's parameters as part of the stored information. This ensures that when we execute the search, we can employ the precise same tokenizer for processing our queries as well. Thus achieving precise matches between query terms and document terms in the inverted index. As a result, for the sake of simplifying the assignment, we assume that during the search process, the tokenizer utilized for building the corresponding index should always be initialized.

## Acknowledgements

This code template were created by Tiago Almeida and Sérgio Matos for the RI class in 2023.
