import time
import tkinter as tk


class AnimationTest:
    def __init__(self, root):
        self.root = root
        self.root.title("2D Animation Test")

        # Create canvas
        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack(padx=10, pady=10)

        # Add some instructions
        self.label = tk.Label(root, text="You should see a bouncing ball")
        self.label.pack(pady=10)

        # Animation parameters
        self.ball_radius = 20
        self.ball_x = 200
        self.ball_y = 50
        self.velocity_y = 0
        self.gravity = 0.5
        self.bounce = -0.8
        self.floor = 350

        # Draw the floor
        self.canvas.create_line(50, self.floor, 350, self.floor, width=2)

        # Draw the ball
        self.ball = self.canvas.create_oval(
            self.ball_x - self.ball_radius,
            self.ball_y - self.ball_radius,
            self.ball_x + self.ball_radius,
            self.ball_y + self.ball_radius,
            fill="blue",
            outline="black",
        )

        # Start animation
        self.last_time = time.time()
        self.animate()

    def animate(self):
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        # Update physics
        self.velocity_y += self.gravity * 60 * delta_time
        self.ball_y += self.velocity_y * 60 * delta_time

        # Bounce off the floor
        if self.ball_y > self.floor - self.ball_radius:
            self.ball_y = self.floor - self.ball_radius
            self.velocity_y *= self.bounce
            # Stop if the bounce is very small
            if abs(self.velocity_y) < 0.5:
                self.velocity_y = 0

        # Update ball position
        self.canvas.coords(
            self.ball,
            self.ball_x - self.ball_radius,
            self.ball_y - self.ball_radius,
            self.ball_x + self.ball_radius,
            self.ball_y + self.ball_radius,
        )

        # Continue animation if the ball is still moving
        if self.velocity_y != 0 or self.ball_y < self.floor - self.ball_radius:
            self.root.after(16, self.animate)  # ~60 FPS
        else:
            self.label.config(text="Animation complete! Click the ball to restart.")
            self.canvas.tag_bind(self.ball, "<Button-1>", self.restart_animation)

    def restart_animation(self, event=None):
        self.ball_y = 50
        self.velocity_y = 0
        self.label.config(text="Animation restarted!")
        self.canvas.tag_unbind(self.ball, "<Button-1>")
        self.animate()


def main():
    root = tk.Tk()
    AnimationTest(root)

    # Center the window
    window_width = 420
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
