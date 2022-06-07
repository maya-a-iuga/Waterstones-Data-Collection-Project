import tkinter as tk
import requests
from project_module_2_GUI_version import Run_Scraper


def run_app():

    """ This function takes the user input from the user interface and
    feeds it to the Run_Scraper class for initilisation of an instance"""

    user_number_pages = int(number_pages_entry.get())
    user_postcode = str(postcode_entry.get())
    user_category = str(category_menu.get())
    user_subcategory = str(subcategory_menu.get())
    user_headless = str(headless_menu.get())
   
    waterstones = Run_Scraper(user_category, user_subcategory, user_headless)
    if waterstones.subcategory_flag == "no":
        waterstones.scrape_individual_subcategories(user_number_pages, user_postcode)
    # if you want to remove duplicates book list
    elif waterstones.subcategory_flag == "yes":
        waterstones.scrape_across_subcategories(user_number_pages, user_postcode)


def close_app():

    """ When called this function will close the user interface"""

    window.destroy()


def caps_postcode(event):

    """ This function capitalises every letter in the postcode"""

    postcode1.set(postcode1.get().upper())


def check_postcode(event):

    """ This function will check postcode input corresponds to a 
    real postcode, otherwise it will randomly generate a new one."""

    postcode_check = postcode1.get()
    postcode_status = requests.get('https://api.postcodes.io/postcodes/' + postcode_check).json()["status"]
    if postcode_status == 404:
        postcode1.set(requests.get('https://api.postcodes.io/random/postcodes').json()["result"]["postcode"])

#initialise window
window = tk.Tk()

window.title("Book Scraper")
#do not allow for resizing window
window.resizable("false", "false")
window.geometry("600x325")

#build frames & arrange them in a grid
frame_header = tk.Frame(window, borderwidth=2, pady =2)
centre_frame = tk.Frame(window, borderwidth=2, pady =5)
bottom_frame = tk.Frame(window, borderwidth=2, pady =5)
frame_header.grid(row = 0, column = 0)
centre_frame.grid(row = 1, column = 0)
bottom_frame.grid(row = 2, column = 0)

#header frame initialisation
header = tk.Label(frame_header, text = "A reader lives a thousand lives before he dies. \n ~A book webscraping tool", 
bg="#CDB5CD", fg="#F5F5F5", height = '7', width='54', font=("Helvetica 18 italic"))
header.grid(row = 0, column = 0)

#centre frame initialisation
frame_main_1 = tk.Frame(centre_frame, borderwidth = 2, relief = 'sunken')
frame_main_2 = tk.Frame(centre_frame, borderwidth = 2, relief = 'sunken', bg = "#CDB5CD")

#allow for user input
category_menu = tk.StringVar()
category_menu.set("Select Any Category")
subcategory_menu = tk.StringVar()
subcategory_menu.set("Scrape Across Subcategories?")
headless_menu = tk.StringVar()
headless_menu.set("Run Headless?")
number_pages1 = tk.StringVar()
postcode1 = tk.StringVar()

#initialise drop down menus
drop_category = tk.OptionMenu(frame_main_1, category_menu, "fiction", "crime-thrillers-mystery", "science-fiction-fantasy-horror",
"graphic-novels-manga", "non-fiction-books")
drop_category.config(width = 15)
drop_category.config(height = 2)
drop_category.config(bg = "#CDB5CD")
drop_subcategory = tk.OptionMenu(frame_main_1, subcategory_menu, "yes", "no")
drop_subcategory.config(width = 21)
drop_subcategory.config(height = 2)
drop_subcategory.config(bg = "#CDB5CD")
drop_headless = tk.OptionMenu(frame_main_1, headless_menu, "yes", "no")
drop_headless.config(width = 13)
drop_headless.config(height = 2)
drop_headless.config(bg = "#CDB5CD")

number_pages = tk.Label(frame_main_2, text = "NUMBER OF PAGES:",  height = '2', width='15', bg="#CDB5CD", fg="#F5F5F5")
postcode = tk.Label(frame_main_2, text = "POSTCODE:", height = '2', width='15', bg = "#CDB5CD", fg="#F5F5F5")
number_pages_entry = tk.Entry(frame_main_2, textvariable = number_pages1, width = 3, bd=2)
postcode_entry = tk.Entry(frame_main_2, textvariable = postcode1, width = 8, bd =2)
#call pre-defined functions on postcode input
postcode_entry.bind("<KeyRelease>", caps_postcode)
postcode_entry.bind("<Leave>", check_postcode)

#arrange middle frame inputs
frame_main_1.pack(fill = 'x', pady = 5)
frame_main_2.pack(fill = 'x', pady = 2)
drop_category.pack(side = "left")
drop_subcategory.pack(side = "left", padx=5)
drop_headless.pack(side = "right")
number_pages.pack(side = "left")
number_pages_entry.pack(side = "left", expand = "True", fill = "x")
postcode.pack(side = "left")
postcode_entry.pack(side = "left", expand = "True", fill = 'x')

#bottom frame initialisation
button_run = tk.Button(bottom_frame, text = "Start", command = run_app, fg = "#548B54",
relief = "raised", width = 15, height = 2, font = ("Helvetica 15 bold"))
button_run.grid(column = 0, row = 0, sticky = 'w', padx = 65, pady = 2)
button_close = tk.Button(bottom_frame, text = "Exit", command = close_app, fg = "#CD5B45",
relief = "raised", width = 15, height = 2, font = ("Helvetica 15 bold"))
button_close.grid(column = 1, row = 0, sticky = 'e', padx = 65, pady = 2)

#run Tkinter event loop
window.mainloop()