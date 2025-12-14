import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation
from matplotlib.widgets import Button
from matplotlib.widgets import CheckButtons
import sys
from subprocess import call
import math

class MyAnim:

    def __init__(self, df, color):
        self.x_data = df.x_data_formatted
        self.y_data = df.y_data_formatted
        self.name = df.name
        self.color = color
        self.annotation = ax2.annotate("", xy = (0,0), xycoords = "data")
        self.lines = []
        self.current_segment, self.segment_start = 0, 0
        self.boundary_reached = False
        self.order = tickers.index(self.name + ":")
        self.create_line()

    def scale_data(self):
        self.divisor = max(self.y_data)
        self.y_data_scaled = list(map(lambda x: x/self.divisor, self.y_data))


    def update_anim(self, k):
        self.lines[self.current_segment].set_data(self.x_data[self.segment_start:k], self.y_data[self.segment_start:k])
        try:
            self.annotation.set_position((self.x_data[k], self.y_data[k]))
            self.annotation.xy = (self.x_data[k], self.y_data[k])
        except:
            pass
        return_value = self.lines + [self.annotation]
        return return_value

    def create_line(self):
        self.lines.extend(ax2.plot([], [], lw = 1.5, color = self.color, markevery=100))

class AllAnims:

    def __init__(self, anims, colors):
        self.animations = anims
        self.colors = colors
        self.annotations = []
        self.create_annotations()

    def create_annotations(self):
        for i in range(len(self.animations)):
            y_position = 1.0047 - 0.0330*i
            self.annotations.append(ax2.annotate("", xy = (legend.get_window_extent().x1 *1.01, legend.get_window_extent().y1*y_position-21), xycoords = "figure pixels", color = self.colors[i]))
        
    def update_all(self, k):
        self.artists = []
        for animation in self.animations:
            self.artists.extend(animation.update_anim(k))
            index = self.animations.index(animation)
            self.annotations[index].set_text(str(int(round(animation.y_data[k], 0))) + "%")
        return self.artists + self.annotations
        
    def start_anims(self, event):
        global ani, speed
        speed = model(len(self.animations[0].x_data))
        ani = animation.FuncAnimation(fig=fig1, func=self.update_all, frames = range(0, len(self.animations[0].x_data), speed), interval = 1, blit = True, repeat = False)
        for anim in self.animations:
            anim.annotation = ax2.annotate(anim.name, xy = (0,0), xycoords = "data", color = anim.color)

class DataFrame:
    def __init__(self, index):
        try:
            self.df = pd.read_csv("Data/" + index + ".csv", sep=r'\s*,\s*', engine = "python")
        except FileNotFoundError:
            print("File not found.")

        self.name = index
        self.df.set_index("Date", inplace = True)
        self.df.sort_values(by=["Date"], axis = "index", inplace = True)
        self.x_data_unformatted = pd.to_datetime(self.df.index, format="mixed")
        self.y_data_unformatted = self.df["Close"].to_numpy()
        self.unformatted_data = dict(zip(self.x_data_unformatted, self.y_data_unformatted))
        self.x_data_formatted = []
        self.y_data_formatted = []

    def convert_to_percentage(self):
        self.y_data_formatted = [round((((value-self.y_data_formatted[0])/self.y_data_formatted[0])*100),3) for value in self.y_data_formatted]


def model(x):
    return int(round(0.135009773 * math.sqrt(x) - 9.390803448, 0))

    
def choose_comparison_callback(event):
    plt.close(fig1)

def choose_comparison():
    global fig1, indexes
    fig1 = plt.figure(figsize = (6,4))
    fig1.suptitle("Please select tickers to plot", fontsize = 16, x=0.66, y=0.90, fontweight = "bold")
    ax_confirm = fig1.add_axes([0.52, 0.425, 0.25, 0.15])
    ax_check = fig1.add_axes([0.1,0.0225,0.4, 0.95])
    ax_check.set_axis_off()
    tickers = ["SPX", "IXIC", "SX5E", "UKX", "DAX", "CAC", "BUX", "N225", "HSI", "SSEC", "BSESN", "KOSPI", "XAO", "IBOV", "J203"]
    bcheck = CheckButtons(ax = ax_check, labels = tickers, label_props={"fontsize": [18]}, check_props={"facecolor":"red"})
    bconfirm = Button(ax_confirm, "Confirm", color = "green", hovercolor="palegreen")
    for label in bcheck.labels:
        label.set_fontsize(12)
    bconfirm.on_clicked(choose_comparison_callback)
    plt.show()
    indexes = bcheck.get_checked_labels()
    title = get_title(indexes)
    to_animate, colors = graph_setup(title, indexes)

    return to_animate, colors

def get_title(title):
    title = ""
    for i in range(len(indexes)):
        if len(indexes) != 1:
            if i > 0 and i < len(indexes):
                title += " vs " + indexes[i]
            else:
                title += indexes[i]
        else:
            title = indexes[0]
    return title

def format_data(dataframes_list):
    dates, intersection = [], []
    for dataframe in dataframes_list:
        dates.append(set(dataframe.x_data_unformatted))

    try:
        intersection = sorted(set.intersection(*dates))
    except:
        sys.exit()
 
    for dataframe in dataframes_list:
        shared_dates = sorted(list(dataframe.unformatted_data.keys() & intersection))
        dataframe.x_data_formatted.extend(shared_dates)
        dataframe.y_data_formatted.extend(dataframe.unformatted_data[key] for key in dataframe.x_data_formatted)

    return dataframes_list

def get_limits(indexes):
    dataframes_list = []
    for index in indexes:
        dataframes_list.append(DataFrame(index))

    dataframes_list = format_data(dataframes_list)

    for df in dataframes_list:
        df.convert_to_percentage()

    x_lowest, x_highest = dataframes_list[0].x_data_formatted[0], dataframes_list[0].x_data_formatted[-1]
    y_lowest, y_highest = dataframes_list[0].y_data_formatted[0], dataframes_list[0].y_data_formatted[-1]
    
    for dataframe in dataframes_list:
        if min(dataframe.x_data_formatted) < x_lowest:
            x_lowest = min(dataframe.x_data_formatted)
        if min(dataframe.y_data_formatted) < y_lowest:
            y_lowest = min(dataframe.y_data_formatted)
        if max(dataframe.x_data_formatted) > x_highest:
            x_highest = max(dataframe.x_data_formatted)
        if max(dataframe.y_data_formatted) > y_highest:
            y_highest = max(dataframe.y_data_formatted)

    return x_lowest, x_highest, y_lowest, y_highest, dataframes_list

def graph_setup(title, indexes):
    mpl.style.use(["ggplot", "fast"])
    global fig2, ax2, legend, tickers
    fig2 = plt.figure(figsize=(15,8))
    ax2 = fig2.add_axes([0.1,0.08,0.85,0.75])
    ax2.set_title(title, fontdict = {})
    x_lowest, x_highest, y_lowest, y_highest, dataframes_list = get_limits(indexes)
    ax2.set_xlim(x_lowest, x_highest)
    if round(y_lowest - (abs(y_lowest) * 20)) < -100:
        ax2.set_ylim(-100, round(y_highest + (abs(y_highest)) * 0.2))
    else:
        ax2.set_ylim(round(y_lowest - (abs(y_lowest) * 20)), round(y_highest + (abs(y_highest)) * 0.2))
    ax2.set_ylabel("Percentage change")
    ax2.set_xlabel("Year")
    vals = ax2.get_yticks()
    labels = [(format(element, ",")[:-2] + "%") for element in vals]
    ax2.set_yticks(vals[1:])
    ax2.set_yticklabels(labels[1:])
    colors = []
    for i in range(len(indexes)):
        p = ax2.plot([],[])
        colors.append(p[-1].get_color())

    indexes = [element + ":" for element in indexes]
    legend = fig2.legend(indexes, loc = 9, bbox_to_anchor = (0.525,0.8))
    text_objects = legend.get_texts()[0:]
    tickers = [element.get_text() for element in text_objects]
    return dataframes_list, colors

def resume_pause_animation(event):
    global trigger
    if trigger % 2 == 0:
        ani.pause()
    else:
        ani.resume()
    trigger += 1

def reset_animation(event):
    plt.close()
    call(["python", "IndexAnimation.py"])
    sys.exit()

def start_animations(event):
    au.start_anims(event)
    bstart.disconnect(cid)
    global cid2
    cid2 = bstart.on_clicked(resume_pause_animation)

def button_init():
    global bstart, breset
    ax_start = fig2.add_axes([0.4755,0.89,0.1,0.075])
    ax_reset = fig2.add_axes([0.6,0.89,0.1,0.075])
    bstart = Button(ax_start, "Start / Stop", color = "red", hovercolor="grey")
    breset = Button(ax_reset, "Reset", color = "lightskyblue", hovercolor="grey")

def main():
    global cid, au, trigger
    to_animate, colors = choose_comparison()
    au = AllAnims(to_animate, colors)
    for index, anim in enumerate(to_animate):
        to_animate[index] = MyAnim(anim, colors[index])
    button_init()
    cid = bstart.on_clicked(start_animations)
    trigger = 2
    cid_r = breset.on_clicked(reset_animation)
    plt.show()
main()
