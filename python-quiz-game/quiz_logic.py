import random
from questions_database import questions

def get_questions_by_theme(theme, num_questions):
    """Filter questions by theme and limit by user preference."""
    filtered_questions = [v for k, v in questions.items() if k[1].lower() == theme]
    return random.sample(filtered_questions, min(len(filtered_questions), num_questions))

def get_random_questions(num_questions):
    """Fetch random questions from all themes."""
    all_questions = list(questions.values())
    return random.sample(all_questions, min(len(all_questions), num_questions))

def play_the_quiz():
    print("WELCOME TO THE HO HO FO. A QUIZ GAME!")
    user = input("Howdy! Please Enter your name: ").strip()

    themes = set(key[1] for key in questions.keys())
    print(f"\nAvailable themes: {', '.join(themes)}")

    theme_mode = input(f"Hey {user}, would you like questions from one theme or multiple themes? (Enter 'one' or 'multi'): ").strip().lower()
    
    if theme_mode not in ['one', 'multi']:
        print("Invalid choice. Exiting game.")
        return

    num_questions = input("How many questions would you like to answer? ").strip()
    try:
        num_questions = int(num_questions)
        if num_questions <= 0:
            print("Invalid number of questions. Exiting game.")
            return
    except ValueError:
        print("Invalid input. Please enter a number. Exiting game.")
        return

    if theme_mode == 'one':
        theme = input("Please select a theme: ").strip().lower()
        available_themes = [t.lower() for t in themes]

        if theme not in available_themes:
            print("Invalid theme. Exiting game.")
            return

        questions_to_ask = get_questions_by_theme(theme, num_questions)
    else:
        questions_to_ask = get_random_questions(num_questions)

    score = 0
    random.shuffle(questions_to_ask)

    for idx, question_data in enumerate(questions_to_ask):
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

    print(f"\nYour final score is: {score}/{len(questions_to_ask)}")
    print("Thank you for playing!")

# To start the game, run the play_game file
