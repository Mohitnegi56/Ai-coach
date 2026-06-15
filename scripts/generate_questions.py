"""Generate the ML/DS interview question bank JSON."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ideal_answers_data import IDEAL_ANSWERS

TOPICS = [
    "machine_learning",
    "deep_learning",
    "statistics",
    "python_data",
    "feature_engineering",
    "model_evaluation",
    "nlp",
    "computer_vision",
    "mlops",
    "sql_databases",
]

DIFFICULTIES = ["easy", "medium", "hard"]

RAW_QUESTIONS: list[tuple[str, str, str, list[str]]] = [
    # machine_learning (15)
    ("ml-001", "What is the difference between supervised and unsupervised learning?", "machine_learning", "easy", ["fundamentals"]),
    ("ml-002", "Explain bias-variance tradeoff.", "machine_learning", "medium", ["theory"]),
    ("ml-003", "What is overfitting and how do you prevent it?", "machine_learning", "easy", ["regularization"]),
    ("ml-004", "Compare bagging and boosting.", "machine_learning", "medium", ["ensemble"]),
    ("ml-005", "What is gradient descent?", "machine_learning", "easy", ["optimization"]),
    ("ml-006", "Explain how a decision tree splits data.", "machine_learning", "easy", ["trees"]),
    ("ml-007", "What is the curse of dimensionality?", "machine_learning", "medium", ["theory"]),
    ("ml-008", "When would you use logistic regression vs linear regression?", "machine_learning", "easy", ["classification"]),
    ("ml-009", "What is cross-validation and why is it important?", "machine_learning", "medium", ["evaluation"]),
    ("ml-010", "Explain random forests and their advantages.", "machine_learning", "medium", ["ensemble"]),
    ("ml-011", "What is k-means clustering?", "machine_learning", "easy", ["clustering"]),
    ("ml-012", "How does XGBoost differ from standard gradient boosting?", "machine_learning", "hard", ["ensemble"]),
    ("ml-013", "What is regularization? Compare L1 and L2.", "machine_learning", "medium", ["regularization"]),
    ("ml-014", "Explain the concept of a support vector machine.", "machine_learning", "hard", ["classification"]),
    ("ml-015", "What is PCA and when would you use it?", "machine_learning", "medium", ["dimensionality_reduction"]),
    # deep_learning (15)
    ("dl-001", "What is a neural network?", "deep_learning", "easy", ["fundamentals"]),
    ("dl-002", "Explain backpropagation.", "deep_learning", "medium", ["training"]),
    ("dl-003", "What is the vanishing gradient problem?", "deep_learning", "medium", ["training"]),
    ("dl-004", "Compare ReLU, sigmoid, and tanh activations.", "deep_learning", "easy", ["activations"]),
    ("dl-005", "What is batch normalization?", "deep_learning", "medium", ["training"]),
    ("dl-006", "Explain CNN architecture for image classification.", "deep_learning", "medium", ["cnn"]),
    ("dl-007", "What is dropout and why is it used?", "deep_learning", "easy", ["regularization"]),
    ("dl-008", "Describe how an LSTM handles sequential data.", "deep_learning", "hard", ["rnn"]),
    ("dl-009", "What is transfer learning?", "deep_learning", "medium", ["transfer"]),
    ("dl-010", "Explain attention mechanism in transformers.", "deep_learning", "hard", ["transformers"]),
    ("dl-011", "What is the difference between epoch, batch, and iteration?", "deep_learning", "easy", ["training"]),
    ("dl-012", "How do you choose a learning rate?", "deep_learning", "medium", ["optimization"]),
    ("dl-013", "What is a GAN?", "deep_learning", "hard", ["generative"]),
    ("dl-014", "Explain residual connections in ResNet.", "deep_learning", "hard", ["architecture"]),
    ("dl-015", "What is fine-tuning a pre-trained model?", "deep_learning", "medium", ["transfer"]),
    # statistics (12)
    ("stat-001", "What is the difference between mean, median, and mode?", "statistics", "easy", ["descriptive"]),
    ("stat-002", "Explain p-value and statistical significance.", "statistics", "medium", ["hypothesis_testing"]),
    ("stat-003", "What is Type I vs Type II error?", "statistics", "medium", ["hypothesis_testing"]),
    ("stat-004", "Describe normal distribution and its properties.", "statistics", "easy", ["distributions"]),
    ("stat-005", "What is Bayes theorem?", "statistics", "medium", ["probability"]),
    ("stat-006", "Explain confidence intervals.", "statistics", "medium", ["inference"]),
    ("stat-007", "What is correlation vs causation?", "statistics", "easy", ["fundamentals"]),
    ("stat-008", "When do you use t-test vs chi-square test?", "statistics", "medium", ["hypothesis_testing"]),
    ("stat-009", "What is the central limit theorem?", "statistics", "medium", ["theory"]),
    ("stat-010", "Explain maximum likelihood estimation.", "statistics", "hard", ["inference"]),
    ("stat-011", "What is multicollinearity?", "statistics", "medium", ["regression"]),
    ("stat-012", "Describe A/B testing methodology.", "statistics", "medium", ["experimentation"]),
    # python_data (12)
    ("py-001", "What is the difference between a list and a tuple?", "python_data", "easy", ["python_basics"]),
    ("py-002", "Explain pandas DataFrame vs Series.", "python_data", "easy", ["pandas"]),
    ("py-003", "How do you handle missing values in pandas?", "python_data", "medium", ["pandas"]),
    ("py-004", "What is vectorization and why is it faster?", "python_data", "medium", ["numpy"]),
    ("py-005", "Explain groupby operations in pandas.", "python_data", "medium", ["pandas"]),
    ("py-006", "What is the difference between merge and concat?", "python_data", "medium", ["pandas"]),
    ("py-007", "How do you read a large CSV that does not fit in memory?", "python_data", "hard", ["pandas"]),
    ("py-008", "What are list comprehensions?", "python_data", "easy", ["python_basics"]),
    ("py-009", "Explain broadcasting in NumPy.", "python_data", "medium", ["numpy"]),
    ("py-010", "What is a generator vs iterator?", "python_data", "medium", ["python_basics"]),
    ("py-011", "How do you optimize Python code for data processing?", "python_data", "hard", ["performance"]),
    ("py-012", "What is the GIL and how does it affect parallelism?", "python_data", "hard", ["python_basics"]),
    # feature_engineering (10)
    ("fe-001", "What is one-hot encoding?", "feature_engineering", "easy", ["encoding"]),
    ("fe-002", "When should you use label encoding vs one-hot?", "feature_engineering", "medium", ["encoding"]),
    ("fe-003", "Explain feature scaling: normalization vs standardization.", "feature_engineering", "easy", ["scaling"]),
    ("fe-004", "What is feature selection and why is it important?", "feature_engineering", "medium", ["selection"]),
    ("fe-005", "How do you handle categorical variables with high cardinality?", "feature_engineering", "hard", ["encoding"]),
    ("fe-006", "What is target encoding?", "feature_engineering", "hard", ["encoding"]),
    ("fe-007", "Explain polynomial features.", "feature_engineering", "medium", ["transforms"]),
    ("fe-008", "How do you create time-based features?", "feature_engineering", "medium", ["datetime"]),
    ("fe-009", "What is feature importance in tree models?", "feature_engineering", "easy", ["selection"]),
    ("fe-010", "Describe handling imbalanced datasets.", "feature_engineering", "medium", ["imbalance"]),
    # model_evaluation (10)
    ("eval-001", "What is accuracy and when is it misleading?", "model_evaluation", "easy", ["metrics"]),
    ("eval-002", "Explain precision, recall, and F1 score.", "model_evaluation", "easy", ["metrics"]),
    ("eval-003", "What is ROC-AUC?", "model_evaluation", "medium", ["metrics"]),
    ("eval-004", "Explain confusion matrix.", "model_evaluation", "easy", ["metrics"]),
    ("eval-005", "What is RMSE vs MAE?", "model_evaluation", "easy", ["regression_metrics"]),
    ("eval-006", "How do you detect data leakage?", "model_evaluation", "hard", ["validation"]),
    ("eval-007", "What is stratified k-fold cross-validation?", "model_evaluation", "medium", ["validation"]),
    ("eval-008", "Explain calibration of probability outputs.", "model_evaluation", "hard", ["metrics"]),
    ("eval-009", "What is a learning curve?", "model_evaluation", "medium", ["diagnostics"]),
    ("eval-010", "How do you compare models statistically?", "model_evaluation", "hard", ["validation"]),
    # nlp (10)
    ("nlp-001", "What is tokenization?", "nlp", "easy", ["preprocessing"]),
    ("nlp-002", "Explain TF-IDF.", "nlp", "medium", ["features"]),
    ("nlp-003", "What are word embeddings?", "nlp", "medium", ["embeddings"]),
    ("nlp-004", "How does Word2Vec work?", "nlp", "hard", ["embeddings"]),
    ("nlp-005", "What is BERT and why is it effective?", "nlp", "hard", ["transformers"]),
    ("nlp-006", "Explain named entity recognition.", "nlp", "medium", ["tasks"]),
    ("nlp-007", "What is sentiment analysis?", "nlp", "easy", ["tasks"]),
    ("nlp-008", "How do you handle out-of-vocabulary words?", "nlp", "medium", ["preprocessing"]),
    ("nlp-009", "What is BLEU score?", "nlp", "medium", ["metrics"]),
    ("nlp-010", "Explain sequence-to-sequence models.", "nlp", "hard", ["architecture"]),
    # computer_vision (10)
    ("cv-001", "What is image classification vs object detection?", "computer_vision", "easy", ["fundamentals"]),
    ("cv-002", "Explain convolution operation.", "computer_vision", "medium", ["cnn"]),
    ("cv-003", "What is pooling in CNNs?", "computer_vision", "easy", ["cnn"]),
    ("cv-004", "How does data augmentation help CV models?", "computer_vision", "medium", ["training"]),
    ("cv-005", "What is IoU in object detection?", "computer_vision", "medium", ["metrics"]),
    ("cv-006", "Explain YOLO architecture at a high level.", "computer_vision", "hard", ["detection"]),
    ("cv-007", "What is semantic segmentation?", "computer_vision", "medium", ["tasks"]),
    ("cv-008", "How do you handle class imbalance in image datasets?", "computer_vision", "medium", ["training"]),
    ("cv-009", "What is transfer learning in computer vision?", "computer_vision", "medium", ["transfer"]),
    ("cv-010", "Explain non-maximum suppression.", "computer_vision", "hard", ["detection"]),
    # mlops (8)
    ("ops-001", "What is MLOps?", "mlops", "easy", ["fundamentals"]),
    ("ops-002", "Explain model versioning.", "mlops", "medium", ["deployment"]),
    ("ops-003", "What is model drift?", "mlops", "medium", ["monitoring"]),
    ("ops-004", "How do you containerize an ML model?", "mlops", "medium", ["deployment"]),
    ("ops-005", "What is CI/CD for machine learning?", "mlops", "medium", ["pipelines"]),
    ("ops-006", "Explain feature stores.", "mlops", "hard", ["infrastructure"]),
    ("ops-007", "How do you monitor model performance in production?", "mlops", "medium", ["monitoring"]),
    ("ops-008", "What is A/B testing for ML models?", "mlops", "medium", ["experimentation"]),
    # sql_databases (8)
    ("sql-001", "What is the difference between INNER and LEFT JOIN?", "sql_databases", "easy", ["joins"]),
    ("sql-002", "Explain GROUP BY and HAVING.", "sql_databases", "easy", ["aggregation"]),
    ("sql-003", "What is a window function?", "sql_databases", "medium", ["analytics"]),
    ("sql-004", "How do you find duplicate records in SQL?", "sql_databases", "easy", ["queries"]),
    ("sql-005", "What is indexing and when does it help?", "sql_databases", "medium", ["performance"]),
    ("sql-006", "Explain normalization vs denormalization.", "sql_databases", "medium", ["design"]),
    ("sql-007", "Write a query to calculate running totals.", "sql_databases", "hard", ["analytics"]),
    ("sql-008", "What is the difference between OLTP and OLAP?", "sql_databases", "medium", ["fundamentals"]),
]


def build_bank() -> dict:
    questions = [
        {
            "id": qid,
            "question": text,
            "topic": topic,
            "difficulty": difficulty,
            "tags": tags,
            "ideal_answer": IDEAL_ANSWERS.get(qid, ""),
        }
        for qid, text, topic, difficulty, tags in RAW_QUESTIONS
    ]
    return {
        "metadata": {
            "version": "2.0",
            "total_questions": len(questions),
            "topics": TOPICS,
            "difficulties": DIFFICULTIES,
        },
        "questions": questions,
    }


def main() -> None:
    output = Path(__file__).resolve().parent.parent / "backend" / "data" / "questions.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    bank = build_bank()
    with output.open("w", encoding="utf-8") as handle:
        json.dump(bank, handle, indent=2, ensure_ascii=False)
    print(f"Wrote {bank['metadata']['total_questions']} questions to {output}")


if __name__ == "__main__":
    main()
