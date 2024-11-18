import random
from questions_database import questions
def get_questions_by_theme(theme):
    "Filter questions by theme according to user input"
    return [v for k, v in questions.items() if k[1].lower() == theme]

def play_the_quiz():
    print("WELCOME TO THE HO HO FO. A QUIZ GAME!")
    user=input("Howdy! Please Enter your name: ")
    themes = set(key[1] for key in questions.keys())
    print(f"Available themes: {', '.join(themes)}")
    theme = input(f"Hey! {user}, Please select a theme: ").strip().lower()
    available_themes = [t.lower() for t in themes]

    if theme not in available_themes:
        print("Invalid theme. Exiting game.")
        return

    theme_questions = get_questions_by_theme(theme)
    random.shuffle(theme_questions)
    score = 0
    for idx, question_data in enumerate(theme_questions):
        question, options, correct = question_data
        print(f"\nQuestion {idx + 1}: {question}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        try:
            answer = int(input("Your answer (1-4): ").strip())
            if options[answer - 1] == correct:
                print("Correct!")
                score += 1
            else:
                print(f"Wrong! The correct answer was: {correct}")
        except (ValueError, IndexError):
            print("Invalid input. Moving to the next question.")

    print(f"\nYour final score is: {score}/{len(theme_questions)}")
    print("Thank you for playing!")