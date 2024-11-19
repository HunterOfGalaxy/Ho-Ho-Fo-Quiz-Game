import random
import time
import json
import os
from questions_database import questions

LEADERBOARD_FILE = "leaderboard.json"
SAVE_FILE = "saved_game.json"

def load_leaderboard():
    """Load leaderboard from a file."""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return []

def save_leaderboard(leaderboard):
    """Save leaderboard to a file."""
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=4)

def display_leaderboard():
    """Display the top scores."""
    leaderboard = load_leaderboard()
    if not leaderboard:
        print("No leaderboard data available yet.")
        return

    print("\nLeaderboard:")
    print("{:<20} {:<10}".format("Player", "Score"))
    print("-" * 30)
    for entry in sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]:
        print(f"{entry['name']:<20} {entry['score']:<10}")
    print("-" * 30)

def save_game_state(game_state):
    """Save the current game state."""
    with open(SAVE_FILE, "w") as f:
        json.dump(game_state, f, indent=4)

def load_game_state():
    """Load a saved game state."""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return None

def delete_saved_game():
    """Delete the saved game file."""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

def get_questions_by_theme(theme, asked_questions):
    """Filter questions by theme and exclude already asked ones."""
    return [
        (k, v) for k, v in questions.items()
        if k[1].lower() == theme and k not in asked_questions
    ]

def distribute_questions(questions_pool, num_questions, weights=None):
    """
    Distribute questions across difficulties for mixed mode.
    Allows dynamic weighting of easy, medium, and hard questions.
    """
    # Categorize questions by difficulty
    difficulties = {"easy": [], "medium": [], "hard": []}
    for key, data in questions_pool:
        difficulties[data[4]].append((key, data))  # data[4] is the difficulty level

    # Set default weights if none are provided
    weights = weights or {"easy": 1, "medium": 1, "hard": 1}
    total_weight = sum(weights.values())

    # Calculate the number of questions for each difficulty
    split = {level: int(num_questions * weights[level] / total_weight) for level in difficulties}
    remaining = num_questions - sum(split.values())

    # Distribute remaining questions randomly among difficulties
    for level in random.sample(list(difficulties.keys()), remaining):
        split[level] += 1

    # Select questions from each difficulty
    selected_questions = []
    for level, count in split.items():
        selected_questions.extend(random.sample(difficulties[level], min(count, len(difficulties[level]))))

    return selected_questions

def play_the_quiz():
    print("WELCOME TO THE HO HO FO. A QUIZ GAME!")
    user = input("Howdy! Please Enter your name: ").strip()

    # Load a saved game or start fresh
    saved_game = None
    if os.path.exists(SAVE_FILE):
        resume = input("You have a saved game. Do you want to resume? (yes/no): ").strip().lower()
        if resume == "yes":
            saved_game = load_game_state()

    if saved_game:
        print("\nResuming your previous game...")
        theme = saved_game["theme"]
        score = saved_game["score"]
        asked_questions = set(tuple(q) for q in saved_game["asked_questions"])
        num_questions = saved_game["num_questions"]
        questions_to_ask = saved_game["questions_to_ask"]
        hints_left = saved_game["hints_left"]
    else:
        themes = set(key[1] for key in questions.keys())
        print("\nAvailable themes:")
        for i, theme_name in enumerate(themes, 1):
            print(f"{i}. {theme_name}")

        try:
            theme_choice = int(input("Select a theme by number: ").strip())
            theme = list(themes)[theme_choice - 1].lower()
        except (ValueError, IndexError):
            print("Invalid theme choice. Exiting game.")
            return

        mixed_mode = input("Do you want mixed difficulty questions? (yes/no): ").strip().lower()
        if mixed_mode not in {"yes", "no"}:
            print("Invalid input. Exiting game.")
            return

        if mixed_mode == "yes":
            weights_input = input(
                "Enter weights for easy, medium, and hard (e.g., 2 3 1) or press Enter for default: "
            ).strip()
            if weights_input:
                try:
                    weights = list(map(int, weights_input.split()))
                    if len(weights) != 3 or any(w < 0 for w in weights):
                        raise ValueError
                    weights = {"easy": weights[0], "medium": weights[1], "hard": weights[2]}
                except ValueError:
                    print("Invalid weights. Using default equal distribution.")
                    weights = {"easy": 1, "medium": 1, "hard": 1}
            else:
                weights = {"easy": 1, "medium": 1, "hard": 1}
        else:
            difficulty = input("\nSelect a difficulty level (easy, medium, hard): ").strip().lower()
            difficulties = {"easy", "medium", "hard"}
            if difficulty not in difficulties:
                print("Invalid difficulty level. Exiting game.")
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

        asked_questions = set()
        all_theme_questions = get_questions_by_theme(theme, asked_questions)

        if mixed_mode == "yes":
            questions_to_ask = distribute_questions(all_theme_questions, num_questions, weights)
        else:
            questions_to_ask = [
                (k, v) for k, v in all_theme_questions if v[4].lower() == difficulty
            ]
            questions_to_ask = random.sample(questions_to_ask, min(len(questions_to_ask), num_questions))

        hints_left = 2  # Allow two hints per game
        score = 0

    if not questions_to_ask:
        print("Sorry, no questions available for the selected options.")
        return

    max_score = 0
    for idx, (key, question_data) in enumerate(questions_to_ask):
        question, options, correct, explanation, difficulty = question_data
        points = {"easy": 1, "medium": 2, "hard": 3}[difficulty]
        max_score += points

        print(f"\nQuestion {idx + 1}: {question}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        if hints_left > 0:
            while True:
                use_hint = input("Would you like a hint? (yes/no): ").strip().lower()
                if use_hint in {"yes", "no"}:
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")

            if use_hint == "yes":
                hints_left -= 1
                incorrect_options = [opt for opt in options if opt != correct]
                eliminated = random.sample(incorrect_options, min(2, len(incorrect_options)))
                print(f"Hint: The following options are incorrect: {', '.join(eliminated)}")


        start_time = time.time()
        try:
            answer = int(input("Your answer (1-4): ").strip())
            elapsed_time = time.time() - start_time

            if options[answer - 1] == correct:
                print(f"Correct! (+{points} points)")
                score += points
            else:
                print(f"Wrong! The correct answer was: {correct}")
        except (ValueError, IndexError):
            print("Invalid input. Moving to the next question.")

        if explanation:
            print(f"Explanation: {explanation}")

        asked_questions.add(key)
        game_state = {
            "theme": theme,
            "score": score,
            "asked_questions": list(asked_questions),
            "num_questions": num_questions,
            "questions_to_ask": questions_to_ask[idx + 1:],
            "hints_left": hints_left,
        }
        save_game_state(game_state)

    print(f"\nYour final score is: {score}/{max_score}")
    leaderboard = load_leaderboard()
    leaderboard.append({"name": user, "score": score})
    save_leaderboard(leaderboard)
    display_leaderboard()
    delete_saved_game()
    print("Thank you for playing!")