Here is the corrected Python code with added docstrings, improvements, and changes as suggested:

```python
"""
Quiz class for creating multiple choice questions and generating quizzes.

Attributes:
    filename (str): The name of the file containing the question data.
    questions (list): List of Question objects containing the questions.
    num_questions (int): Number of questions to include in the quiz.
"""
import random
from typing import Iterable, List, Tuple

class Question:
    """
    Represents a multiple choice question with four possible answers.

    Attributes:
        text (str): The text of the question.
        answers (list[str]): List of possible answers for the question.
        correct_answer (str): The correct answer for the question.
    """

    def __init__(self, text: str, answers: List[str], correct_answer: str) -> None:
        self.text = text
        self.answers = answers
        self.correct_answer = correct_answer

class Quiz:
    """
    Generates a multiple choice quiz from a file containing question data.

    Attributes:
        filename (str): The name of the file containing the question data.
        questions (list[Question]): List of Question objects containing the questions.
        num_questions (int): Number of questions to include in the quiz.
    """

    def __init__(self, filename: str, num_questions: int = 10) -> None:
        self.filename = filename
        self.num_questions = num_questions

    def _load_questions(self) -> List[Question]:
        """
        Loads the question data from a file and returns a list of Question objects.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        questions = []
        with open(self.filename, 'r') as f:
            for line in f:
                text, *answers, correct_answer = line.strip().split('|')
                question = Question(text, answers, correct_answer)
                questions.append(question)
        return questions

    def _select_questions(self, questions: Iterable[Question]) -> List[Question]:
        """
        Selects the desired number of questions from a list of Questions.

        Args:
            questions (Iterable[Question]): A iterable containing Question objects.

        Returns:
            A new list of Question objects containing the selected questions.
        """
        return random.sample(questions, self.num_questions)

    def _generate_quiz(self) -> List[Tuple[Question, str]]:
        """
        Generates a multiple choice quiz from the loaded question data.

        Returns:
            A list of tuples containing each question and its correct answer.
        """
        questions = self._load_questions()
        selected_questions = self._select_questions(questions)
        return [(question, question.correct_answer) for question in selected_questions]

    def generate_quiz(self) -> List[Tuple[str, List[str]]]:
        """
        Generates a multiple choice quiz and returns it as a list of tuples containing each question text and its possible answers.

        Raises:
            ValueError: If an empty file is encountered or the number of questions exceeds the available questions.
        """
        if not self._load_questions():
            raise FileNotFoundError(f'The file {self.filename} was empty.')

        quiz = self._generate_quiz()
        if len(quiz) < self.num_questions:
            raise ValueError(f'There are not enough questions in the file to generate a quiz with {self.num_questions} questions.')

        return quiz
```