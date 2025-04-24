import tkinter as tk
from tkinter import messagebox

class TicTacToe3D:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Tic-Tac-Toe with Lattice Visualizer")
        self.tabuleiro = [[[None for _ in range(3)] for _ in range(3)] for _ in range(3)]
        self.turn = "X"
        self.score = {"X": 0, "O": 0, "Ties": 0}
        self.moves = 0

        self.setup_ui()
        self.update_score()

    def setup_ui(self):
        self.frame_score = tk.Frame(self.root)
        self.frame_score.pack()

        self.score_label = tk.Label(
            self.frame_score, text="Score: X 0 vs O 0 | Ties: 0", font=("Arial", 14)
        )
        self.score_label.pack()

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(side="left", padx=100)

        self.frames_board = []
        for layer in range(3):
            frame = tk.LabelFrame(self.board_frame, text=f"Layer {layer + 1}", padx=5, pady=5)
            frame.grid(row=0, column=layer, padx=5)
            self.frames_board.append(frame)
            for row in range(3):
                for col in range(3):
                    button = tk.Button(
                        frame, text="", font=("Arial", 20), width=4, height=2,
                        command=lambda l=layer, r=row, c=col: self.play(l, r, c)
                    )
                    button.grid(row=row, column=col)
                    self.tabuleiro[layer][row][col] = button

        self.visualizer = tk.Canvas(self.root, width=500, height=500, bg="white")
        self.visualizer.pack(side="right", padx=10)

        self.reset_button = tk.Button(
            self.root, text="Restart Game", command=self.restart_game, font=("Arial", 12)
        )
        self.reset_button.pack(pady=10)

    def update_score(self):
        self.score_label.config(
            text=f"Score: X {self.score['X']} vs O {self.score['O']} | Ties: {self.score['Ties']}"
        )

    def play(self, layer, row, col):
        button = self.tabuleiro[layer][row][col]
        if button["text"] == "":
            button.config(text=self.turn)
            self.moves += 1
            self.update_visualizer()

            if self.check_winner():
                self.score[self.turn] += 1
                self.end_game(f"Congratulations! Player ({self.turn}) wins!")
                return

            if self.moves == 27:
                self.score["Ties"] += 1
                self.end_game("It's a tie! No one wins.")
                return

            self.turn = "O" if self.turn == "X" else "X"
        else:
            messagebox.showwarning("Invalid Move", "This cell is already occupied!")

    def update_visualizer(self):
        self.visualizer.delete("all")
        size = 50
        gap = 150
        offset_x = 100
        offset_y = 100

        for z in range(3):
            for y in range(3):
                for x in range(3):
                    cx = offset_x + x * gap + z * 10
                    cy = offset_y + y * gap - z * 10
                    self.visualizer.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="gray")
                    cell = self.tabuleiro[z][y][x].cget("text")
                    if cell:
                        color = "black" if cell == "X" else "red"
                        self.visualizer.create_text(cx, cy - 10, text=cell, font=("Arial", 16), fill=color)

        for z in range(3):
            for y in range(3):
                for x in range(3):
                    start = self._coords(x, y, z, offset_x, offset_y, gap)
                    if x < 2:
                        end = self._coords(x+1, y, z, offset_x, offset_y, gap)
                        self.visualizer.create_line(*start, *end, fill="lightgray")
                    if y < 2:
                        end = self._coords(x, y+1, z, offset_x, offset_y, gap)
                        self.visualizer.create_line(*start, *end, fill="lightgray")
                    if z < 2:
                        end = self._coords(x, y, z+1, offset_x, offset_y, gap)
                        self.visualizer.create_line(*start, *end, fill="lightgray")

    def _coords(self, x, y, z, offset_x, offset_y, gap):
        cx = offset_x + x * gap + z * 10
        cy = offset_y + y * gap - z * 10
        return (cx, cy)

    def check_winner(self):
        for layer in range(3):
            for row in range(3):
                if all(self.tabuleiro[layer][row][col].cget("text") == self.turn for col in range(3)):
                    return True
            for col in range(3):
                if all(self.tabuleiro[layer][row][col].cget("text") == self.turn for row in range(3)):
                    return True
            if all(self.tabuleiro[layer][i][i].cget("text") == self.turn for i in range(3)):
                return True
            if all(self.tabuleiro[layer][i][2 - i].cget("text") == self.turn for i in range(3)):
                return True

        for row in range(3):
            for col in range(3):
                if all(self.tabuleiro[layer][row][col].cget("text") == self.turn for layer in range(3)):
                    return True

        if all(self.tabuleiro[i][i][i].cget("text") == self.turn for i in range(3)):
            return True
        if all(self.tabuleiro[i][i][2 - i].cget("text") == self.turn for i in range(3)):
            return True
        if all(self.tabuleiro[i][2 - i][i].cget("text") == self.turn for i in range(3)):
            return True
        if all(self.tabuleiro[i][2 - i][2 - i].cget("text") == self.turn for i in range(3)):
            return True

        return False

    def end_game(self, message):
        self.update_score()
        for layer in range(3):
            for row in range(3):
                for col in range(3):
                    self.tabuleiro[layer][row][col].config(state="disabled")
        messagebox.showinfo("Game Over", message)

    def restart_game(self):
        self.turn = "X"
        self.moves = 0
        for layer in range(3):
            for row in range(3):
                for col in range(3):
                    self.tabuleiro[layer][row][col].config(text="", state="normal")
        self.update_visualizer()

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = TicTacToe3D()
    game.start()