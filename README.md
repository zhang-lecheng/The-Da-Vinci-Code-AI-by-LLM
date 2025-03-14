# The-Da-Vinci-Code-AI-by-LLM （达芬奇密码AI）

[The board game: da vinci code](https://boardgamegeek.com/boardgame/8946/da-vinci-code) .

you can use (after write your api in the `main.py`)

```bash
python main.py
```

to start a **1 vs 1** game against AI (the default model is Deepseek-R1).

---

todo:

1. modify prompts
2. webui
3. multiplayer
4. AI vs AI

---

r1-zero on this.

train a based ai model to get score of choice(相当于爆算一个概率)

cold start llm + rl


---

easy version

```
- Cards are either Black (B) or White (W) followed by a number 0-11 or wildcard '-'
- Cards are arranged by number first, then by color (B3, W3, B4, W4)
- For the same number, Black cards are smaller than White cards (B5 < W5)
- Wildcards (B-, W-) are the smallest cards, with B- < W-
- You should guess one of your opponent's hidden cards ()

Please output your answer of these formats, enclosed within a boxed comment:
$$
boxed{
2 \ W7
}
$$
is to guess that the opponent's **third** card is W7.

Your hand:

W0 < W5 < W6 < B7 < W8

Your opponent's hand:

W? < B? < B? < W? < W11
```
