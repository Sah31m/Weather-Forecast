import tkinter as Tk
import math
import threading
import time
import requests
import pytz

from PIL import Image, ImageTk
from tkinter import ttk,messagebox,PhotoImage
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
from Countries import Countries as Countries
from io import BytesIO
from datetime import datetime, timedelta


API_Key = "4803dccc4166c3e6c1127c6732e44a01"


 
def GetCountryCentre(Country):

    Geocator = Nominatim(user_agent = "country_center_locator")
    Location = Geocator.geocode(Country,exactly_one = True)
 
    Lat = Location.latitude if Location else 0
    Lon = Location.longitude if Location else 0

    return Lat,Lon


def GetDayNames(Country):

    TimeZone = pytz.timezone(Country)
    Today = datetime.now(TimeZone)
    Tomorrow = Today + timedelta(days = 1)
    DayNames = []

    for _ in range(5):

        DayNames.append(Tomorrow.strftime("%A"))
        Tomorrow += timedelta(days = 1)
    
    DayNames[0] = "Tomorrow"
    
    return DayNames




class Main():
    
    # Attributes
    CellObjects = {}

    #Initialize
    def __init__(self):
        
        WinX,WinY = 900,500

        #Window
        Root = Tk.Tk()
        Root.title("Weather Forecast")
        RootIcon = PhotoImage(file="C:\\Users\\draco\\Documents\\GitHub\\Portfolio\\WeatherForecaster\\Images\\weather-icon-png-11063.png")
        Root.iconphoto(False,RootIcon)
        Root.geometry(f"{WinX}x{WinY}+300+200")
        Root.resizable(0,0)
        Root.wm_attributes('-transparentcolor', '#ab23ff')

        #Background Image
        Img = Image.open("C:\\Users\\draco\\Documents\\GitHub\\Portfolio\\WeatherForecaster\\Images\\Background.jpg")
        Background = Img.resize((1920,1200))
        BackgroundImg = ImageTk.PhotoImage(Background)

        #Canvas
        Canvas = Tk.Canvas(Root,bg = "blue")
        Canvas.create_image(0,0,anchor = "nw",image = BackgroundImg)
        Canvas.place(relx = .5,rely = .5,anchor = "center",relwidth=1,relheight=1)

        #Backgrounds
        Img = Image.open("C:\\Users\\draco\\Documents\\GitHub\\Portfolio\\WeatherForecaster\\Images\\BlueRectangle.png")
        Img = Img.resize((500,90))
        BlueBG = ImageTk.PhotoImage(Img) 
        Canvas.create_image(450,50,anchor = "center",image = BlueBG)
        Img2 = Image.open("C:\\Users\\draco\\Documents\\GitHub\\Portfolio\\WeatherForecaster\\Images\\BlueRectangle.png")
        Img2 = Img2.resize((850,100))
        BlueBG2 = ImageTk.PhotoImage(Img2) 
        Canvas.create_image(450,250,anchor = "center",image = BlueBG2)
        Canvas.create_rectangle(
            0,
            300,  
            900,
            500,
            fill="gray8"
        )
         
        #Labels
        Canvas.create_text(450,35,anchor = "center",text = "Select Location",font='Helvetica 18 bold',fill = "white")  
        Canvas.create_text(150,235,anchor = "center",text = "WINDS",font='Helvetica 16 bold',fill = "white")
        Canvas.create_text(350,235,anchor = "center",text = "HUMIDITY",font='Helvetica 16 bold',fill = "white")
        Canvas.create_text(550,235,anchor = "center",text = "DESCRIPTION",font='Helvetica 16 bold',fill = "white")
        Canvas.create_text(750,235,anchor = "center",text = "PRESSURE",font='Helvetica 16 bold',fill = "white")
        self.Clock = Canvas.create_text(450,107,anchor = "center",text = "00:00:00",font='Helvetica 32 bold',fill = "white")

        #Cells
        canvas_width = Canvas.winfo_width()

        CurrentContainer = {}
        CurrentContainer["wind_speed"] = Canvas.create_text(150,265,anchor = "center",text = "...",font='Helvetica 12 bold',fill = "dark blue")
        CurrentContainer["humidity"] = Canvas.create_text(350,265,anchor = "center",text = "...",font='Helvetica 12 bold',fill = "dark blue")
        CurrentContainer["description"] = Canvas.create_text(550,265,anchor = "center",text = "...",font='Helvetica 12 bold',fill = "dark blue")
        CurrentContainer["pressure"] = Canvas.create_text(750,265,anchor = "center",text = "...",font='Helvetica 12 bold',fill = "dark blue")
        CurrentContainer["temp"] = Canvas.create_text(450,200,anchor = "center",text = "00:00:00",font='Helvetica 12 bold',fill = "white")
        CurrentContainer["icon"] = Canvas.create_image(450,155,anchor = "center")
 
        self.CellObjects["current"] = CurrentContainer

        for i in range(5):

            Container = {}
            Size = 240 if (i == 0) else 145
            Offset = 150 if (i == 0) else 200
            X, Y = (Offset + 150 * i), 480
            rect_left = (X - Size / 2) * canvas_width
            rect_right = (X + Size / 2) * canvas_width
            Canvas.create_rectangle(
                rect_left,
                315,
                rect_right,
                Y,
                fill="#282829"
            )
            
            TColour = "light blue" if (i == 0) else "white"

            Container["Title"] = Canvas.create_text(X, 325, font='Helvetica 12 bold', text="Test", fill=TColour, anchor="center")
            Container["day"] = Canvas.create_text(X,425,anchor = "center",text = "DAY",font='Helvetica 8 bold',fill = TColour)
            Container["night"] = Canvas.create_text(X,450,anchor = "center",text = "NIGHT",font='Helvetica 8 bold',fill = TColour)
             
            Container["icon"] = Canvas.create_image(X,375,anchor = "center")
            self.CellObjects[str(i)] = Container
 
        Variable = Tk.StringVar(Root)
        Variable.set(Countries[0])
        ComboBox = ttk.Combobox(Canvas,textvariable=Variable, values = Countries)
        ComboBox.bind('<<ComboboxSelected>>', self.OnSelection)
        ComboBox.place(x= 450,y = 65,anchor="center",width=200,height=20)
        ComboBox.focus()

        self.Root = Root
        self.Canvas = Canvas
        self.ComboBox = ComboBox
        self.OnSelection(self)
        threading.Thread(target = self.UpdateClock,args=(False,)).start()
        Root.mainloop()

        return

    
    def UpdateClock(self,Break):

        while True :
            
            Home = pytz.timezone(self.Country)
            Time = datetime.now(Home)
            CurrentTime = Time.strftime("%I:%M %p")
            self.Canvas.itemconfig(self.Clock,text=CurrentTime)

            if Break == True:
 
                break

            else:

                time.sleep(1)

        return


    ##// Setters \\--##
    def SetWeather(self):

        Data = self.GetWeather()
        DayNames = GetDayNames(self.Country)
 
        for CellName,Container in self.CellObjects.items():
 
            WeatherIndex = Data["current"] if CellName == "current" else Data["daily"][int(CellName)]

            for Key,Value in WeatherIndex.items():

                Key = str.lower(Key)
                
                if (Key in Container):

                    Target = Container[Key] 
                    self.Canvas.itemconfig(Target,text = (str(math.floor(Value))+"°") if Key == "temp" else Value)

                elif Key == "weather":
                    IconID = (Value[0]["icon"])
                    IconURL = f"http://openweathermap.org/img/wn/{IconID}.png"
                    Promise = requests.get(IconURL)
                    Content = Promise.content

                    Img = Image.open(BytesIO(Content))
                    Img = Img.resize((100,100))
                    Tk_Image = ImageTk.PhotoImage(Img)
                    Container["TKImage"] = Tk_Image

                    if CellName == "current":

                        self.Canvas.itemconfig(Container["description"],text = WeatherIndex["weather"][0]["description"])
                        
                    self.Canvas.itemconfig(Container["icon"],image = Container["TKImage"])

                elif Key == "temp" and (("day" in Container) or ("night" in Container)):
                    DayT,NightT = str(math.floor(Value["day"])),str(math.floor(Value["night"]))
                    self.Canvas.itemconfig(Container["day"],text = "DAY : "+DayT+"°")
                    self.Canvas.itemconfig(Container["night"],text = "Night : "+NightT+"°")

            if CellName != "current":

                self.Canvas.itemconfig(Container["Title"],text = DayNames[int(CellName)])
        
        return
    
    def SetCountry(self):

        Geocator = Nominatim(user_agent = "geoapiExercises")
        Location = Geocator.geocode(self.GetCountry())
        Obj = TimezoneFinder()
        self.Country = Obj.timezone_at(lng = Location.longitude,lat = Location.latitude)
        self.UpdateClock(True)

        return
    
    
    ##// Getters \\--##
    def GetCountry(self):

        return self.ComboBox.get()
    
    def GetWeather(self):

        Lat,Long = GetCountryCentre(self.Country)
        URL = f'https://api.openweathermap.org/data/3.0/onecall?lat={Lat}&lon={Long}&exclude=hourly&appid={API_Key}'
        Params = {
            "units" : "metric"
        }
        Promise = requests.get(URL,Params)

        if Promise.status_code == 200:

            Data = Promise.json()
 
            return Data
        
        else:

            messagebox.ERROR("Failed","Unfortunately there was")

        return
    

    ##// Events \\--##
    def OnSelection(self,Event):

        self.SetCountry()
        self.SetWeather()

        return
    

   

 



Root = Main()
