import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Tkinter Test")

    label = tk.Label(root, text="If you can see this, Tkinter is working!")
    label.pack(padx=20, pady=20)

    button = tk.Button(root, text="Click me to exit", command=root.quit)
    button.pack(pady=10)

    print("Tkinter window should open now...")
    root.mainloop()
    print("Tkinter test complete!")


if __name__ == "__main__":
    main()
