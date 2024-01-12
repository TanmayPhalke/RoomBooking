import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar, DateEntry  # Ensure tkcalendar is installed
import sqlite3
from ttkthemes import ThemedTk
from datetime import datetime, timedelta

class RoomBookingApp:
    def __init__(self, root):
        self.root = ThemedTk(theme="equilux")
        self.root.title("Room Booking App")
        self.root.geometry("800x600")  # Set your desired window size

        # Configure title bar
        title_frame = ttk.Frame(self.root)
        title_frame.pack(side="top", fill="both", expand=True)

        # Title label
        title_label = ttk.Label(title_frame, text="Room Booking App", font=("Helvetica", 24, "bold"), foreground="cyan")
        title_label.pack(pady=20)

        self.selected_room = None
        self.booking_data = {}

        with sqlite3.connect("C:\\Users\\tanyp\\Desktop\\room_booking.db") as self.conn:
            self.create_tables()

        self.style = ttk.Style()
        self.style.configure('TButton', padding=5, font=('Helvetica', 12))
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TEntry', font=('Helvetica', 12))

        # Room Selection Screen
        room_frame = ttk.Frame(self.root)
        room_frame.pack(side="top", fill="both", expand=True)

        self.room_label = ttk.Label(room_frame, text="Select a Room:", font=('Helvetica', 14))
        self.room_label.grid(row=0, column=0, pady=(10, 5), sticky="e")

        rooms = self.get_room_names()
        self.room_combobox = ttk.Combobox(room_frame, values=rooms, state="readonly", font=('Helvetica', 12))
        self.room_combobox.grid(row=0, column=1, pady=(10, 5), sticky="w")

        self.show_calendar_button = ttk.Button(room_frame, text="Show Booking Calendar", command=self.show_booking_calendar, style="TButton")
        self.show_calendar_button.grid(row=0, column=2, pady=(10, 5), sticky="e")

        # Availability Calendar Container
        availability_frame = ttk.Frame(self.root)
        availability_frame.pack(side="top", fill="both", expand=True)

        self.availability_container = ttk.Frame(availability_frame)
        self.availability_container.pack(side="left", padx=10, pady=5, fill="both", expand=True)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        calendar_width = int(0.4 * screen_width)
        calendar_height = int(0.4 * screen_height)

        self.availability_calendar = Calendar(self.availability_container, selectmode="day", date_pattern="yyyy-mm-dd", showweeknumbers=False, font=('Helvetica', 12), width=calendar_width, height=calendar_height)
        self.availability_calendar.pack(pady=(10, 5), padx=5)

        self.availability_calendar_button = ttk.Button(self.availability_container, text="Check Availability", command=self.check_availability, style="TButton")
        self.availability_calendar_button.pack(pady=(5, 10))

        # Booking Form Container
        booking_form_frame = ttk.Frame(self.root)
        booking_form_frame.pack(side="top", fill="both", expand=True)

        self.booking_form_container = ttk.Frame(booking_form_frame)
        self.create_booking_form()
        self.booking_form_container.pack(side="right", padx=10, pady=5, fill="both", expand=True)

        for i in range(1, len(rooms) + 1):
            self.root.grid_rowconfigure(i + 3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

    # ... (remaining methods remain the same)

    def get_room_names(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT RoomName FROM Rooms')
        rooms = cursor.fetchall()
        return [room[0] for room in rooms]

    def show_booking_calendar(self):
        self.selected_room = self.room_combobox.get()
        self.populate_availability_calendar()

        self.availability_container.grid(row=2, column=0, columnspan=3, rowspan=len(self.get_room_names()), padx=10, pady=5, sticky="nsew")
        self.availability_calendar.grid(row=0, column=0, pady=(10, 5), padx=5)
        self.availability_calendar_button.grid(row=1, column=0, pady=(5, 10))
        self.room_label.grid_forget()

    def populate_availability_calendar(self):
        room_name = self.selected_room

        if not room_name:
            messagebox.showwarning("Select a Room", "Please select a room first.")
            return

        # Fetch booked dates for the selected room from the database
        booked_dates = self.get_booked_dates(room_name)

        # Clear existing tags
        self.availability_calendar._calendar.tag_delete("booked")

        # Tag booked dates
        for date in booked_dates:
            tag = f"{date}"
            self.availability_calendar._calendar.tag_configure(tag, background="red")
            self.availability_calendar._calendar.tag_add("booked", f"{date}")

        self.availability_calendar.update_idletasks()

    def get_booked_dates(self, room_name):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT BookingFromDate, BookingToDate
            FROM Bookings
            JOIN Rooms ON Bookings.RoomID = Rooms.RoomID
            WHERE Rooms.RoomName = ?
        ''', (room_name,))

        booked_dates = []
        for row in cursor.fetchall():
            start_date, end_date = row
            current_date = datetime.strptime(start_date, "%Y-%m-%d")
            while current_date <= datetime.strptime(end_date, "%Y-%m-%d"):
                booked_dates.append(current_date)
                current_date += timedelta(days=1)

        return booked_dates

    def check_availability(self):
        selected_date = self.availability_calendar.get_date()
        if selected_date:
            if selected_date in self.availability_calendar._calendar._tags:
                messagebox.showinfo("Availability", f"The room is Booked on {selected_date}")
            else:
                messagebox.showinfo("Availability", f"The room is Available on {selected_date}")
        else:
            messagebox.showwarning("Invalid Date", "Please select a date.")

    def create_booking_form(self):
        ttk.Label(self.booking_form_container, text="Booking Form", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        fields = ["Room", "Number of Guests", "Food Preference", "Special Requirement", "From Date", "To Date", "Guest Name", "Guest Rank", "Guest Unit"]

        # Create a room dropdown
        rooms = self.get_room_names()
        self.room_combobox_booking = ttk.Combobox(self.booking_form_container, values=rooms, state="readonly", font=('Helvetica', 12))
        self.room_combobox_booking.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        for row, field in enumerate(fields[1:], start=2):  # Skip the room in fields
            ttk.Label(self.booking_form_container, text=field + ":").grid(row=row, column=0, padx=10, pady=5, sticky="e")

            if field.lower().replace(" ", "_") in ["from_date", "to_date"]:
                date_entry = DateEntry(self.booking_form_container, selectmode="day", date_pattern="yyyy-mm-dd")
                date_entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                self.booking_data[field.lower().replace(" ", "_")] = date_entry
            else:
                entry = ttk.Entry(self.booking_form_container)
                entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
                self.booking_data[field.lower().replace(" ", "_")] = entry

        ttk.Button(self.booking_form_container, text="Submit Booking", command=self.submit_booking).grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

    def submit_booking(self):
        for field, entry_widget in self.booking_data.items():
            value = entry_widget.get()
            if not value:
                messagebox.showwarning("Missing Information", f"Please fill in the {field.replace('_', ' ')} field.")
                return

        room_id = self.get_room_id_by_name(self.room_combobox_booking.get())

        if not room_id:
            messagebox.showwarning("Room not found", "Selected room not found in the database.")
            return

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO Users (Name, Rank, Unit) VALUES (?, ?, ?)
        ''', (self.booking_data["guest_name"].get(), self.booking_data["guest_rank"].get(), self.booking_data["guest_unit"].get()))
        user_id = cursor.lastrowid

        cursor.execute('''
            INSERT INTO Bookings (RoomID, UserID, NumberOfGuests, FoodPreference, SpecialRequirement, BookingFromDate, BookingToDate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (room_id, user_id, int(self.booking_data["number_of_guests"].get()), self.booking_data["food_preference"].get(),
              self.booking_data["special_requirement"].get(), self.booking_data["from_date"].get(), self.booking_data["to_date"].get()))

        self.conn.commit()

        messagebox.showinfo("Booking Submitted", "Booking submitted successfully!")
        self.reset_form()

    def get_room_id_by_name(self, room_name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT RoomID FROM Rooms WHERE RoomName = ?', (room_name,))
        room_id = cursor.fetchone()
        return room_id[0] if room_id else None

    def reset_form(self):
        for entry_widget in self.booking_data.values():
            if isinstance(entry_widget, DateEntry):
                entry_widget.set_date(datetime.now())
            else:
                entry_widget.delete(0, tk.END)

        self.booking_form_container.grid_forget()
        self.room_combobox_booking.set('')
        self.room_label.grid(row=1, column=0, pady=(10, 5), sticky="e")

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Rooms (
                RoomID INTEGER PRIMARY KEY,
                RoomNumber INTEGER UNIQUE NOT NULL,
                RoomName TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                UserID INTEGER PRIMARY KEY,
                Name TEXT NOT NULL,
                Rank TEXT NOT NULL,
                Unit TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Bookings (
                BookingID INTEGER PRIMARY KEY,
                RoomID INTEGER,
                UserID INTEGER,
                NumberOfGuests INTEGER NOT NULL,
                FoodPreference TEXT,
                SpecialRequirement TEXT,
                BookingFromDate DATE NOT NULL,
                BookingToDate DATE NOT NULL,
                FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
                FOREIGN KEY (UserID) REFERENCES Users(UserID)
            )
        ''')
        self.conn.commit()

if __name__ == "__main__":
    root = ThemedTk(theme="plastik")
    app = RoomBookingApp(root)
    root.mainloop()
