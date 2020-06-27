from matplotlib import dates
from matplotlib import pyplot as plt
from PIL import Image
import pytz


def plot_time_data(x, y):
    plt.figure(figsize=(2, 1.5), dpi=125)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0.15)
    plt.fill_between(x, 0, y, color="black")

    axes = plt.gca()
    axes.axes.get_yaxis().set_visible(False)
    axes.set_frame_on(False)
    hfmt = dates.DateFormatter("%H:%M", tz=pytz.timezone("Europe/London"))
    axes.set_ylim([0, 10])
    axes.set_xticks(axes.get_xticks()[::2])
    axes.xaxis.set_major_formatter(hfmt)
    # plt.show()
    plt.savefig("myfig.png", transparent=True)
    img = Image.open("myfig.png")
    return img
