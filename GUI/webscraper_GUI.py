import os
import tkinter as tk
import requests
from tkinter import font as tkfont
from tkinter import messagebox
from PIL import ImageTk, Image
from Scraper_Runner_GUI import Run_Scraper
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

os.environ["GH_TOKEN"] = "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"
base_folder = os.path.dirname(__file__)
image_path = os.path.join(base_folder, 'book.png')
gif_path = os.path.join(base_folder, 'book.gif')
song_path = os.path.join(base_folder, "Harry-Potter-Theme-Song.wav")

class MainFrame(tk.Tk):

    """Frame object/Controller holding all of our different pages"""

    def __init__(self, *args, **kwargs):

        """See help(MainFrame) for more details"""

        tk.Tk.__init__(self, *args, **kwargs)
        self.titlefont = tkfont.Font(family = 'Helvetica', size = 18, weight = 'bold', slant = 'roman')
        self.title('Book Scraper')
        self.geometry('910x435')
      
        # frame object that will hold all the pages 
        container = tk.Frame(self)
        container.pack(side = "top", fill = "both")
        container.grid_rowconfigure(0, weight = 1)
        container.columnconfigure (0, weight = 1)

        # create empty dictionary to define all pages
        self.listing = {}
        # These pages are built later on as classes
        for page in (WelcomePage, PageOne, PageTwo):
            page_name = page.__name__
            # new frame object for each page
            frame = page(parent = container, controller = self)
            # same as main frame - completely layered without distinction
            frame.grid(row = 0, column = 0, sticky = 'nesw')
            self.listing[page_name] = frame

        self.play_sound()
        self.up_frame('WelcomePage')
        
    def play_sound(self):
        self.sound = SoundLoader.load(song_path)
        if self.sound:
           self.sound.play()
          
        
    # define first page to pop up
    def up_frame(self, page_name):
        page = self.listing[page_name]
        page.tkraise()


class WelcomePage(tk.Frame):

    """Frame object corresponding to the first/welcome page of the GUI"""

    def __init__(self, parent, controller):

        """See help(WelcomePage) for more details"""

        tk.Frame.__init__(self, parent)
        self.controller = controller

        # set image as background of frame     
        self.background_image = ImageTk.PhotoImage(file=image_path)
        self.background_label = tk.Label(self, image = self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_label.image = self.background_image

        # add label
        label = tk.Label(self, text = 'Waterstones Web Scraping Tool', font = controller.titlefont)
        label.pack(pady = 100)
        # add Get Started button
        button = tk.Button(self, text = 'Get Started', command = lambda: controller.up_frame("PageOne"))
        button.pack(pady = 75)


class PageOne(tk.Frame):
    
    """Frame object corresponding to page one of the GUI"""

    def __init__(self, parent, controller):

        """See help(PageOne) for more details"""

        tk.Frame.__init__(self, parent, bg = "#27408B")
        self.controller = controller

        #header label
        header = tk.Label(self, text = "A reader lives a thousand lives before he dies.", 
        bg="#27408B", fg="#FFF5EE", height = '5', width='54',font=("Helvetica 18 italic bold"))
        header.grid(row=0, column=0)

        # adds the drop down menus
        drop_down_menus = self.initialise_menus()
        drop_down_menus[0].grid(row=1, column=0, sticky='W', pady=30)
        drop_down_menus[1].grid(row=1, column=0, pady=30)
        drop_down_menus[2].grid(row=1, column=0, sticky='E', pady=30, padx=20)
        # adds the user entry variables
        self.intialises_user_entries()
        number_pages = tk.Label(self, text = "NUMBER OF PAGES:",  height = '5', width='17', bg="#27408B", fg="#F5F5F5")
        number_pages.grid(column=0, row=2, sticky='W', padx = 50, pady = 2)
        self.number_pages_entry.grid(column=0, row=2,  sticky='W', padx = 200, pady = 5)
        postcode = tk.Label(self, text = "POSTCODE:", height = '5', width='15', bg = "#27408B", fg="#F5F5F5")
        postcode.grid(row=2, column=0, sticky='E', padx = 150, pady = 5)
        self.postcode_entry.grid(row =2, column=0, sticky='E', padx = 60, pady = 5)

        # Start button will start the scraper & once run will navigate to final page
        start_button = tk.Button(self, text = "Start", command = lambda: [self.run_app(), controller.up_frame("PageTwo")], fg = "#548B54",
        relief = "raised", width = 12, height = 3, font = ("Helvetica 12 bold"))
        start_button.grid(column = 0, row = 3, sticky = 'e',padx = 65, pady = 2)
        # Back button to return to welcome page
        back_button = tk.Button(self, text = "Back", command = lambda: controller.up_frame("WelcomePage"), fg = "#CD5B45",
        relief = "raised", width = 12, height = 3, font = ("Helvetica 12 bold"))
        back_button.grid(column = 0, row = 3, sticky = 'w', padx = 65, pady = 2)


    def user_input(self):

        """This methods allows to easily monitor changes of tinker variables"""

        self.category_menu = tk.StringVar()
        self.category_menu.set("Select Any Category")
        self.subcategory_menu = tk.StringVar()
        self.subcategory_menu.set("Scrape Across Subcategories?")
        self.headless_menu = tk.StringVar()
        self.headless_menu.set("Run Headless?")
        self.number_pages = tk.StringVar()
        self.postcode = tk.StringVar()


    def initialise_menus(self):

        """This methods initialises the options of the drop-down menus"""
        
        self.user_input()
        drop_category = tk.OptionMenu(self, self.category_menu, "fiction", "crime-thrillers-mystery", "science-fiction-fantasy-horror","graphic-novels-manga", "non-fiction-books")
        drop_category.config(width = 15)
        drop_category.config(height = 2)
        drop_category.config(bg = "#27408B")
        drop_subcategory = tk.OptionMenu(self, self.subcategory_menu, "yes", "no")
        drop_subcategory.config(width = 23)
        drop_subcategory.config(height = 2)
        drop_subcategory.config(bg = "#27408B")
        drop_headless = tk.OptionMenu(self, self.headless_menu, "yes", "no")
        drop_headless.config(width = 13)
        drop_headless.config(height = 2)
        drop_headless.config(bg = "#27408B")

        return drop_category, drop_subcategory, drop_headless


    def intialises_user_entries(self):

        """This method initialises user entries &
        applies pre-defined functions on them"""

        self.number_pages_entry = tk.Entry(self, textvariable = self.number_pages, width = 5, bd=2)
        self.postcode_entry = tk.Entry(self, textvariable = self.postcode, width = 8, bd =2)
        #call functions on postcode input
        self.postcode_entry.bind("<KeyRelease>", self.caps_postcode)
        self.postcode_entry.bind("<Leave>", self.check_postcode)
        

    def caps_postcode(self, event):

        """ This function capitalises every letter in the postcode entry"""

        self.postcode.set(self.postcode.get().upper())


    def check_postcode(self, event):

        """ This function will check postcode input corresponds to a 
        real postcode, otherwise it will raise a pop up message."""

        postcode_check = self.postcode.get()
        postcode_status = requests.get('https://api.postcodes.io/postcodes/' + postcode_check).json()["status"]
        if postcode_status == 404:
            #self.postcodepostcode.set(requests.get('https://api.postcodes.io/random/postcodes').json()["result"]["postcode"])
            messagebox.showinfo("Error Message", "Not a valid UK postcode, try again!")


    def run_app(self):

        """ This function takes the user input from the user interface and
        feeds it to the Run_Scraper class for initilisation of an instance"""

        user_number_pages = int(self.number_pages_entry.get())
        user_postcode = str(self.postcode_entry.get())
        user_category = str(self.category_menu.get())
        user_subcategory = str(self.subcategory_menu.get())
        user_headless = str(self.headless_menu.get())
   
        waterstones = Run_Scraper(user_category, user_subcategory, user_headless)
        if waterstones.subcategory_flag == "no":
            waterstones.scrape_individual_subcategories(user_number_pages, user_postcode)
        # if you want to remove duplicates book list
        elif waterstones.subcategory_flag == "yes":
            waterstones.scrape_across_subcategories(user_number_pages, user_postcode)
            
        
class PageTwo(tk.Frame):

    """Frame object corresponding to page two of the GUI"""

    def __init__(self, parent, controller):

        """See help(PageOne) for more details"""

        tk.Frame.__init__(self, parent, bg = "#27408B")
        self.controller = controller
        
        # opens every image frame in the gif
        info = Image.open(gif_path)
        self.frames = info.n_frames
        self.im = [tk.PhotoImage(file = gif_path, format=f"gif -index {i}") for i in range(self.frames)]
        count = 0
        anim = None
        
        # sets background of the tkinter frame
        self.background_label = tk.Label(self,image="")
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_label.image = self.im
        # loops through each image frame
        self.animation(count)

        # display message
        label = tk.Label(self, text = 'Everything went well!', font = controller.titlefont)
        label.pack(pady = 50)
        # Exit button to quit the GUI    
        exit_button = tk.Button(self, text = 'Exit', command = lambda: controller.destroy())
        exit_button.pack(pady = 125)


    def animation(self, count):

        """This function will set each of the image frames as the
        frame background one by one 50ms apart"""

        global anim
        im2 = self.im[count]
        self.background_label.configure(image=im2)
        count += 1
        # when it reaches the end - starts again from beggining
        if count == self.frames:
            count = 0
        anim = self.after(50,lambda :self.animation(count))


if __name__ == '__main__':
    app = MainFrame()  
    app.mainloop()
   