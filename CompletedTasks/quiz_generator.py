# Quiz Generator

import random

class QuizGenerator:
    def __init__(self, questions_file, answers_file):
        self.questions = self.read_file(questions_file)
        self.answers = self.read_file(answers_file)

    def read_file(self, file_name):
        try:
            with open(file_name, 'r') as file:
                data = file.readlines()
                return [line.strip() for line in data]
        except FileNotFoundError:
            print(f"File {file_name} not found.")
            return []

    def generate_quiz(self, num_questions):
        quiz = []
        for _ in range(num_questions):
            index = random.randint(0, len(self.questions) - 1)
            question = self.questions[index]
            answer = self.answers[index]
            quiz.append((question, answer))
        return quiz

# Test the QuizGenerator class
if __name__ == "__main__":
    quiz_gen = QuizGenerator("questions.txt", "answers.txt")
    num_questions = 5
    quiz = quiz_gen.generate_quiz(num_questions)
    for i, (question, answer) in enumerate(quiz, 1):
        print(f"Question {i}: {question}")
        user_answer = input("Your answer: ")
        if user_answer.lower() == answer.lower():
            print("Correct!\n")
        else:
            print("Incorrect. The correct answer is: {}\n".format(answer))

# Task: Validate input files for questions and answers to ensure they have the same number of entries.