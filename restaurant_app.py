import tkinter as tk
from tkinter import messagebox, simpledialog
import pandas as pd
import sqlite3
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize NLTK
nltk.download('vader_lexicon')

# 1. DATA INITIALIZATION & DATABASE SETUP
FOOD_ITEMS = [
    'Idli', 'Dosa', 'Vada', 'Roti', 'Meals', 'Veg Biryani', 
    'Egg Biryani', 'Mutton Biryani', 'Ice Cream', 'Noodles', 
    'Orange Juice', 'Mango Juice'
]

def init_db():
    conn = sqlite3.connect('restaurant_feedback.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reviews 
                      (id INTEGER PRIMARY KEY, item TEXT, review TEXT, sentiment TEXT)''')
    cursor.execute("SELECT COUNT(*) FROM reviews")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('Ice Cream', 'Very delicious and creamy', 'Positive'),
            ('Ice Cream', 'Too melted and sweet', 'Negative'),
            ('Mutton Biryani', 'Spicy and tender meat', 'Positive')
        ]
        cursor.executemany("INSERT INTO reviews (item, review, sentiment) VALUES (?,?,?)", sample_data)
    conn.commit()
    conn.close()

def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(text)
    return "Positive" if score['compound'] > 0 else "Negative"

class RestaurantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NLP Food Analysis System")
        self.root.geometry("400x400")
        
        # --- PASSWORD CHANGED HERE ---
        self.owner_code = "1234" 
        
        self.main_menu()

    def main_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="Welcome to Food Analytics", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Customer Portal", width=20, command=self.customer_view).pack(pady=10)
        tk.Button(self.root, text="Owner Portal", width=20, command=self.verify_owner).pack(pady=10)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def customer_view(self):
        self.clear_screen()
        tk.Label(self.root, text="Select Food Item:").pack(pady=5)
        self.selected_item = tk.StringVar(self.root)
        self.selected_item.set(FOOD_ITEMS[0])
        tk.OptionMenu(self.root, self.selected_item, *FOOD_ITEMS).pack()
        tk.Label(self.root, text="Write your review:").pack(pady=5)
        self.review_text = tk.Text(self.root, height=5, width=30)
        self.review_text.pack()
        tk.Button(self.root, text="Submit Review", command=self.submit_review).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack()

    def submit_review(self):
        item = self.selected_item.get()
        text = self.review_text.get("1.0", tk.END).strip()
        if text:
            sentiment = analyze_sentiment(text)
            conn = sqlite3.connect('restaurant_feedback.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO reviews (item, review, sentiment) VALUES (?, ?, ?)", (item, text, sentiment))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Review analyzed as {sentiment} and saved!")
            self.customer_view()
        else:
            messagebox.showwarning("Error", "Review cannot be empty")

    def verify_owner(self):
        code = simpledialog.askstring("Security", "Enter Unique Global Owner Code:", show='*')
        if code == self.owner_code:
            self.owner_dashboard()
        else:
            messagebox.showerror("Access Denied", "Incorrect Ownership Code!")

    def owner_dashboard(self):
        self.clear_screen()
        tk.Label(self.root, text="Owner Dashboard", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="View Analytics (Table)", width=25, command=self.view_data).pack(pady=5)
        tk.Button(self.root, text="Clear/Clean Data", width=25, command=self.clean_data).pack(pady=5)
        tk.Button(self.root, text="Logout", width=25, command=self.main_menu).pack(pady=5)

    def view_data(self):
        conn = sqlite3.connect('restaurant_feedback.db')
        df = pd.read_sql_query("SELECT * FROM reviews", conn)
        conn.close()

        if df.empty:
            messagebox.showinfo("Data", "No reviews yet.")
            return

        summary = df.groupby(['item', 'sentiment']).size().unstack(fill_value=0)
        
        report_win = tk.Toplevel(self.root)
        report_win.title("Business Intelligence Report")
        report_win.geometry("450x350")

        header = tk.Label(report_win, text="Food Performance Report", font=("Arial", 12, "bold"))
        header.pack(pady=10)

        # MONOSPACED FONT forces the 0 and 1 to line up perfectly
        display_text = tk.Text(report_win, font=("Courier", 10), height=12, width=50)
        display_text.insert(tk.END, summary.to_string())
        display_text.config(state=tk.DISABLED)
        display_text.pack(padx=20, pady=10)

        tk.Button(report_win, text="Close", command=report_win.destroy).pack(pady=5)

    def clean_data(self):
        confirm = messagebox.askyesno("Clean Data", "Clear all history to observe new performance?")
        if confirm:
            conn = sqlite3.connect('restaurant_feedback.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reviews")
            conn.commit()
            conn.close()
            messagebox.showinfo("Cleaned", "Database cleared successfully.")

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = RestaurantApp(root)
    root.mainloop()
