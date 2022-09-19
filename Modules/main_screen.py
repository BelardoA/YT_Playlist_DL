import tkinter
from tkinter import messagebox, filedialog
from os.path import exists
from Modules.threads import start_threads
from Modules.functions import get_channel, get_vid_count, clean_dir

window = tkinter.Tk()
window.title("Playlist Downloader")
window.geometry('600x350')
window.configure(bg='#333333')
window.resizable(False, False)
var = tkinter.StringVar()
path_check_pass = tkinter.StringVar()
path_check_fail = tkinter.StringVar()
path_check_fail.set("❌")


def browseFiles():
    """
    function to update the filepath status
    """
    global file_path
    file_path = filedialog.askdirectory(
        initialdir="/",
        title="Select a Folder")
    # Change label contents
    var.set(file_path)
    if exists(file_path) is True:
        path_check_pass.set("✔️")
        path_check_fail.set("")
    else:
        path_check_pass.set("")
        path_check_fail.set("❌")


def start_dl():
    """
    start the process of downloading the playlist
    """
    pl_link = pl_link_input.get()
    output_dir = file_path_input.get()
    if pl_link != '' and output_dir != '':
        get_channel(
            pl_link=pl_link)
        threads = get_vid_count(
            pl_link=pl_link)
        start_threads(
            thread_cnt=threads,
            pl_link=pl_link,
            file_path=output_dir
        )
        clean_dir()
        messagebox.showinfo(
            title="Mission Complete!",
            message="Playlist has been downloaded. {} tracks".format(
                threads
            ) + ' have been downloaded.')
    else:
        messagebox.showerror(
            title="Information Missing!",
            message="Please verify the necessary information"
            + " has been provided."
        )


def quit_app():
    """
    function to terminate the window and
    terminate the program
    """
    window.destroy()
    exit()


def close_window():
    """
    function to close the window and
    proceed to the next part of the main script
    """
    window.destroy()


def start_window():
    """
    function to start the program window
    """
    frame = tkinter.Frame(bg='#333333')
    global file_path_input
    global pl_link_input
    header_label = tkinter.Label(
        frame,
        text="YouTube Playlist Downloader",
        bg="#333333",
        fg="#FF5F15",
        font=("Arial", 30)
    )
    pl_link_label = tkinter.Label(
        frame,
        text="Playlist Link:",
        bg="#333333",
        fg="#FFFFFF",
        font=("Arial", 16)
    )
    pl_link_input = tkinter.Entry(
        frame,
        font=("Arial", 16)
    )
    path_pass = tkinter.Label(
        frame,
        textvariable=path_check_pass,
        font=("Airal", 16),
        bg="#333333",
        fg="#00FF3A"
    )
    path_fail = tkinter.Label(
        frame,
        textvariable=path_check_fail,
        font=("Airal", 16),
        bg="#333333",
        fg="#FF0000"
    )
    file_path_input = tkinter.Entry(
        frame,
        textvariable=var,
        font=("Airal", 16),
        state="disabled"
    )
    button_explore = tkinter.Button(
        frame,
        text="Save Location",
        command=browseFiles)
    submit_btn = tkinter.Button(
        frame,
        text="Start",
        bg="#FF5F15",
        fg="#FFFFFF",
        font=("Arial", 16),
        command=start_dl
    )
    cancel_btn = tkinter.Button(
        frame,
        text="Quit",
        bg="#FF0000",
        fg="#FFFFFF",
        font=("Arial", 16),
        command=quit_app
    )
    header_label.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="news",
        pady=20,
        padx=20
    )
    button_explore.grid(
        row=1,
        column=0
    )
    file_path_input.grid(
        row=1,
        column=1,
        pady=20,
        padx=20
    )
    path_pass.grid(
        row=1,
        column=2,
        padx=10
    )
    path_fail.grid(
        row=1,
        column=2
    )
    pl_link_label.grid(
        row=2,
        column=0,
        padx=20
    )
    pl_link_input.grid(
        row=2,
        column=1,
        pady=20
    )
    submit_btn.grid(
        row=3,
        column=0,
        padx=40
    )
    cancel_btn.grid(
        row=3,
        column=1,
        columnspan=2,
        pady=30
    )
    frame.pack()

    window.mainloop()
