import random
from openai import OpenAI
import time
import os
# Call the LLM API
client = OpenAI(
api_key="your-deepseek-api",  # 在这里填写你的 DeepSeek API Key
base_url="https://api.deepseek.com/v1"  # DeepSeek API 的基础 URL
)

class DaVinciCodeGame:
    def __init__(self):
        # Initialize deck: black cards (0-11), white cards (0-11), and wildcards (-)
        self.deck = [f"B{i}" for i in range(12)] + [f"W{i}" for i in range(12)] + ["B-", "W-"]
        random.shuffle(self.deck)
        
        # Player hands (each player gets 4 cards)
        self.human_hand = []
        self.ai_hand = []
        
        # Face-up cards (cards that have been guessed correctly)
        self.human_revealed = []
        self.ai_revealed = []
        
        # Game history
        self.history = []
        
        # Log file for AI interactions
        self.log_file = "davinci_code_ai_log.txt"
        with open(self.log_file, "w") as f:
            f.write("DA VINCI CODE GAME - AI INTERACTION LOG\n")
            f.write("="*50 + "\n\n")
        
        # Initialize game
        self.deal_initial_cards()
    
    def card_value(self, card):
        """Returns the numerical value of a card for sorting purposes"""
        # Wildcard handling
        if card[1] == '-':
            return -1 if card[0] == 'B' else -0.5  # B- is smallest, W- is second smallest
        
        # For numbered cards: number is primary, color is secondary
        num = int(card[1:])
        color_value = 0 if card[0] == 'B' else 0.5  # Black cards are slightly smaller than white cards
        return num + color_value
    
    def deal_initial_cards(self):
        """Deal 4 cards to each player and sort them"""
        for _ in range(4):
            self.human_hand.append(self.deck.pop())
            self.ai_hand.append(self.deck.pop())
        
        # Sort hands in ascending order
        self.human_hand.sort(key=self.card_value)
        self.ai_hand.sort(key=self.card_value)
        
        # Initialize revealed status
        self.human_revealed = [False] * len(self.human_hand)
        self.ai_revealed = [False] * len(self.ai_hand)
    
    def draw_card(self):
        """Draw a card from the deck"""
        if not self.deck:
            return None
        return self.deck.pop()
    
    def insert_card(self, hand, revealed_list, card, reveal=True):
        """Insert a card into a hand in the correct position and update revealed status"""
        # Add the new card
        hand.append(card)
        hand.sort(key=self.card_value)
        
        # Get the position of the newly inserted card
        position = hand.index(card)
        
        # Create a new revealed list
        new_revealed = revealed_list.copy()
        new_revealed.insert(position, reveal)  # Use the reveal parameter
        
        return position, new_revealed
    
    def display_game_state(self):
        """Display the current game state"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*50)
        print("THE DA VINCI CODE GAME")
        print("="*50 + "\n")
        
        # Display AI's hand
        print("AI's hand:")
        for i, card in enumerate(self.ai_hand):
            if self.ai_revealed[i]:
                print(f"[{card}]", end=" ")
            else:
                # Show color but hide number
                print(f"[{card[0]}?]", end=" ")
        print("\n")
        #print(self.ai_hand[0])
        # Display remaining cards in deck
        print(f"Cards remaining in deck: {len(self.deck)}")
        print("-"*50)
        
        # Display human's hand
        print("Your hand:")
        for i, card in enumerate(self.human_hand):
            if self.human_revealed[i]:
                print(f"[{card}]", end=" ")
            else:
                print(f"[{card}]*", end=" ")  # * indicates hidden from AI but visible to human
        print("\n")
        
        # Display recent history
        print("ALL moves:")
        start = max(0, len(self.history) - 5)
        for entry in self.history:
            print(f"- {entry}")
        print("-"*50 + "\n")
    
    def generate_ai_prompt(self, drawn_card=None, has_correct_guess=False):
        """Generate a detailed prompt for the AI"""
        prompt = "You are playing the card game 'The Da Vinci Code' against a human player. Here's the current game state:\n\n"
        
        # Explain the rules
        prompt += "GAME RULES:\n"
        prompt += "- Cards are either Black (B) or White (W) followed by a number 0-11 or wildcard '-'\n"
        prompt += "- Cards are arranged by number first, then by color (B3, W3, B4, W4)\n"
        prompt += "- For the same number, Black cards are smaller than White cards (B5 < W5)\n"
        prompt += "- Wildcards (B-, W-) are the smallest cards, with B- < W-\n"
        prompt += "- On your turn, you draw a card and then decide to guess one of your opponent's hidden cards or place the card\n"
        prompt += "- If you guess correctly, the card is revealed and you can choose to guess again or place your drawn card (it will not be revealed)\n"
        prompt += "- If you guess incorrectly or choose to place without guessing correctly, you must place your drawn card in your hand (it becomes revealed)\n"
        prompt += "- The goal is to reveal all your opponent's cards first\n\n"
        
        # Game state
        prompt += "CURRENT GAME STATE:\n"
        
        # AI's hand (what it knows)
        prompt += "Your hand (AI): "
        for i, card in enumerate(self.ai_hand):
            if self.ai_revealed[i]:
                prompt += f"[{card}](revealed) "
            else:
                prompt += f"[{card}](hidden) "
        prompt += "\n\n"
        
        # Human's hand (what AI can see)
        prompt += "Opponent's hand (Human): "
        for i, card in enumerate(self.human_hand):
            if self.human_revealed[i]:
                prompt += f"[{self.human_hand[i]}](revealed) "
            else:
                # Show color but hide number
                prompt += f"[{self.human_hand[i][0]}?](hidden) "
        prompt += "\n\n"
        
        # Compile list of all cards that have been seen
        visible_cards = []
        
        # Add revealed cards from both hands
        for i, revealed in enumerate(self.ai_revealed):
            if revealed:
                visible_cards.append(self.ai_hand[i])
        
        for i, revealed in enumerate(self.human_revealed):
            if revealed:
                visible_cards.append(self.human_hand[i])
        
        # Add cards that were placed from incorrect guesses or explicit placement
        for entry in self.history:
            if "placed" in entry and "in their hand" in entry:
                parts = entry.split()
                for part in parts:
                    if part.startswith(('B', 'W')) and (part[1] == '-' or part[1:].isdigit()):
                        if part not in visible_cards:
                            visible_cards.append(part)
        
        prompt += f"Cards that have been revealed so far: {', '.join(visible_cards) if visible_cards else 'None'}\n"
        prompt += f"Cards remaining in deck: {len(self.deck)}\n\n"
        
        # Game history
        prompt += "GAME HISTORY:\n"
        start = max(0, len(self.history) - 5)  # Show last 5 moves for better context
        for entry in self.history[start:]:
            prompt += f"- {entry}\n"
        prompt += "\n"
        
        # Current action
        if drawn_card:
            prompt += f"You just drew: {drawn_card}\n\n"
            
            prompt += "Your task is to decide your move. You have two options:\n"
            prompt += "1. Guess one of your opponent's hidden cards (specify the position and the card you think it is)\n"
            if has_correct_guess:
                prompt += "2. Place your drawn card in your hand (it will not be revealed)\n\n"
            else:
                prompt += "2. Place your drawn card in your hand (it will be revealed)\n\n"
            
            prompt += "Based on the game state, make a strategic decision. Consider:\n"
            prompt += "- What can you infer from the game history?\n"
            prompt += "- What can you infer from your opponent's cards?\n\n"
            # give ai valid positions hint
            valid_positions =[i for i, revealed in enumerate(self.human_revealed) if not revealed]
            prompt += f"Valid positions for your opponent's hidden cards are: {valid_positions}\n"
            prompt += "Respond with EXACTLY ONE of these formats:\n"
            prompt += "- GUESS: [position] [card] (e.g., 'GUESS: 2 W7' to guess that the opponent's **third** card is White 7)\n"
            prompt += "- PLACE (to place your drawn card in your hand)\n"
        else:
            prompt += "It's your turn. You will draw a card and then decide your next move.\n"
        
        return prompt
    
    def log_ai_interaction(self, prompt, response):
        """Log AI prompt and response to file"""
        with open(self.log_file, "a") as f:
            f.write(f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n")
            f.write("PROMPT:\n")
            f.write(prompt + "\n\n")
            f.write("RESPONSE:\n")
            f.write(response + "\n\n")
            f.write("-"*50 + "\n\n")
    
    def ai_turn(self):
        """Handle the AI's turn"""
        self.display_game_state()
        print("AI's turn...")
        time.sleep(1)
        
        # AI draws a card
        drawn_card = self.draw_card()
        
        self.history.append(f"AI drew a card")
        
        continue_turn = True
        while continue_turn:
            # Generate prompt for AI
            prompt = self.generate_ai_prompt(drawn_card)
            
            # Get AI's decision
            print("AI is thinking...")
            


            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    }
                ],
                model='deepseek-reasoner',
            )
            
            ai_response = chat_completion.choices[0].message.content
            print(f"AI decision: {ai_response}")
            
            # Log the interaction
            self.log_ai_interaction(prompt, ai_response)
            
            # Parse AI's decision
            if "GUESS:" in ai_response:
                try:
                    # Extract position and card guess
                    guess_parts = ai_response.split("GUESS:")[1].strip().split()
                    position = int(guess_parts[0])
                    card_guess = guess_parts[1]
                    
                    # Validate position
                    if position < 0 or position >= len(self.human_hand) or self.human_revealed[position]:
                        print("Invalid guess position. AI will place the drawn card.")
                        position, self.ai_revealed = self.insert_card(self.ai_hand, self.ai_revealed, drawn_card)
                        self.history.append(f"AI placed {drawn_card} in their hand (invalid guess)")
                        continue_turn = False
                    else:
                        # Check if guess is correct
                        actual_card = self.human_hand[position]
                        if card_guess == actual_card:
                            print(f"AI correctly guessed your card at position {position} is {card_guess}!")
                            self.human_revealed[position] = True
                            self.history.append(f"AI correctly guessed {card_guess} at position {position}")
                            
                            # Check if AI has won
                            if all(self.human_revealed):
                                print("AI has revealed all your cards and wins!")
                                return False
                                
                            # AI can continue guessing
                            input("Press Enter to continue...")
                        else:
                            print(f"AI incorrectly guessed your card at position {position} is {card_guess}.")
                            # AI must place its drawn card
                            position, self.ai_revealed = self.insert_card(self.ai_hand, self.ai_revealed, drawn_card)
                            self.history.append(f"AI guessed incorrectly (it guessed {position}-th card is {card_guess}) and placed {drawn_card} in their hand")
                            continue_turn = False
                except Exception as e:
                    print(f"Error parsing AI's guess: {e}")
                    print("AI will place the drawn card.")
                    position, self.ai_revealed = self.insert_card(self.ai_hand, self.ai_revealed, drawn_card)
                    self.history.append(f"AI placed {drawn_card} in their hand (parsing error)")
                    continue_turn = False
            else:
                # AI chooses to place the card
                position, self.ai_revealed = self.insert_card(self.ai_hand, self.ai_revealed, drawn_card)
                self.history.append(f"AI placed {drawn_card} in their hand")
                continue_turn = False
        
        return True
    
    def human_turn(self):
        """Handle the human player's turn"""
        self.display_game_state()
        print("Your turn!")
        # Human draws a card
        drawn_card = self.draw_card()

        
        print(f"You drew: {drawn_card}")
        self.history.append(f"Human drew a card")
        
        has_correct_guess = False  # 追踪是否至少猜对一次
        
        while True:
            self.display_game_state()
            print(f"You drew: {drawn_card}")
            
            if has_correct_guess:
                # 猜对后，提供猜测或放置（不公开）的选项
                action = input("Do you want to guess again or place the card without revealing? (guess/place): ").lower()
            else:
                # 初始选择：猜测或放置（公开）
                action = input("Do you want to guess a card or place your drawn card (it will be revealed)? (guess/place): ").lower()
            
            if action == "guess":
                valid_positions = [i for i, revealed in enumerate(self.ai_revealed) if not revealed]
                if not valid_positions:
                    print("All AI cards are already revealed. You must place your drawn card.")
                    action = "place"
                else:
                    print(f"Valid positions to guess: {valid_positions}")
                    try:
                        position = int(input("Enter the position to guess (0-based index): "))
                        if position not in valid_positions:
                            print("Invalid position. Try again.")
                            continue
                        
                        card_guess = input("Enter your guess (e.g., B5, W3, B-, W-): ").upper()
                        if not (card_guess.startswith(('B', 'W')) and 
                            (card_guess[1] == '-' or (card_guess[1:].isdigit() and 0 <= int(card_guess[1:]) <= 11))):
                            print("Invalid card format. Try again.")
                            continue
                        
                        actual_card = self.ai_hand[position]
                        if card_guess == actual_card:
                            print(f"Correct! The card at position {position} is {card_guess}!")
                            self.ai_revealed[position] = True
                            self.history.append(f"Human correctly guessed {card_guess} at position {position}")
                            has_correct_guess = True
                            
                            if all(self.ai_revealed):
                                print("You have revealed all AI's cards and win!")
                                return False
                        else:
                            print(f"Incorrect! The card at position {position} is not {card_guess}.")
                            position, self.human_revealed = self.insert_card(self.human_hand, self.human_revealed, drawn_card, reveal=True)
                            self.history.append(f"Human guessed incorrectly (guessed {position}-th card is {card_guess}) and placed {drawn_card} in their hand")
                            break
                    except ValueError:
                        print("Invalid input. Try again.")
                        continue
            
            elif action == "place":
                if has_correct_guess:
                    # 猜对后选择放置，不公开
                    position, self.human_revealed = self.insert_card(self.human_hand, self.human_revealed, drawn_card, reveal=False)
                    self.history.append(f"Human placed a card in their hand without revealing")
                else:
                    # 未猜对直接放置，公开
                    position, self.human_revealed = self.insert_card(self.human_hand, self.human_revealed, drawn_card, reveal=True)
                    self.history.append(f"Human placed {drawn_card} in their hand")
                break
            
            else:
                print("Invalid action. Please type 'guess' or 'place'.")
        
        return True
    
    def play_game(self):
        """Main game loop"""
        print("Welcome to The Da Vinci Code!")
        print("You will play against an AI opponent.")
        print("Your goal is to guess all of the AI's cards before it guesses yours.")
        input("Press Enter to start the game...")
        
        # Determine first player randomly
        current_player = random.choice(["human", "ai"])
        print(f"{current_player.capitalize()} goes first!")
        
        game_active = True
        while game_active:
            if current_player == "human":
                game_active = self.human_turn()
                current_player = "ai"
            else:
                game_active = self.ai_turn()
                current_player = "human"
            
            if game_active:
                input("Press Enter to continue to the next turn...")
        
        # Game over
        self.display_game_state()
        print("Game Over!")
        
        # Determine winner
        if all(self.ai_revealed):
            print("You win! You revealed all of the AI's cards!")
        elif all(self.human_revealed):
            print("AI wins! It revealed all of your cards!")
        else:
            print("The game ended in a draw.")

# Start the game
if __name__ == "__main__":
    game = DaVinciCodeGame()
    game.play_game()